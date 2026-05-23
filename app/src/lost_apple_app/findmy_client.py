"""Boundary around FindMy.py so the App can run without live Apple access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from datetime import datetime


class _FindMyDeviceLocation(Protocol):
    """Protocol for the location object emitted by FindMy.py."""

    latitude: float
    longitude: float
    horizontal_accuracy: float | None
    timestamp: datetime


class _FindMyRawDevice(Protocol):
    """Protocol for a raw FindMy.py device object."""

    identifier: object
    name: object
    battery_status: str | None
    location: _FindMyDeviceLocation


@dataclass(frozen=True, slots=True)
class FindMyDevice:
    """Normalized device shape for adapter consumers."""

    id: str
    name: str
    latitude: float
    longitude: float
    accuracy_m: float | None
    battery_status: str | None
    last_reported_at: datetime


def normalize_findmy_device(raw_device: _FindMyRawDevice) -> FindMyDevice:
    """Normalize a FindMy.py device into app device shape."""
    location = raw_device.location
    raw_accuracy = getattr(location, "horizontal_accuracy", None)
    raw_battery_status = getattr(raw_device, "battery_status", None)

    return FindMyDevice(
        id=str(raw_device.identifier),
        name=str(raw_device.name),
        latitude=float(location.latitude),
        longitude=float(location.longitude),
        accuracy_m=None if raw_accuracy is None else float(raw_accuracy),
        battery_status=None if raw_battery_status is None else str(raw_battery_status),
        last_reported_at=location.timestamp,
    )


class FindMyService:
    """Boundary to Fetch My Apple devices."""

    def __init__(self, account: object | None = None) -> None:
        """Initialize with an optional authenticated FindMy account."""
        self._account = account

    async def fetch_devices(self) -> list[FindMyDevice]:
        """Fetch official Apple account-discovered Find My devices."""
        if self._account is None:
            return []

        fetcher = getattr(self._account, "fetch_devices", None)
        if not callable(fetcher):
            message = (
                "Authenticated FindMy account does not expose "
                "fetch_devices() in the installed FindMy.py version."
            )
            raise TypeError(message)

        typed_fetcher = cast("Callable[[], Awaitable[list[_FindMyRawDevice]]]", fetcher)
        raw_devices = await typed_fetcher()
        return [normalize_findmy_device(raw_device) for raw_device in raw_devices]
