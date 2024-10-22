"""Base module for handling API interactions."""

from typing import Optional

import requests
from requests import Response


class BaseAPI:
    """Base class for API interactions."""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def _get(self, endpoint: str, headers: Optional[dict[str, str]] = None) -> Response:
        """Make a GET request to the API."""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {"accept": "application/json"}
        response: Response = requests.get(url, headers=headers, timeout=self.timeout)

        if response.status_code != 200:
            response.raise_for_status()  # Raise an error for bad responses
        return response

    def _post(self, endpoint: str, json: dict, headers: Optional[dict[str, str]] = None) -> Response:
        """Make a POST request to the API."""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {"Content-Type": "application/json"}
        response: Response = requests.post(url, json=json, headers=headers, timeout=self.timeout)

        response.raise_for_status()  # Raise an error for bad responses
        return response
