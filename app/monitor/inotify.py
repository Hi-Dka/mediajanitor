import os
import queue
import threading
from typing import Any

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from app.clients.moviepilot import CMoviePilotClient
from app.clients.qbittorrent import CQbittorrentClient
from app.common.config import MP_PASS, MP_URL, MP_USER, QB_PASS, QB_URL, QB_USER
from app.common.logger import logger


class CHandler(FileSystemEventHandler):
    """Watchdog event handler for file system changes"""

    def __init__(self, q: queue.Queue[Any]):
        super().__init__()
        self.q = q

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        logger.info("[WATCH] created: %s", event.src_path)

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        logger.info("[WATCH] modified: %s", event.src_path)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        logger.info("[WATCH] moved: %s -> %s", event.src_path, event.dest_path)

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        if event.is_directory:
            logger.info("[WATCH] directory deleted: %s", event.src_path)
            return

        logger.info("[WATCH] File deleted: %s", event.src_path)
        self.q.put(("delete", event.src_path))


class CInotify:
    """Inotify wrapper for monitoring file system events"""

    def __init__(self, path: list[str]):
        if not path:
            raise ValueError("Path cannot be empty")
        self.inotify_path = path

    def start(self):
        """Start monitoring the inotify paths"""
        logger.info(
            "[WATCH] Starting inotify observer for paths: %s", self.inotify_path
        )
        q: queue.Queue[Any] = queue.Queue()
        handler = CHandler(q)
        observer = Observer()
        moviepilot = CMoviePilotClient(
            base_url=MP_URL, user=MP_USER, password=MP_PASS
        )
        qbittorrent = CQbittorrentClient(
            base_url=QB_URL, user=QB_USER, password=QB_PASS
        )

        for path in self.inotify_path:
            if not os.path.exists(path):
                logger.warning("[WATCH] Path does not exist: %s", path)
                continue
            if not os.path.isdir(path):
                logger.warning("[WATCH] Not a directory: %s", path)
                continue
            logger.info("[WATCH] Adding watch for: %s", path)
            observer.schedule(handler, path, recursive=True)

        threading.Thread(
            target=self.worker, args=(q, moviepilot, qbittorrent), daemon=True
        ).start()
        observer.start()
        logger.info("[WATCH] Observer started")
        return observer

    def worker(
        self,
        q: queue.Queue[Any],
        moviepilot: CMoviePilotClient,
        qbittorrent: CQbittorrentClient,
    ):
        """Worker thread to process events from the queue"""
        logger.info("[WATCH] Worker thread started")
        while True:
            item = q.get()
            if item is None:
                logger.info("[WATCH] Worker thread stopping")
                break
            try:
                kind = item[0]
                if kind == "delete":
                    path = item[1]
                    logger.info("[WATCH] Processing delete: %s", path)

                    filename: str = os.path.basename(path)
                    destname: list[str] = [filename]
                    srcname: list[str] = []
                    moviepilot.delete_transfer_history_by_name(
                        destname, srcname
                    )
                    for src in srcname:
                        qbittorrent.delete_torrents(src)
            except OSError as e:
                logger.error(
                    "[WATCH] OS error processing event %s: %s", item, e
                )
            except ValueError as e:
                logger.warning(
                    "[WATCH] ValueError processing event %s: %s",
                    item,
                    e,
                )
            except TypeError as e:
                logger.warning(
                    "[WATCH] TypeError processing event %s: %s",
                    item,
                    e,
                )
