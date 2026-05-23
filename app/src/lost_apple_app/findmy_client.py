"""Boundary around FindMy.py so the App can run without live Apple access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from datetime import datetime

    from findmy.accessory import RollingKeyPairSource  # type: ignore[import-untyped]
    from findmy.keys import HasHashedPublicKey  # type: ignore[import-untyped]
    type _FindMySourceKey = HasHashedPublicKey | RollingKeyPairSource

    class _FindMyAccount(Protocol):
        """FindMy account protocol used by this adapter."""

        def fetch_location(
            self,
            key: _FindMySourceKey,
        ) -> Awaitable[_FindMyLocationReport | None]:
            ...
else:
    class _FindMySourceKey(Protocol):
        """Fallback protocol for key-like values when typed keys are unavailable."""

        def __hash__(self) -> int:
            """Hash helper for dictionary-compatible keys."""
            raise NotImplementedError

class _FindMyLocationReport(Protocol):
    """Protocol for a FindMy.py location report."""

    @property
    def latitude(self) -> float: ...

    @property
    def longitude(self) -> float: ...

    @property
    def horizontal_accuracy(self) -> float | None: ...

    @property
    def timestamp(self) -> datetime: ...


class _FindMyRawDevice(Protocol):
    """Protocol for a raw FindMy.py device object."""

    @property
    def identifier(self) -> object: ...

    @property
    def name(self) -> object: ...

    @property
    def battery_status(self) -> str | None: ...

    @property
    def location(self) -> _FindMyLocationReport: ...


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
        account: _FindMyAccount | None = None,
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

        fetcher_typed = cast(
            "Callable[[_FindMySourceKey], Awaitable[_FindMyLocationReport | None]]",
            fetcher,
        )

        devices: list[FindMyDevice] = []
        for source in self._sources:
            location = await fetcher_typed(source.findmy_key_or_accessory)
            if location is None:
                # Explicitly skip missing reports for a configured source.
                continue
            devices.append(normalize_findmy_report(source, location))

        return devices
