from typing import Any, Optional
from urllib.parse import urljoin

import requests


class CApiClient:
    """API Client for making requests to a REST API"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, path: str, **kwargs: Any) -> Any:
        """Get a resource from the API"""
        url = urljoin(self.base_url, path)
        response = self.session.get(url, **kwargs)
        return response

    def post(
        self,
        path: str,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Post data to the API"""
        url = urljoin(self.base_url, path)
        response = self.session.post(url, data=data, json=json, **kwargs)
        return response

    def delete(self, path: str, **kwargs: Any) -> Any:
        """Delete a resource from the API"""
        url = urljoin(self.base_url, path)
        response = self.session.delete(url, **kwargs)
        return response

    def login(self) -> bool:
        """Login to the API and obtain an access token"""
        return False
