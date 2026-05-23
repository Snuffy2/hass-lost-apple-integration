"""Boundary around FindMy.py so the App can run without live Apple access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime


class _FindMyLocationReport(Protocol):
    """Protocol for a FindMy.py location report."""

    latitude: float
    longitude: float
    horizontal_accuracy: float | None
    timestamp: datetime


class _FindMyRawDevice(Protocol):
    """Protocol for a raw FindMy.py device object."""

    identifier: object
    name: object
    battery_status: str | None
    location: _FindMyLocationReport


class _FindMySourceKey(Protocol):
    """Protocol for a FindMy.py key/accessory object."""

    def __hash__(self) -> int:
        """Enable hashing for stable map and test keys."""
        raise NotImplementedError


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


@dataclass(frozen=True, slots=True)
class FindMySource:
    """Project-owned configured source for FindMy lookups."""

    id: str
    name: str
    findmy_key_or_accessory: _FindMySourceKey
    battery_status: str | None = None


def normalize_findmy_device(raw_device: _FindMyRawDevice) -> FindMyDevice:
    """Normalize a raw FindMy.py device into app shape."""
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


def normalize_findmy_report(
    source: FindMySource,
    report: _FindMyLocationReport,
) -> FindMyDevice:
    """Normalize a FindMy.py location report using a configured source."""
    raw_accuracy = getattr(report, "horizontal_accuracy", None)
    return FindMyDevice(
        id=source.id,
        name=source.name,
        latitude=float(report.latitude),
        longitude=float(report.longitude),
        accuracy_m=None if raw_accuracy is None else float(raw_accuracy),
        battery_status=source.battery_status,
        last_reported_at=report.timestamp,
    )


class FindMyService:
    """Boundary to Fetch My Apple devices."""

    def __init__(
        self,
        account: object | None = None,
        sources: list[FindMySource] | None = None,
    ) -> None:
        """Initialize with optional authenticated account and configured sources."""
        self._account = account
        self._sources = tuple(sources or ())

    async def fetch_devices(self) -> list[FindMyDevice]:
        """Fetch official Apple account-discovered Find My devices."""
        if self._account is None or not self._sources:
            return []

        fetcher = getattr(self._account, "fetch_location", None)
        if not callable(fetcher):
            message = (
                "Authenticated FindMy account must implement fetch_location(); "
                "installed FindMy.py exposes: fetch_location, "
                "fetch_location_history, fetch_raw_reports."
            )
            raise TypeError(message)

        devices: list[FindMyDevice] = []
        for source in self._sources:
            location = await fetcher(source.findmy_key_or_accessory)
            if location is None:
                # Explicitly skip missing reports for a configured source.
                continue
            devices.append(normalize_findmy_report(source, location))

        return devices
