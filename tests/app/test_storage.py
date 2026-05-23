"""Tests for Lost Apple App storage."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from lost_apple_app.models import DeviceSnapshot
from lost_apple_app.storage import AppStorage

if TYPE_CHECKING:
    from pathlib import Path


async def test_storage_round_trips_device_snapshot(tmp_path: Path) -> None:
    """Store and retrieve a normalized device snapshot."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    snapshot = DeviceSnapshot(
        id="airtag-001",
        name="Keys",
        latitude=40.7128,
        longitude=-74.0060,
        accuracy_m=12.4,
        battery_status="medium",
        status="ok",
        last_reported_at=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
        last_polled_at=datetime(2026, 5, 23, 20, 35, tzinfo=UTC),
        error=None,
    )

    await storage.upsert_snapshot(snapshot)

    assert await storage.list_snapshots() == [snapshot]


async def test_storage_saves_polling_interval(tmp_path: Path) -> None:
    """Persist the user-selected polling interval."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()

    await storage.set_polling_interval_minutes(10)

    assert await storage.get_polling_interval_minutes() == 10
