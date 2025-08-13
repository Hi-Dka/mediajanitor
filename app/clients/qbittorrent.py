import os
from typing import Any, Dict

from app.clients.once_api_client import CTryOnceLoginApiClient
from app.common.constants import HTTP_OK
from app.common.endpoints import (
    QBITTORRENT_FILE_PRIORITY,
    QBITTORRENT_LOGIN,
    QBITTORRENT_TORRENTS_DELETE,
    QBITTORRENT_TORRENTS_FILES,
    QBITTORRENT_TORRENTS_INFO,
)
from app.common.logger import logger


class CQbittorrentClient(CTryOnceLoginApiClient):
    """qBittorrent API Client"""

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url)
        self.user = user
        self.password = password
        self.cache: Dict[str, Any] = {}  # 缓存种子文件信息
        self.login()
        self.refresh_all_torrents_info()

    def login(self) -> bool:
        payload = {"username": self.user, "password": self.password}
        response = self.session.post(
            self.base_url + QBITTORRENT_LOGIN, data=payload, timeout=10
        )

        if response.status_code == HTTP_OK and response.text == "Ok.":
            logger.info("[qbittorrent] Successfully logged in to qBittorrent")
            return True

        logger.error(
            "[qbittorrent] Failed to login to qBittorrent, please check username and password"
        )
        return False

    def refresh_all_torrents_info(self):
        """全量刷新所有种子及文件信息"""
        try:
            torrents: list[Dict[str, Any]] = self.get(
                QBITTORRENT_TORRENTS_INFO
            ).json()
        except ValueError as e:
            logger.error(
                "[qbittorrent] Failed to parse torrents info JSON: %s", e
            )
            return
        new_cache = {}
        for t in torrents:
            category = t.get("category", "")
            if category == "刷流":
                continue

            torrent_hash = t.get("hash")
            files = self.get(
                QBITTORRENT_TORRENTS_FILES, params={"hash": torrent_hash}
            ).json()
            new_cache[torrent_hash] = [
                {
                    "id": file_id,
                    "name": file_info["name"],
                    "priority": file_info["priority"],
                }
                for file_id, file_info in enumerate(files)
            ]
        logger.info("[qbittorrent] Successfully refreshed all torrents info")
        self.cache = new_cache

    def choose_to_delete(self, torrent_hash: str) -> bool:
        """Delete torrent and its files"""
        video_exts = {".mp4", ".mkv", ".avi"}

        files = self.cache.get(torrent_hash, [])
        for file in files:
            filename = os.path.basename(file["name"])
            if any(filename.endswith(ext) for ext in video_exts):
                if file["priority"] != 0:
                    logger.warning(
                        "[qbittorrent] File %s in torrent %s has non-zero priority, cannot delete",
                        filename,
                        torrent_hash,
                    )
                    return False
        logger.info(
            "[qbittorrent] All files in torrent %s have zero priority, proceeding to delete",
            torrent_hash,
        )
        self.post(
            QBITTORRENT_TORRENTS_DELETE,
            data={"hashes": torrent_hash, "deleteFiles": "true"},
        )
        return True

    def set_file_priority(
        self, torrent_hash: str, file_id: int, priority: int = 0
    ):
        """Set file priority"""
        data = {
            "hash": torrent_hash,
            "id": str(file_id),
            "priority": str(priority),
        }
        logger.info(
            "[qbittorrent] Setting file priority for torrent %s, file %d to %d",
            torrent_hash,
            file_id,
            priority,
        )
        self.post(QBITTORRENT_FILE_PRIORITY, data=data)

    def find_hash_and_id_by_file_name(self, filename: str):
        """Find torrent hash and file ID by file name"""

        def search(files: Dict[str, Any], filename: str):
            for torrent_hash, file_list in files.items():
                for file_info in file_list:
                    if os.path.basename(file_info["name"]) == filename:
                        logger.info(
                            "[qbittorrent] Found file %s in torrent %s with ID %d",
                            filename,
                            torrent_hash,
                            file_info["id"],
                        )
                        return torrent_hash, file_info["id"]
            return None, None

        result = search(self.cache, filename)
        if result != (None, None):
            return result

        self.refresh_all_torrents_info()
        return search(self.cache, filename)

    def delete_torrents(self, filename: str):
        """Delete torrents"""
        torrent_hash, file_id = self.find_hash_and_id_by_file_name(filename)
        if torrent_hash is None or file_id is None:
            logger.error(
                "[qbittorrent] No torrent found for file: %s", filename
            )
            return

        self.set_file_priority(torrent_hash, file_id, 0)

        if not self.choose_to_delete(torrent_hash):
            logger.error(
                "[qbittorrent] User chose not to delete torrent: %s",
                torrent_hash,
            )
            return
