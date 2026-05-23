"""SQLite persistence for Lost Apple App state."""

from __future__ import annotations

import json
from pathlib import Path

import aiosqlite

from lost_apple_app.models import DeviceSnapshot


class AppStorage:
    """Persist App settings and normalized device snapshots."""

    def __init__(self, database_path: Path) -> None:
        """Initialize storage for the given SQLite database path."""
        self._database_path = database_path

    async def initialize(self) -> None:
        """Create required tables if they do not already exist."""
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._database_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS snapshots (id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            await db.commit()

    async def upsert_snapshot(self, snapshot: DeviceSnapshot) -> None:
        """Insert or replace a device snapshot."""
        async with aiosqlite.connect(self._database_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO snapshots (id, payload) VALUES (?, ?)",
                (snapshot.id, snapshot.model_dump_json()),
            )
            await db.commit()

    async def list_snapshots(self) -> list[DeviceSnapshot]:
        """Return all known device snapshots sorted by display name."""
        async with aiosqlite.connect(self._database_path) as db:
            rows = await db.execute_fetchall("SELECT payload FROM snapshots")
        snapshots = [DeviceSnapshot.model_validate_json(row[0]) for row in rows]
        return sorted(snapshots, key=lambda item: item.name.casefold())

    async def set_polling_interval_minutes(self, value: int) -> None:
        """Persist polling interval in minutes."""
        if value < 5 or value > 60:
            msg = "Polling interval must be between 5 and 60 minutes"
            raise ValueError(msg)
        async with aiosqlite.connect(self._database_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('polling_interval_minutes', ?)",
                (json.dumps(value),),
            )
            await db.commit()

    async def get_polling_interval_minutes(self) -> int:
        """Return polling interval in minutes, defaulting to 15."""
        async with aiosqlite.connect(self._database_path) as db:
            cursor = await db.execute(
                "SELECT value FROM settings WHERE key = 'polling_interval_minutes'"
            )
            row = await cursor.fetchone()
        if row is None:
            return 15
        return int(json.loads(row[0]))
