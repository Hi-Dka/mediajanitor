from typing import Any, Dict, List, Optional

from app.clients.once_api_client import CTryOnceLoginApiClient
from app.common.config import (
    MP_DELETE_DEST,
    MP_DELETE_SRC,
    MP_TRANSFER_COUNT,
    MP_TRANSFER_PAGE,
)
from app.common.constants import HTTP_OK
from app.common.endpoints import MOVIEPILOT_LOGIN, MOVIEPILOT_QUERY_BASE
from app.common.logger import logger


class CMoviePilotClient(CTryOnceLoginApiClient):
    """MoviePilot API Client"""

    def __init__(self, base_url: str, user: str, password: str):
        super().__init__(base_url)
        self.user = user
        self.password = password
        self.login()

    def login(self) -> bool:
        payload = {"username": self.user, "password": self.password}
        response = self.session.post(
            self.base_url + MOVIEPILOT_LOGIN, data=payload, timeout=10
        )
        if response.status_code == HTTP_OK:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {response.json().get('access_token')}"
                }
            )

            logger.info("Successfully logged in to MoviePilot")
            return True

        logger.error("Failed to log in to MoviePilot: %s", response.text)
        return False

    def query_transfer_history(self, title: str) -> Dict[str, Any]:
        """Query transfer history for a specific title"""
        payload: Dict[str, Any] = {
            "page": MP_TRANSFER_PAGE,
            "count": MP_TRANSFER_COUNT,
            "title": title,
        }
        logger.info("Querying transfer history for title: %s", title)
        response = self.get(MOVIEPILOT_QUERY_BASE, params=payload)
        return response.json()

    def extract_id_from_rdict_by_name(
        self, rdict: Dict[str, Any], target_name: str
    ) -> Optional[int]:
        """Extract the ID from the API response"""

        data: Dict[str, Any] = rdict.get("data", {})
        items = data.get("list", [])
        for item in items:
            dest_fileitem = item.get("dest_fileitem", {})
            if dest_fileitem.get("name") == target_name:
                logger.info(
                    "Found matching item for title: %s with ID: %s",
                    target_name,
                    item.get("id"),
                )
                return item.get("id")
        logger.warning("No matching item found for title: %s", target_name)
        return None

    def extract_srcname_from_rdict_by_name(
        self, rdict: Dict[str, Any], target_name: str
    ) -> str:
        """Extract the source name from the API response"""

        data: Dict[str, Any] = rdict.get("data", {})
        items = data.get("list", [])
        for item in items:
            dest_fileitem = item.get("dest_fileitem", {})
            if dest_fileitem.get("name") == target_name:
                src_fileitem = item.get("src_fileitem", {})
                logger.info(
                    "Found matching item for title: %s with source name: %s",
                    target_name,
                    src_fileitem.get("name"),
                )
                return src_fileitem.get("name")

        logger.warning("No matching item found for title: %s", target_name)
        return "None"

    def delete_transfer_history_by_id(self, transfer_id: Optional[int]) -> bool:
        """Delete transfer history by ID"""
        params: Dict[str, Any] = {
            "deletesrc": MP_DELETE_SRC,
            "deletedest": MP_DELETE_DEST,
        }

        body: Dict[str, Any] = {
            "id": transfer_id,
            "status": True,
            "date": "",
        }

        response = self.delete(MOVIEPILOT_QUERY_BASE, params=params, json=body)
        try:
            result: Dict[str, Any] = response.json()
        except ValueError as e:
            logger.error("Failed to parse response JSON: %s", e)
            return False

        if result.get("success") is True:
            logger.info(
                "Successfully deleted transfer history with ID: %s", transfer_id
            )
            return True

        logger.error(
            "Failed to delete transfer history with ID %s", transfer_id
        )
        return False

    def delete_transfer_history_by_name(
        self, destName: List[str], srcName: List[str]
    ):
        """Delete transfer history by title"""
        for title in destName:
            response = self.query_transfer_history(title)
            transfer_id = self.extract_id_from_rdict_by_name(response, title)
            if transfer_id is None:
                logger.error("No transfer ID found for title: %s", title)
                continue

            srcName.append(
                self.extract_srcname_from_rdict_by_name(response, title)
            )

            self.delete_transfer_history_by_id(transfer_id)
