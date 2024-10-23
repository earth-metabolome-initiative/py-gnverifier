"""Base module for handling API interactions."""

from time import sleep, time
from typing import Any

import compress_json  # type: ignore[import-untyped]
import requests
from cache_decorator import Cache  # type: ignore[import-untyped]
from requests import Response

from pygnverifier.__version__ import __version__


class BaseAPI:
    """Base class for API interactions."""

    BASE_URL: str = "https://verifier.globalnames.org/api/v1"
    SLEEP_TIME: float = 0.500

    def __init__(self, email: str, timeout: int = 10):
        """Initialize the BaseAPI class."""
        self._user_agent = f"pygnverifier/{__version__} ({email})"
        self._timeout = timeout

    def _auto_sleep(self) -> None:
        """Automatically sleep for a set time."""
        try:
            metadata: dict = compress_json.local_load("metadata.json")
        except FileNotFoundError:
            metadata = {
                "last_request": 0,
            }

        time_since_last_request = time() - metadata["last_request"]

        if time_since_last_request < self.SLEEP_TIME:
            sleep_time = self.SLEEP_TIME - time_since_last_request
            sleep(sleep_time)

        metadata["last_request"] = time()
        compress_json.local_dump(metadata, "metadata.json")

    @Cache(
        cache_path="{cache_dir}/{endpoint}.json.gz",
        validity_duration=60 * 60 * 24 * 7,
    )
    def _get(self, endpoint: str) -> Any:
        """Make a GET request to the API."""
        url = f"{self.BASE_URL}/{endpoint}"

        self._auto_sleep()

        response: Response = requests.get(
            url, headers={"accept": "application/json", "User-Agent": self._user_agent}, timeout=self._timeout
        )

        response.raise_for_status()
        return response.json()

    @Cache(
        cache_path="{cache_dir}/{endpoint}/{_hash}.json.gz",
        validity_duration=60 * 60 * 24 * 7,
    )
    def _post(self, endpoint: str, json: dict) -> Any:
        """Make a POST request to the API."""
        url = f"{self.BASE_URL}/{endpoint}"

        self._auto_sleep()

        response: Response = requests.post(
            url,
            json=json,
            headers={"Content-Type": "application/json", "User-Agent": self._user_agent},
            timeout=self._timeout,
        )

        response.raise_for_status()
        return response.json()
