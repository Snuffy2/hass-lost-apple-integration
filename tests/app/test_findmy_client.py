"""Tests for FindMy.py adapter normalization."""

from __future__ import annotations

from datetime import UTC, datetime

from lost_apple_app.findmy_client import (
    FindMyDevice,
    FindMyService,
    normalize_findmy_device,
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


class RawLocationMissingFields:
    """Fake FindMy.py location object with missing optional accuracy."""

    latitude = 40.7128
    longitude = -74.006
    horizontal_accuracy = None
    timestamp = datetime(2026, 5, 23, 20, 30, tzinfo=UTC)


class RawDeviceMissingOptionalFields:
    """Fake FindMy.py official device object with missing optional battery."""

    identifier = "airtag-002"
    name = "Backpack"
    battery_status = None
    location = RawLocationMissingFields()


class FakeFindMyAccount:
    """Fake account object that returns raw FindMy.py devices."""

    async def fetch_devices(self) -> list[object]:
        """Return raw devices to mimic the installed API."""
        return [RawDevice()]


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


def test_normalize_findmy_device_with_missing_optional_fields() -> None:
    """Optional location/battery attributes normalize to None when unavailable."""
    normalized = normalize_findmy_device(RawDeviceMissingOptionalFields())
    if normalized.accuracy_m is not None or normalized.battery_status is not None:
        message = "Optional None fields should remain None after normalization"
        raise AssertionError(message)


async def test_fetch_devices_returns_empty_when_account_is_missing() -> None:
    """FindMyService returns an empty list when not configured with account state."""
    service = FindMyService()
    devices = await service.fetch_devices()
    if devices != []:
        message = "Service without account should return an empty list"
        raise AssertionError(message)


async def test_fetch_devices_normalizes_account_devices() -> None:
    """FindMyService normalizes raw devices returned by the account interface."""
    service = FindMyService(account=FakeFindMyAccount())
    devices = await service.fetch_devices()
    expected = [normalize_findmy_device(RawDevice())]
    if devices != expected:
        message = "Service must normalize raw FindMy devices from account results"
        raise AssertionError(message)
