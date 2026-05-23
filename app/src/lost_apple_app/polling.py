"""Polling service for FindMy devices."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from lost_apple_app.models import DeviceSnapshot

if TYPE_CHECKING:
    from lost_apple_app.findmy_client import FindMyService
    from lost_apple_app.storage import AppStorage


class PollingService:
    """Poll FindMy.py and persist latest normalized device snapshots."""

    def __init__(
        self,
        storage: AppStorage,
        findmy: FindMyService,
    ) -> None:
        """Initialize the polling service."""
        self._storage = storage
        self._findmy = findmy

    async def poll_once(self, now: datetime | None = None) -> None:
        """Poll FindMy.py once and persist normalized snapshots."""
        polled_at = now or datetime.now(tz=UTC)
        devices = await self._findmy.fetch_devices()
        for device in devices:
            await self._storage.upsert_snapshot(
                DeviceSnapshot(
                    id=device.id,
                    name=device.name,
                    latitude=device.latitude,
                    longitude=device.longitude,
                    accuracy_m=device.accuracy_m,
                    battery_status=device.battery_status,
                    status="ok",
                    last_reported_at=device.last_reported_at,
                    last_polled_at=polled_at,
                    error=None,
                )
            )
