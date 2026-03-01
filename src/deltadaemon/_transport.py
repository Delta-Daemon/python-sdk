import json
from typing import Any

import aiohttp

from deltadaemon.errors import (
    APIError,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
    RequestTimeoutError,
    TransportError,
)
from deltadaemon.models import ErrorResponse


DEFAULT_BASE_URL = "https://api.deltadaemon.com"
DEFAULT_TIMEOUT = 30.0


class Transport:
    """Low-level HTTP transport using aiohttp."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._own_session = session is None
        self._session = session

    async def __aenter__(self) -> "Transport":
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """Perform GET request and return parsed JSON or raw string (for CSV)."""
        session = await self._ensure_session()
        url = f"{self._base_url}{path}"
        try:
            async with session.get(
                url, params=params, headers=self._headers()
            ) as response:
                content_type = response.headers.get("Content-Type", "")
                if "text/csv" in content_type or "application/csv" in content_type:
                    return await response.text()
                text = await response.text()
                if response.status >= 400:
                    self._raise_for_status(response.status, text, path)
                if not text:
                    return {}
                return json.loads(text)
        except aiohttp.ClientError as e:
            raise TransportError(str(e))
        except aiohttp.ServerTimeoutError as e:
            raise RequestTimeoutError(str(e), status_code=408)

    async def post(
        self,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform POST request and return parsed JSON."""
        session = await self._ensure_session()
        url = f"{self._base_url}{path}"
        try:
            async with session.post(
                url, json=body, headers=self._headers()
            ) as response:
                text = await response.text()
                if response.status >= 400:
                    self._raise_for_status(response.status, text, path)
                if not text:
                    return {}
                return json.loads(text)
        except aiohttp.ClientError as e:
            raise TransportError(str(e))
        except aiohttp.ServerTimeoutError as e:
            raise RequestTimeoutError(str(e), status_code=408)

    async def delete(self, path: str) -> dict[str, Any]:
        """Perform DELETE request and return parsed JSON."""
        session = await self._ensure_session()
        url = f"{self._base_url}{path}"
        try:
            async with session.delete(url, headers=self._headers()) as response:
                text = await response.text()
                if response.status >= 400:
                    self._raise_for_status(response.status, text, path)
                if not text:
                    return {}
                return json.loads(text)
        except aiohttp.ClientError as e:
            raise TransportError(str(e))
        except aiohttp.ServerTimeoutError as e:
            raise RequestTimeoutError(str(e), status_code=408)

    def _raise_for_status(self, status: int, text: str, path: str) -> None:
        error_msg = text
        try:
            data = json.loads(text)
            err = ErrorResponse.model_validate(data)
            error_msg = err.error
        except Exception:
            pass
        if status == 401:
            raise AuthenticationError(error_msg, status_code=401)
        if status == 402:
            raise PaymentRequiredError(error_msg, status_code=402)
        if status == 429:
            raise RateLimitError(error_msg, status_code=429)
        raise APIError(error_msg, status_code=status)
