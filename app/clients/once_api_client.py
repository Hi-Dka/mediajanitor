from typing import Any, Optional

from app.clients.api_client import CApiClient
from app.common.constants import HTTP_OK, HTTP_UNAUTHORIZED
from app.common.logger import logger


class CTryOnceLoginApiClient(CApiClient):
    """Auto Auth API Client"""

    def get(self, path: str, **kwargs: Any) -> Any:
        response = super().get(path, **kwargs)
        if response.status_code == HTTP_UNAUTHORIZED:
            logger.warning("Unauthorized access, attempting to login once...")
            if self.login():
                logger.info("Login succeeded")
                response = super().get(path, **kwargs)
            else:
                logger.error("Login failed, returning HTTP_UNAUTHORIZED")
                return HTTP_UNAUTHORIZED
        if response.status_code == HTTP_OK:
            response.raise_for_status()
            return response
        return response.status_code

    def post(
        self,
        path: str,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        response = super().post(path, data=data, json=json, **kwargs)
        if response.status_code == HTTP_UNAUTHORIZED:
            logger.warning("Unauthorized access, attempting to login once...")
            if self.login():
                logger.info("Login succeeded")
                response = super().post(path, data=data, json=json, **kwargs)
            else:
                logger.error("Login failed, returning HTTP_UNAUTHORIZED")
                return HTTP_UNAUTHORIZED
        if response.status_code == HTTP_OK:
            response.raise_for_status()
            return response
        logger.error(
            "Request failed with status code: %s", response.status_code
        )
        return response.status_code

    def delete(self, path: str, **kwargs: Any) -> Any:
        response = super().delete(path, **kwargs)
        if response.status_code == HTTP_UNAUTHORIZED:
            logger.warning("Unauthorized access, attempting to login once...")
            if self.login():
                logger.info("Login succeeded")
                response = super().delete(path, **kwargs)
            else:
                logger.error("Login failed, returning HTTP_UNAUTHORIZED")
                return HTTP_UNAUTHORIZED
        if response.status_code == HTTP_OK:
            response.raise_for_status()
            return response
        logger.error(
            "Delete request failed with status code: %s", response.status_code
        )
        return response.status_code
