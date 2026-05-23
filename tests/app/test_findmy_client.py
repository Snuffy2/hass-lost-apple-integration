"""Tests for FindMy.py adapter normalization."""

from __future__ import annotations

from datetime import UTC, datetime

from lost_apple_app.findmy_client import (
    FindMyDevice,
    FindMyService,
    FindMySource,
    normalize_findmy_device,
    normalize_findmy_report,
)


class RawLocation:
    """Fake FindMy.py location object."""

    latitude = 40.7128
    longitude = -74.006
    horizontal_accuracy = 12.4
    timestamp = datetime(2026, 5, 23, 20, 30, tzinfo=UTC)


class RawDevice:
    """Fake FindMy.py official device object."""

    identifier = "airtag-001"
    name = "Keys"
    battery_status = "medium"
    location = RawLocation()


class LocationReport:
    """Fake FindMy.py location report."""

    latitude = 40.7128
    longitude = -74.006
    horizontal_accuracy = 12.4
    timestamp = datetime(2026, 5, 23, 20, 30, tzinfo=UTC)


class FindMyKey:
    """Fake key/accessory source identifier used by account.fetch_location()."""

    def __init__(self, key: str) -> None:
        """Store the key used by the fake account."""
        self.key = key

    def __hash__(self) -> int:
        """Hash using the underlying stable key string."""
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        """Consider keys equal when the value matches."""
        return isinstance(other, FindMyKey) and self.key == other.key


class FakeFindMyAccount:
    """Fake account implementing find_location() with deterministic responses."""

    def __init__(self, mapping: dict[FindMyKey, object | None]) -> None:
        """Store the lookup table for key-to-report mapping."""
        self._mapping = mapping

    async def fetch_location(self, key: FindMyKey) -> object | None:
        """Return report for key or ``None`` when unavailable."""
        return self._mapping.get(key)


def test_normalize_findmy_device() -> None:
    """Raw FindMy.py device is normalized for polling."""
    normalized = normalize_findmy_device(RawDevice())
    expected = FindMyDevice(
        id="airtag-001",
        name="Keys",
        latitude=40.7128,
        longitude=-74.006,
        accuracy_m=12.4,
        battery_status="medium",
        last_reported_at=RawLocation.timestamp,
    )
    if normalized != expected:
        message = "Normalized device did not match expected output"
        raise AssertionError(message)


def test_normalize_findmy_report() -> None:
    """Location report is normalized into configured source metadata."""
    source = FindMySource(
        id="airtag-001",
        name="Keys",
        findmy_key_or_accessory=FindMyKey("airtag"),
        battery_status="medium",
    )
    normalized = normalize_findmy_report(source=source, report=LocationReport())
    expected = FindMyDevice(
        id="airtag-001",
        name="Keys",
        latitude=40.7128,
        longitude=-74.006,
        accuracy_m=12.4,
        battery_status="medium",
        last_reported_at=LocationReport.timestamp,
    )
    if normalized != expected:
        message = "Normalized report did not match configured source metadata"
        raise AssertionError(message)


async def test_fetch_devices_returns_empty_when_account_is_missing() -> None:
    """FindMyService returns empty list when account is missing."""
    service = FindMyService(
        sources=[
            FindMySource(
                id="airtag-001",
                name="Keys",
                findmy_key_or_accessory=FindMyKey("airtag"),
            )
        ]
    )
    devices = await service.fetch_devices()
    if devices != []:
        message = "Service without account should return an empty list"
        raise AssertionError(message)


async def test_fetch_devices_returns_empty_when_sources_are_missing() -> None:
    """FindMyService returns empty list when sources are missing."""
    service = FindMyService(account=FakeFindMyAccount({}))
    devices = await service.fetch_devices()
    if devices != []:
        message = "Service without sources should return an empty list"
        raise AssertionError(message)


async def test_fetch_devices_normalizes_account_locations() -> None:
    """FindMyService normalizes reports from account.fetch_location()."""
    key = FindMyKey("airtag")
    source = FindMySource(
        id="airtag-001",
        name="Keys",
        findmy_key_or_accessory=key,
        battery_status="medium",
    )
    account = FakeFindMyAccount({key: LocationReport()})
    service = FindMyService(account=account, sources=[source])
    devices = await service.fetch_devices()
    if devices != [normalize_findmy_report(source=source, report=LocationReport())]:
        message = "Service should normalize each location report by configured source"
        raise AssertionError(message)


async def test_fetch_devices_skips_missing_location_reports() -> None:
    """FindMyService skips configured sources that return no location report."""
    key = FindMyKey("airtag")
    source = FindMySource(
        id="airtag-001",
        name="Keys",
        findmy_key_or_accessory=key,
        battery_status="medium",
    )
    account = FakeFindMyAccount({key: None})
    service = FindMyService(account=account, sources=[source])
    if await service.fetch_devices() != []:
        message = "Service should skip missing location reports instead of failing"
        raise AssertionError(message)
