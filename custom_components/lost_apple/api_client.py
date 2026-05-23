"""HTTP client for the Lost Apple App API."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import aiohttp


class LostAppleClient:
    """Client for the local Lost Apple App API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        token: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}

    async def health(self) -> dict[str, object]:
        """Return app health metadata from the API."""
        payload = await self._get_json("/api/v1/health")
        if not isinstance(payload, dict):
            message = "Lost Apple health endpoint returned a non-object payload"
            raise TypeError(message)
        return cast("dict[str, object]", payload)

    async def devices(self) -> list[dict[str, object]]:
        """Return the latest device snapshots from the API."""
        payload = await self._get_json("/api/v1/devices")
        if not isinstance(payload, list):
            message = "Lost Apple devices endpoint returned a non-list payload"
            raise TypeError(message)
        return [cast("dict[str, object]", item) for item in payload]

    async def _get_json(self, path: str) -> object:
        """Fetch JSON from the Lost Apple App API and raise on HTTP errors."""
        async with self._session.get(
            f"{self._base_url}{path}",
            headers=self._headers,
        ) as response:
            response.raise_for_status()
            return await response.json()
