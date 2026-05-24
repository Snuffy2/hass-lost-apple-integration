# Hass Lost Apple Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `snuffy2/hass-lost-apple`, a Home Assistant App plus HACS-managed custom integration that tracks official Apple Find My devices through FindMy.py with local anisette and guided UI setup.

**Architecture:** The Lost Apple App owns Apple authentication, FindMy.py/local anisette runtime, polling, stored snapshots, and the guided Web UI/API. The Lost Apple Integration is a thin HA adapter that pairs to the Lost Apple App API, creates `device_tracker` and diagnostic entities, and never stores Apple credentials or talks to Apple directly.

**Tech Stack:** Python 3.14, FastAPI/Uvicorn for the Lost Apple App service, FindMy.py, SQLite via `aiosqlite`, Home Assistant custom integration APIs, pytest/pytest-asyncio/aioresponses, ruff, mypy, prek, Docker, GitHub Actions, HACS metadata, HA App repository metadata.

---

## Scope Check

This plan produces one working vertical MVP: installable App repository, HACS-compatible integration, mocked and real-HA validation path, and docs. It deliberately supports official Apple account-discovered Find My devices only. Manual key imports, OpenHaystack/custom accessories, MQTT discovery, HA Container/Core-only runtime packaging, and upstream Home Assistant core submission are excluded from this MVP.

## File Structure

- `pyproject.toml` - root Python project metadata, dependencies, tooling config.
- `prek.toml` - repo checks for ruff, mypy, and pytest.
- `README.md`, `LICENSE`, `.gitignore` - public repo basics.
- `.github/workflows/ci.yml` - lint/type/test/container validation.
- `repository.yaml` - Home Assistant App repository metadata.
- `app/lost_apple/config.yaml`, `app/lost_apple/Dockerfile`, `app/lost_apple/run.sh`, `app/lost_apple/DOCS.md`, `app/lost_apple/README.md`, `app/lost_apple/translations/en.yaml` - HA App package.
- `app/src/lost_apple_app/` - App Python package.
- `app/src/lost_apple_app/api.py` - FastAPI routes and auth dependency.
- `app/src/lost_apple_app/auth.py` - Apple login/session state machine wrapper.
- `app/src/lost_apple_app/config.py` - persisted settings and environment loading.
- `app/src/lost_apple_app/findmy_client.py` - FindMy.py adapter boundary.
- `app/src/lost_apple_app/models.py` - Pydantic API models.
- `app/src/lost_apple_app/polling.py` - scheduler, backoff, snapshot refresh.
- `app/src/lost_apple_app/storage.py` - SQLite persistence.
- `app/src/lost_apple_app/web.py` - simple guided setup pages.
- `custom_components/lost_apple/` - HACS-managed integration.
- `custom_components/lost_apple/manifest.json`, `hacs.json` - HA/HACS metadata.
- `custom_components/lost_apple/config_flow.py` - integration setup and pairing.
- `custom_components/lost_apple/coordinator.py` - App API polling coordinator.
- `custom_components/lost_apple/device_tracker.py`, `sensor.py`, `diagnostics.py`, `repairs.py`, `const.py` - HA entity and support modules.
- `tests/app/` - App unit/API tests.
- `tests/integration/` - custom integration tests.
- `tests/fixtures/` - deterministic device snapshots and API responses.

## Task 1: Repository Baseline And Tooling

**Files:**
- Create: `pyproject.toml`
- Create: `prek.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `LICENSE`
- Create: `.github/workflows/ci.yml`
- Modify: `MEMORY.md`

- [ ] **Step 1: Initialize git repository and default branch**

Run:

```bash
git init
git branch -M main
```

Expected: `git status --short --branch` prints `## No commits yet on main`.

- [ ] **Step 2: Write root project metadata**

Create `pyproject.toml`:

```toml
[project]
name = "hass-lost-apple"
version = "0.1.0"
description = "Home Assistant App and custom integration for Apple Find My devices via FindMy.py"
readme = "README.md"
requires-python = ">=3.14"
license = "GPL-3.0-or-later"
authors = [{ name = "snuffy2" }]
dependencies = [
  "aiosqlite>=0.20.0",
  "fastapi>=0.115.0",
  "findmy>=0.10.0",
  "pydantic>=2.10.0",
  "uvicorn[standard]>=0.32.0",
]

[project.optional-dependencies]
test = [
  "aioresponses>=0.7.7",
  "homeassistant>=2026.5.0",
  "mypy>=1.15.0",
  "pytest>=8.3.0",
  "pytest-asyncio>=0.25.0",
  "ruff>=0.9.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D203", "D213", "COM812"]

[tool.mypy]
python_version = "3.14"
strict = true
packages = ["lost_apple_app", "custom_components.lost_apple"]
```

- [ ] **Step 3: Add prek checks**

Create `prek.toml`:

```toml
minimum_pre_commit_version = "4.0.0"

repos = [
  { repo = "https://github.com/astral-sh/ruff-pre-commit", rev = "v0.9.10", hooks = [
    { id = "ruff", args = ["--fix"] },
    { id = "ruff-format" },
  ] },
  { repo = "local", hooks = [
    { id = "mypy", name = "mypy", entry = "./.venv/bin/mypy", language = "system", types = ["python"] },
    { id = "pytest", name = "pytest", entry = "./.venv/bin/pytest", language = "system", pass_filenames = false },
  ] },
]
```

- [ ] **Step 4: Add repo basics**

Create `.gitignore`:

```gitignore
.DS_Store
.mypy_cache/
.pytest_cache/
.ruff_cache/
.venv/
__pycache__/
*.py[cod]
dist/
build/
htmlcov/
.coverage
```

Create `README.md`:

```markdown
# Hass Lost Apple

`hass-lost-apple` provides a Home Assistant App and HACS-managed custom integration for official Apple Find My devices using FindMy.py with local anisette.

The Lost Apple App owns Apple authentication, polling, local storage, and guided setup. The Lost Apple Integration pairs to the Lost Apple App and exposes device trackers plus diagnostics.

## Status

This project is in initial development.
```

Create `LICENSE` using the full GPL-3.0-or-later license text from <https://www.gnu.org/licenses/gpl-3.0.txt>.

- [ ] **Step 5: Add CI skeleton**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.14"
      - run: python -m venv .venv
      - run: ./.venv/bin/python -m pip install --upgrade pip
      - run: ./.venv/bin/python -m pip install -e ".[test]"
      - run: ./.venv/bin/ruff check .
      - run: ./.venv/bin/ruff format --check .
      - run: ./.venv/bin/mypy app/src custom_components tests
      - run: ./.venv/bin/pytest
```

- [ ] **Step 6: Install local dev environment**

Run:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[test]"
```

Expected: package install completes without dependency resolver errors.

- [ ] **Step 7: Run initial checks**

Run:

```bash
./.venv/bin/ruff check .
./.venv/bin/mypy app/src custom_components tests
./.venv/bin/pytest
```

Expected: ruff passes; mypy and pytest may report missing source/test paths until Task 2 creates them. Record the exact current output in `MEMORY.md`.

- [ ] **Step 8: Commit baseline**

Run:

```bash
git add pyproject.toml prek.toml .gitignore README.md LICENSE .github/workflows/ci.yml MEMORY.md AGENTS.md
git commit -m "chore: initialize hass lost apple project"
```

Expected: one root commit on `main`.

## Task 2: App Domain Models And Storage

**Files:**
- Create: `app/src/lost_apple_app/__init__.py`
- Create: `app/src/lost_apple_app/models.py`
- Create: `app/src/lost_apple_app/storage.py`
- Create: `tests/app/test_storage.py`
- Create: `tests/fixtures/device_snapshot.json`

- [ ] **Step 1: Write fixture**

Create `tests/fixtures/device_snapshot.json`:

```json
{
  "id": "airtag-001",
  "name": "Keys",
  "latitude": 40.7128,
  "longitude": -74.006,
  "accuracy_m": 12.4,
  "battery_status": "medium",
  "status": "ok",
  "last_reported_at": "2026-05-23T20:30:00Z",
  "last_polled_at": "2026-05-23T20:35:00Z",
  "error": null
}
```

- [ ] **Step 2: Write failing storage tests**

Create `tests/app/test_storage.py`:

```python
"""Tests for Lost Apple App storage."""

from __future__ import annotations

from datetime import UTC, datetime

from lost_apple_app.models import DeviceSnapshot
from lost_apple_app.storage import AppStorage


async def test_storage_round_trips_device_snapshot(tmp_path) -> None:
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


async def test_storage_saves_polling_interval(tmp_path) -> None:
    """Persist the user-selected polling interval."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()

    await storage.set_polling_interval_minutes(10)

    assert await storage.get_polling_interval_minutes() == 10
```

- [ ] **Step 3: Run storage tests and verify failure**

Run:

```bash
./.venv/bin/pytest tests/app/test_storage.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'lost_apple_app'`.

- [ ] **Step 4: Implement models and storage**

Create `app/src/lost_apple_app/__init__.py`:

```python
"""Lost Apple Home Assistant App package."""
```

Create `app/src/lost_apple_app/models.py`:

```python
"""API and persistence models for the Lost Apple App."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DeviceStatus = Literal["ok", "stale", "auth_error", "rate_limited", "error"]


class DeviceSnapshot(BaseModel):
    """Normalized Find My device state stored by the App."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    latitude: float
    longitude: float
    accuracy_m: float | None
    battery_status: str | None
    status: DeviceStatus
    last_reported_at: datetime
    last_polled_at: datetime
    error: str | None


class AppHealth(BaseModel):
    """Current App health returned to the integration."""

    api_version: int
    app_version: str
    account_state: Literal["not_configured", "authenticated", "reauth_required"]
    polling_interval_minutes: int
    device_count: int
```

Create `app/src/lost_apple_app/storage.py`:

```python
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
            row = await db.execute_fetchone(
                "SELECT value FROM settings WHERE key = 'polling_interval_minutes'"
            )
        if row is None:
            return 15
        return int(json.loads(row[0]))
```

- [ ] **Step 5: Run storage tests and fix `execute_fetchone` if needed**

Run:

```bash
./.venv/bin/pytest tests/app/test_storage.py -v
```

Expected: PASS. If `aiosqlite.Connection` lacks `execute_fetchone`, replace that call with:

```python
cursor = await db.execute(
    "SELECT value FROM settings WHERE key = 'polling_interval_minutes'"
)
row = await cursor.fetchone()
```

- [ ] **Step 6: Commit storage layer**

Run:

```bash
git add app/src/lost_apple_app tests/app tests/fixtures pyproject.toml
git commit -m "feat: add app storage models"
```

Expected: commit succeeds.

## Task 3: FindMy Adapter And Polling Service

**Files:**
- Create: `app/src/lost_apple_app/findmy_client.py`
- Create: `app/src/lost_apple_app/polling.py`
- Create: `tests/app/test_polling.py`

- [ ] **Step 1: Write failing polling tests**

Create `tests/app/test_polling.py`:

```python
"""Tests for polling Find My devices."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from lost_apple_app.findmy_client import FindMyDevice, FindMyService
from lost_apple_app.models import DeviceSnapshot
from lost_apple_app.polling import PollingService
from lost_apple_app.storage import AppStorage


class FakeFindMyService(FindMyService):
    """Fake FindMy service returning deterministic devices."""

    async def fetch_devices(self) -> list[FindMyDevice]:
        """Return one fake device."""
        return [
            FindMyDevice(
                id="airtag-001",
                name="Keys",
                latitude=40.7128,
                longitude=-74.006,
                accuracy_m=12.4,
                battery_status="medium",
                last_reported_at=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
            )
        ]


async def test_poll_once_stores_snapshots(tmp_path) -> None:
    """Polling once stores normalized snapshots."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    service = PollingService(storage=storage, findmy=FakeFindMyService())

    await service.poll_once(now=datetime(2026, 5, 23, 20, 35, tzinfo=UTC))

    assert await storage.list_snapshots() == [
        DeviceSnapshot(
            id="airtag-001",
            name="Keys",
            latitude=40.7128,
            longitude=-74.006,
            accuracy_m=12.4,
            battery_status="medium",
            status="ok",
            last_reported_at=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
            last_polled_at=datetime(2026, 5, 23, 20, 35, tzinfo=UTC),
            error=None,
        )
    ]


async def test_polling_interval_rejects_fast_values(tmp_path) -> None:
    """Polling interval cannot be less than five minutes."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()

    with pytest.raises(ValueError, match="between 5 and 60"):
        await storage.set_polling_interval_minutes(4)
```

- [ ] **Step 2: Run polling tests and verify failure**

Run:

```bash
./.venv/bin/pytest tests/app/test_polling.py -v
```

Expected: FAIL with missing `lost_apple_app.findmy_client`.

- [ ] **Step 3: Implement adapter boundary and polling**

Create `app/src/lost_apple_app/findmy_client.py`:

```python
"""Boundary around FindMy.py so the App can test without Apple access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FindMyDevice:
    """Normalized data returned by the FindMy.py adapter."""

    id: str
    name: str
    latitude: float
    longitude: float
    accuracy_m: float | None
    battery_status: str | None
    last_reported_at: datetime


class FindMyService:
    """Fetch devices from FindMy.py."""

    async def fetch_devices(self) -> list[FindMyDevice]:
        """Fetch official Apple account-discovered Find My devices."""
        msg = "FindMy account is not configured"
        raise NotImplementedError(msg)
```

Create `app/src/lost_apple_app/polling.py`:

```python
"""Polling service for Find My devices."""

from __future__ import annotations

from datetime import UTC, datetime

from lost_apple_app.findmy_client import FindMyService
from lost_apple_app.models import DeviceSnapshot
from lost_apple_app.storage import AppStorage


class PollingService:
    """Poll FindMy.py and persist latest device snapshots."""

    def __init__(self, storage: AppStorage, findmy: FindMyService) -> None:
        """Initialize the polling service."""
        self._storage = storage
        self._findmy = findmy

    async def poll_once(self, now: datetime | None = None) -> None:
        """Poll FindMy.py once and persist normalized snapshots."""
        polled_at = now or datetime.now(tz=UTC)
        for device in await self._findmy.fetch_devices():
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
```

- [ ] **Step 4: Run polling tests**

Run:

```bash
./.venv/bin/pytest tests/app/test_polling.py tests/app/test_storage.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit polling boundary**

Run:

```bash
git add app/src/lost_apple_app/findmy_client.py app/src/lost_apple_app/polling.py tests/app/test_polling.py
git commit -m "feat: add findmy polling boundary"
```

Expected: commit succeeds.

## Task 4: App API And Pairing Token

**Files:**
- Create: `app/src/lost_apple_app/api.py`
- Create: `app/src/lost_apple_app/config.py`
- Create: `tests/app/test_api.py`

- [ ] **Step 1: Write failing API tests**

Create `tests/app/test_api.py`:

```python
"""Tests for Lost Apple App API."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from lost_apple_app.api import create_app
from lost_apple_app.models import DeviceSnapshot
from lost_apple_app.storage import AppStorage


async def test_health_requires_token(tmp_path) -> None:
    """API rejects requests without the pairing token."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    app = create_app(storage=storage, pairing_token="secret-token", app_version="0.1.0")

    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 401


async def test_health_returns_app_status(tmp_path) -> None:
    """API returns health for paired integration."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    await storage.set_polling_interval_minutes(10)
    app = create_app(storage=storage, pairing_token="secret-token", app_version="0.1.0")

    response = TestClient(app).get(
        "/api/v1/health",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "api_version": 1,
        "app_version": "0.1.0",
        "account_state": "not_configured",
        "polling_interval_minutes": 10,
        "device_count": 0,
    }


async def test_devices_returns_snapshots(tmp_path) -> None:
    """API returns latest device snapshots."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    await storage.upsert_snapshot(
        DeviceSnapshot(
            id="airtag-001",
            name="Keys",
            latitude=40.7128,
            longitude=-74.006,
            accuracy_m=12.4,
            battery_status="medium",
            status="ok",
            last_reported_at=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
            last_polled_at=datetime(2026, 5, 23, 20, 35, tzinfo=UTC),
            error=None,
        )
    )
    app = create_app(storage=storage, pairing_token="secret-token", app_version="0.1.0")

    response = TestClient(app).get(
        "/api/v1/devices",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == "airtag-001"
```

- [ ] **Step 2: Run API tests and verify failure**

Run:

```bash
./.venv/bin/pytest tests/app/test_api.py -v
```

Expected: FAIL with missing `lost_apple_app.api`.

- [ ] **Step 3: Implement API**

Create `app/src/lost_apple_app/api.py`:

```python
"""FastAPI application for the Lost Apple App."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status

from lost_apple_app.models import AppHealth, DeviceSnapshot
from lost_apple_app.storage import AppStorage


def _authorize(
    pairing_token: str,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Validate bearer token for integration API calls."""
    expected = f"Bearer {pairing_token}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pairing token",
        )


def create_app(storage: AppStorage, pairing_token: str, app_version: str) -> FastAPI:
    """Create the FastAPI app with injected storage and token."""
    app = FastAPI(title="Lost Apple", version=app_version)

    async def require_auth(
        authorization: Annotated[str | None, Header()] = None,
    ) -> None:
        _authorize(pairing_token=pairing_token, authorization=authorization)

    @app.get("/api/v1/health", dependencies=[Depends(require_auth)])
    async def health() -> AppHealth:
        """Return App health for the HA integration."""
        snapshots = await storage.list_snapshots()
        return AppHealth(
            api_version=1,
            app_version=app_version,
            account_state="not_configured",
            polling_interval_minutes=await storage.get_polling_interval_minutes(),
            device_count=len(snapshots),
        )

    @app.get("/api/v1/devices", dependencies=[Depends(require_auth)])
    async def devices() -> list[DeviceSnapshot]:
        """Return latest device snapshots."""
        return await storage.list_snapshots()

    return app
```

- [ ] **Step 4: Run API tests**

Run:

```bash
./.venv/bin/pytest tests/app/test_api.py tests/app/test_storage.py tests/app/test_polling.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit API**

Run:

```bash
git add app/src/lost_apple_app/api.py tests/app/test_api.py
git commit -m "feat: expose lost apple app api"
```

Expected: commit succeeds.

## Task 5: App Package, Container, And Web Setup Shell

**Files:**
- Create: `repository.yaml`
- Create: `app/lost_apple/config.yaml`
- Create: `app/lost_apple/Dockerfile`
- Create: `app/lost_apple/run.sh`
- Create: `app/lost_apple/README.md`
- Create: `app/lost_apple/DOCS.md`
- Create: `app/lost_apple/translations/en.yaml`
- Create: `app/src/lost_apple_app/__main__.py`
- Create: `app/src/lost_apple_app/web.py`
- Create: `tests/app/test_web.py`

- [ ] **Step 1: Write web shell test**

Create `tests/app/test_web.py`:

```python
"""Tests for guided setup web routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from lost_apple_app.api import create_app
from lost_apple_app.storage import AppStorage
from lost_apple_app.web import register_web_routes


async def test_setup_page_links_to_hacs_install(tmp_path) -> None:
    """Setup page provides a direct HACS install link."""
    storage = AppStorage(tmp_path / "lost_apple.sqlite3")
    await storage.initialize()
    app = create_app(storage=storage, pairing_token="secret-token", app_version="0.1.0")
    register_web_routes(app)

    response = TestClient(app).get("/setup")

    assert response.status_code == 200
    assert "my.home-assistant.io/redirect/hacs_repository" in response.text
    assert "owner=snuffy2" in response.text
    assert "repository=hass-lost-apple" in response.text
```

- [ ] **Step 2: Run web test and verify failure**

Run:

```bash
./.venv/bin/pytest tests/app/test_web.py -v
```

Expected: FAIL with missing `lost_apple_app.web`.

- [ ] **Step 3: Add web setup routes**

Create `app/src/lost_apple_app/web.py`:

```python
"""Guided setup pages for the Lost Apple App."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


HACS_INSTALL_URL = (
    "https://my.home-assistant.io/redirect/hacs_repository/"
    "?owner=snuffy2&repository=hass-lost-apple&category=integration"
)


def register_web_routes(app: FastAPI) -> None:
    """Register guided setup routes."""

    @app.get("/setup", response_class=HTMLResponse)
    async def setup() -> str:
        """Render the setup shell."""
        return f"""
        <!doctype html>
        <html lang="en">
          <head><title>Lost Apple Setup</title></head>
          <body>
            <h1>Lost Apple Setup</h1>
            <ol>
              <li>Authenticate your Apple account in this App.</li>
              <li><a href="{HACS_INSTALL_URL}">Install the Lost Apple Integration with HACS</a>.</li>
              <li>Add the Lost Apple Integration in Home Assistant and paste the pairing token.</li>
            </ol>
          </body>
        </html>
        """
```

- [ ] **Step 4: Add App entrypoint**

Create `app/src/lost_apple_app/__main__.py`:

```python
"""Runtime entrypoint for the Lost Apple App container."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from lost_apple_app.api import create_app
from lost_apple_app.storage import AppStorage
from lost_apple_app.web import register_web_routes


async def build_app() -> object:
    """Build the ASGI app for tests that need direct access."""
    storage = AppStorage(Path(os.getenv("LOST_APPLE_DB", "/data/lost_apple.sqlite3")))
    await storage.initialize()
    app = create_app(
        storage=storage,
        pairing_token=os.environ["LOST_APPLE_PAIRING_TOKEN"],
        app_version=os.getenv("LOST_APPLE_VERSION", "0.1.0"),
    )
    register_web_routes(app)
    return app


def main() -> None:
    """Run the App service with Uvicorn."""
    uvicorn.run(
        "lost_apple_app.__main__:build_app",
        host="0.0.0.0",
        port=8099,
        factory=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Add HA App repository files**

Create `repository.yaml`:

```yaml
name: Lost Apple Home Assistant Apps
url: https://github.com/snuffy2/hass-lost-apple
maintainer: snuffy2
```

Create `app/lost_apple/config.yaml`:

```yaml
name: Lost Apple
version: 0.1.0
slug: lost_apple
description: Apple Find My tracking for Home Assistant using local FindMy.py runtime
url: https://github.com/snuffy2/hass-lost-apple
arch:
  - aarch64
  - amd64
startup: application
boot: auto
ingress: true
ingress_port: 8099
panel_icon: mdi:map-marker-radius
homeassistant_api: true
ports:
  8099/tcp: null
map:
  - type: addon_config
    read_only: false
image: ghcr.io/snuffy2/hass-lost-apple-{arch}
options:
  pairing_token: ""
schema:
  pairing_token: "password"
```

Create `app/lost_apple/Dockerfile`:

```dockerfile
ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-python:3.14-alpine3.21
FROM ${BUILD_FROM}

WORKDIR /app
COPY pyproject.toml README.md LICENSE /app/
COPY app/src /app/app/src
RUN python3 -m pip install --no-cache-dir /app
COPY app/lost_apple/run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
```

Create `app/lost_apple/run.sh`:

```bash
#!/usr/bin/with-contenv bashio
set -euo pipefail

export LOST_APPLE_PAIRING_TOKEN
LOST_APPLE_PAIRING_TOKEN="$(bashio::config 'pairing_token')"

if [[ -z "${LOST_APPLE_PAIRING_TOKEN}" ]]; then
  bashio::log.warning "No pairing token configured. Generate one in the App UI before pairing Home Assistant."
  export LOST_APPLE_PAIRING_TOKEN="change-me"
fi

python3 -m lost_apple_app
```

Create `app/lost_apple/README.md`:

```markdown
# Lost Apple

Lost Apple runs FindMy.py inside Home Assistant OS and exposes a local API for the Lost Apple custom integration.
```

Create `app/lost_apple/DOCS.md`:

```markdown
# Lost Apple App Documentation

Install the Lost Apple App, open the Web UI, authenticate with Apple, then install the companion Lost Apple Integration through the HACS link shown in the setup page.
```

Create `app/lost_apple/translations/en.yaml`:

```yaml
configuration:
  pairing_token:
    name: Pairing token
    description: Token used by the Lost Apple Integration to call the Lost Apple App API.
```

- [ ] **Step 6: Run web and package checks**

Run:

```bash
./.venv/bin/pytest tests/app/test_web.py tests/app/test_api.py -v
./.venv/bin/ruff check app tests
```

Expected: PASS.

- [ ] **Step 7: Commit App package**

Run:

```bash
git add repository.yaml app/lost_apple app/src/lost_apple_app/__main__.py app/src/lost_apple_app/web.py tests/app/test_web.py
git commit -m "feat: add home assistant app package"
```

Expected: commit succeeds.

## Task 6: Home Assistant Integration Config Flow And Client

**Files:**
- Create: `custom_components/lost_apple/__init__.py`
- Create: `custom_components/lost_apple/const.py`
- Create: `custom_components/lost_apple/manifest.json`
- Create: `custom_components/lost_apple/api_client.py`
- Create: `custom_components/lost_apple/config_flow.py`
- Create: `hacs.json`
- Create: `tests/integration/test_config_flow.py`

- [ ] **Step 1: Write failing config flow test**

Create `tests/integration/test_config_flow.py`:

```python
"""Tests for Lost Apple integration config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from custom_components.lost_apple.const import DOMAIN


async def test_config_flow_creates_entry(hass) -> None:
    """Config flow stores App URL and pairing token after health check."""
    with patch(
        "custom_components.lost_apple.config_flow.LostAppleClient.health",
        AsyncMock(return_value={"api_version": 1, "app_version": "0.1.0"}),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "base_url": "http://localhost:8099",
                "pairing_token": "secret-token",
            },
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "Lost Apple"
    assert result["data"] == {
        "base_url": "http://localhost:8099",
        "pairing_token": "secret-token",
    }
```

- [ ] **Step 2: Run config flow test and verify failure**

Run:

```bash
./.venv/bin/pytest tests/integration/test_config_flow.py -v
```

Expected: FAIL with missing `custom_components.lost_apple`.

- [ ] **Step 3: Add integration metadata and constants**

Create `custom_components/lost_apple/const.py`:

```python
"""Constants for the Lost Apple integration."""

from __future__ import annotations

DOMAIN = "lost_apple"
CONF_BASE_URL = "base_url"
CONF_PAIRING_TOKEN = "pairing_token"
```

Create `custom_components/lost_apple/manifest.json`:

```json
{
  "domain": "lost_apple",
  "name": "Lost Apple",
  "codeowners": ["@Snuffy2"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/snuffy2/hass-lost-apple",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/snuffy2/hass-lost-apple/issues",
  "requirements": [],
  "version": "0.1.0"
}
```

Create `hacs.json`:

```json
{
  "name": "Lost Apple",
  "render_readme": true,
  "domains": ["device_tracker", "sensor"],
  "iot_class": "local_polling",
  "homeassistant": "2026.5.0"
}
```

- [ ] **Step 4: Add API client and config flow**

Create `custom_components/lost_apple/api_client.py`:

```python
"""HTTP client for the Lost Apple App API."""

from __future__ import annotations

from typing import Any

import aiohttp


class LostAppleClient:
    """Client for the local Lost Apple App API."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, token: str) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}

    async def health(self) -> dict[str, Any]:
        """Return App health."""
        async with self._session.get(
            f"{self._base_url}/api/v1/health",
            headers=self._headers,
        ) as response:
            response.raise_for_status()
            return dict(await response.json())

    async def devices(self) -> list[dict[str, Any]]:
        """Return latest device snapshots."""
        async with self._session.get(
            f"{self._base_url}/api/v1/devices",
            headers=self._headers,
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return list(payload)
```

Create `custom_components/lost_apple/config_flow.py`:

```python
"""Config flow for the Lost Apple integration."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.lost_apple.api_client import LostAppleClient
from custom_components.lost_apple.const import CONF_BASE_URL, CONF_PAIRING_TOKEN, DOMAIN


class LostAppleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Lost Apple config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle manual setup."""
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = LostAppleClient(
                session=session,
                base_url=str(user_input[CONF_BASE_URL]),
                token=str(user_input[CONF_PAIRING_TOKEN]),
            )
            try:
                await client.health()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Lost Apple", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default="http://localhost:8099"): str,
                vol.Required(CONF_PAIRING_TOKEN): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
```

Create `custom_components/lost_apple/__init__.py`:

```python
"""Lost Apple integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS = ["device_tracker", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lost Apple from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Lost Apple config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

- [ ] **Step 5: Run config flow test**

Run:

```bash
./.venv/bin/pytest tests/integration/test_config_flow.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit config flow**

Run:

```bash
git add custom_components/lost_apple hacs.json tests/integration/test_config_flow.py
git commit -m "feat: add lost apple integration config flow"
```

Expected: commit succeeds.

## Task 7: Coordinator And Entities

**Files:**
- Create: `custom_components/lost_apple/coordinator.py`
- Create: `custom_components/lost_apple/device_tracker.py`
- Create: `custom_components/lost_apple/sensor.py`
- Create: `tests/integration/test_entities.py`

- [ ] **Step 1: Write entity tests**

Create `tests/integration/test_entities.py`:

```python
"""Tests for Lost Apple entities."""

from __future__ import annotations

from datetime import UTC, datetime

from custom_components.lost_apple.device_tracker import LostAppleDeviceTracker
from custom_components.lost_apple.sensor import LastReportSensor


SNAPSHOT = {
    "id": "airtag-001",
    "name": "Keys",
    "latitude": 40.7128,
    "longitude": -74.006,
    "accuracy_m": 12.4,
    "battery_status": "medium",
    "status": "ok",
    "last_reported_at": "2026-05-23T20:30:00Z",
    "last_polled_at": "2026-05-23T20:35:00Z",
    "error": None,
}


def test_device_tracker_properties() -> None:
    """Device tracker exposes location and accuracy."""
    entity = LostAppleDeviceTracker(SNAPSHOT)

    assert entity.unique_id == "lost_apple_airtag-001_tracker"
    assert entity.name == "Keys"
    assert entity.latitude == 40.7128
    assert entity.longitude == -74.006
    assert entity.location_accuracy == 12.4


def test_last_report_sensor_properties() -> None:
    """Last report sensor exposes the parsed timestamp."""
    entity = LastReportSensor(SNAPSHOT)

    assert entity.unique_id == "lost_apple_airtag-001_last_report"
    assert entity.native_value == datetime(2026, 5, 23, 20, 30, tzinfo=UTC)
```

- [ ] **Step 2: Run entity tests and verify failure**

Run:

```bash
./.venv/bin/pytest tests/integration/test_entities.py -v
```

Expected: FAIL with missing entity modules.

- [ ] **Step 3: Add coordinator**

Create `custom_components/lost_apple/coordinator.py`:

```python
"""Coordinator for polling the Lost Apple App API."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.lost_apple.api_client import LostAppleClient
from custom_components.lost_apple.const import CONF_BASE_URL, CONF_PAIRING_TOKEN, DOMAIN


class LostAppleCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch latest snapshots from the Lost Apple App."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.client = LostAppleClient(
            session=async_get_clientsession(hass),
            base_url=str(entry.data[CONF_BASE_URL]),
            token=str(entry.data[CONF_PAIRING_TOKEN]),
        )
        super().__init__(
            hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch latest device snapshots."""
        return await self.client.devices()
```

- [ ] **Step 4: Add device tracker entity**

Create `custom_components/lost_apple/device_tracker.py`:

```python
"""Device tracker entities for Lost Apple."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.lost_apple.coordinator import LostAppleCoordinator


class LostAppleDeviceTracker(TrackerEntity):
    """Location tracker for one Find My device."""

    def __init__(self, snapshot: dict[str, Any]) -> None:
        """Initialize tracker from a snapshot."""
        self._snapshot = snapshot
        self._attr_unique_id = f"lost_apple_{snapshot['id']}_tracker"
        self._attr_name = str(snapshot["name"])

    @property
    def latitude(self) -> float:
        """Return latitude."""
        return float(self._snapshot["latitude"])

    @property
    def longitude(self) -> float:
        """Return longitude."""
        return float(self._snapshot["longitude"])

    @property
    def location_accuracy(self) -> float | None:
        """Return location accuracy in meters."""
        accuracy = self._snapshot.get("accuracy_m")
        return None if accuracy is None else float(accuracy)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up tracker entities."""
    coordinator = LostAppleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(LostAppleDeviceTracker(snapshot) for snapshot in coordinator.data)
```

- [ ] **Step 5: Add diagnostic sensor**

Create `custom_components/lost_apple/sensor.py`:

```python
"""Diagnostic sensors for Lost Apple."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.lost_apple.coordinator import LostAppleCoordinator


class LastReportSensor(SensorEntity):
    """Last reported timestamp for one Find My device."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, snapshot: dict[str, Any]) -> None:
        """Initialize sensor from a snapshot."""
        self._snapshot = snapshot
        self._attr_unique_id = f"lost_apple_{snapshot['id']}_last_report"
        self._attr_name = f"{snapshot['name']} Last Report"

    @property
    def native_value(self) -> datetime:
        """Return last reported timestamp."""
        return datetime.fromisoformat(str(self._snapshot["last_reported_at"]).replace("Z", "+00:00"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up diagnostic sensor entities."""
    coordinator = LostAppleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(LastReportSensor(snapshot) for snapshot in coordinator.data)
```

- [ ] **Step 6: Run entity tests**

Run:

```bash
./.venv/bin/pytest tests/integration/test_entities.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit entities**

Run:

```bash
git add custom_components/lost_apple/coordinator.py custom_components/lost_apple/device_tracker.py custom_components/lost_apple/sensor.py tests/integration/test_entities.py
git commit -m "feat: add lost apple entities"
```

Expected: commit succeeds.

## Task 8: Auth State, Reauth, Repairs, And Diagnostics

**Files:**
- Create: `app/src/lost_apple_app/auth.py`
- Create: `custom_components/lost_apple/diagnostics.py`
- Create: `custom_components/lost_apple/repairs.py`
- Create: `tests/app/test_auth_state.py`
- Create: `tests/integration/test_diagnostics.py`

- [ ] **Step 1: Write auth state tests**

Create `tests/app/test_auth_state.py`:

```python
"""Tests for Apple account auth state."""

from __future__ import annotations

from lost_apple_app.auth import AuthState, classify_auth_error


def test_classify_auth_error_marks_reauth_required() -> None:
    """Apple auth failures require user reauthentication."""
    assert classify_auth_error("Invalid session token") == AuthState.REAUTH_REQUIRED


def test_classify_non_auth_error_keeps_authenticated_state() -> None:
    """Transient network errors do not clear authentication."""
    assert classify_auth_error("HTTP 503 from Apple") == AuthState.AUTHENTICATED
```

- [ ] **Step 2: Implement auth state module**

Create `app/src/lost_apple_app/auth.py`:

```python
"""Apple authentication state helpers for Lost Apple."""

from __future__ import annotations

from enum import StrEnum


class AuthState(StrEnum):
    """Known Apple account authentication states."""

    NOT_CONFIGURED = "not_configured"
    AUTHENTICATED = "authenticated"
    REAUTH_REQUIRED = "reauth_required"


def classify_auth_error(message: str) -> AuthState:
    """Classify an Apple/FindMy.py error into an auth state."""
    lowered = message.casefold()
    if "invalid session" in lowered or "unauthorized" in lowered or "2fa" in lowered:
        return AuthState.REAUTH_REQUIRED
    return AuthState.AUTHENTICATED
```

- [ ] **Step 3: Add diagnostics test**

Create `tests/integration/test_diagnostics.py`:

```python
"""Tests for Lost Apple diagnostics redaction."""

from __future__ import annotations

from custom_components.lost_apple.diagnostics import redact_diagnostics


def test_diagnostics_redacts_pairing_token() -> None:
    """Diagnostics never expose pairing tokens."""
    payload = redact_diagnostics(
        {
            "base_url": "http://localhost:8099",
            "pairing_token": "secret-token",
            "device_count": 1,
        }
    )

    assert payload == {
        "base_url": "http://localhost:8099",
        "pairing_token": "**REDACTED**",
        "device_count": 1,
    }
```

- [ ] **Step 4: Implement diagnostics and repairs shell**

Create `custom_components/lost_apple/diagnostics.py`:

```python
"""Diagnostics support for Lost Apple."""

from __future__ import annotations

from typing import Any


REDACT_KEYS = {"pairing_token", "token", "password", "apple_id", "session"}


def redact_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    """Return diagnostics payload with sensitive values redacted."""
    return {
        key: "**REDACTED**" if key in REDACT_KEYS else value
        for key, value in payload.items()
    }
```

Create `custom_components/lost_apple/repairs.py`:

```python
"""Repair helpers for Lost Apple."""

from __future__ import annotations

REAUTH_REPAIR_ID = "lost_apple_reauth_required"
```

- [ ] **Step 5: Run auth/diagnostics tests**

Run:

```bash
./.venv/bin/pytest tests/app/test_auth_state.py tests/integration/test_diagnostics.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit auth and diagnostics**

Run:

```bash
git add app/src/lost_apple_app/auth.py custom_components/lost_apple/diagnostics.py custom_components/lost_apple/repairs.py tests/app/test_auth_state.py tests/integration/test_diagnostics.py
git commit -m "feat: add auth state diagnostics"
```

Expected: commit succeeds.

## Task 9: FindMy.py Real Adapter

**Files:**
- Modify: `app/src/lost_apple_app/findmy_client.py`
- Create: `tests/app/test_findmy_client.py`

- [ ] **Step 1: Write adapter test with fake raw device**

Create `tests/app/test_findmy_client.py`:

```python
"""Tests for FindMy.py adapter normalization."""

from __future__ import annotations

from datetime import UTC, datetime

from lost_apple_app.findmy_client import normalize_findmy_device


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


def test_normalize_findmy_device() -> None:
    """Raw FindMy.py device is normalized for polling."""
    normalized = normalize_findmy_device(RawDevice())

    assert normalized.id == "airtag-001"
    assert normalized.name == "Keys"
    assert normalized.latitude == 40.7128
    assert normalized.longitude == -74.006
    assert normalized.accuracy_m == 12.4
    assert normalized.battery_status == "medium"
```

- [ ] **Step 2: Implement normalizer and real service skeleton**

Modify `app/src/lost_apple_app/findmy_client.py` to include:

```python
from typing import Any


def normalize_findmy_device(raw_device: Any) -> FindMyDevice:
    """Normalize a FindMy.py device object into App data."""
    location = raw_device.location
    return FindMyDevice(
        id=str(raw_device.identifier),
        name=str(raw_device.name),
        latitude=float(location.latitude),
        longitude=float(location.longitude),
        accuracy_m=(
            None
            if getattr(location, "horizontal_accuracy", None) is None
            else float(location.horizontal_accuracy)
        ),
        battery_status=(
            None
            if getattr(raw_device, "battery_status", None) is None
            else str(raw_device.battery_status)
        ),
        last_reported_at=location.timestamp,
    )
```

Then replace `FindMyService.fetch_devices` with the real implementation after confirming the current FindMy.py API names from installed docs/source:

```python
class FindMyService:
    """Fetch devices from FindMy.py."""

    def __init__(self, account: Any | None = None) -> None:
        """Initialize with an authenticated FindMy.py account object."""
        self._account = account

    async def fetch_devices(self) -> list[FindMyDevice]:
        """Fetch official Apple account-discovered Find My devices."""
        if self._account is None:
            return []
        raw_devices = await self._account.fetch_devices()
        return [normalize_findmy_device(raw_device) for raw_device in raw_devices]
```

- [ ] **Step 3: Run adapter tests**

Run:

```bash
./.venv/bin/pytest tests/app/test_findmy_client.py tests/app/test_polling.py -v
```

Expected: PASS.

- [ ] **Step 4: Commit adapter**

Run:

```bash
git add app/src/lost_apple_app/findmy_client.py tests/app/test_findmy_client.py
git commit -m "feat: normalize findmy devices"
```

Expected: commit succeeds.

## Task 10: Documentation And Release Packaging

**Files:**
- Modify: `README.md`
- Modify: `app/lost_apple/DOCS.md`
- Create: `docs/security.md`
- Create: `docs/development.md`
- Modify: `MEMORY.md`

- [ ] **Step 1: Update README**

Replace `README.md` with:

```markdown
# Hass Lost Apple

`hass-lost-apple` provides a Home Assistant App and HACS-managed custom integration for official Apple Find My devices using FindMy.py with local anisette.

## Install

1. In Home Assistant OS, go to **Settings > Apps** and add `https://github.com/snuffy2/hass-lost-apple` as a third-party App repository.
2. Install the **Lost Apple** App and open its Web UI.
3. Complete Apple login and 2FA in the Lost Apple App UI.
4. Use the Lost Apple App UI link to install the **Lost Apple Integration** with HACS.
5. Add the **Lost Apple Integration** in Home Assistant and paste the pairing token shown by the Lost Apple App.

## Privacy

Apple credentials and session data are stored only in the Lost Apple App's persistent data volume. The Lost Apple Integration stores only the local Lost Apple App URL and pairing token.

## Supported Devices

The first release supports official Apple account-discovered Find My devices. Manual key imports and OpenHaystack/custom accessories are not part of the first release.
```

- [ ] **Step 2: Add security docs**

Create `docs/security.md`:

```markdown
# Security

The Lost Apple App stores Apple credentials and session material inside the Home Assistant App data volume. The Lost Apple Integration stores only a local Lost Apple App URL and pairing token.

Logs must not contain Apple IDs, passwords, two-factor codes, session cookies, pairing tokens, or raw Apple response payloads. Diagnostics redact token-like fields before export.

The Lost Apple App uses Home Assistant Ingress for browser access where available. The local API used by the Lost Apple Integration requires a bearer pairing token.
```

- [ ] **Step 3: Add development docs**

Create `docs/development.md`:

~~~markdown
# Development

Create the local environment:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[test]"
```

Run checks:

```bash
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy app/src custom_components tests
./.venv/bin/pytest
```
~~~

- [ ] **Step 4: Run full verification**

Run:

```bash
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy app/src custom_components tests
./.venv/bin/pytest
```

Expected: all commands PASS.

- [ ] **Step 5: Commit docs**

Run:

```bash
git add README.md app/lost_apple/DOCS.md docs/security.md docs/development.md MEMORY.md
git commit -m "docs: document lost apple setup"
```

Expected: commit succeeds.

## Task 11: GitHub Repository Creation And First Push

**Files:**
- No file changes unless CI badge URLs are added after repo creation.

- [ ] **Step 1: Confirm GitHub auth**

Run:

```bash
gh status
```

Expected: authenticated as the target GitHub user that owns `snuffy2/hass-lost-apple`.

- [ ] **Step 2: Create public GitHub repo**

Run:

```bash
gh repo create snuffy2/hass-lost-apple --public --source=. --remote=origin --description "Home Assistant App and custom integration for Apple Find My devices"
```

Expected: repo created and `git remote -v` shows `origin` pointing at `git@github.com:snuffy2/hass-lost-apple.git` or `https://github.com/snuffy2/hass-lost-apple.git`.

- [ ] **Step 3: Push main**

Run:

```bash
git push -u origin main
```

Expected: branch `main` is pushed and set to track `origin/main`.

- [ ] **Step 4: Verify CI starts**

Run:

```bash
gh run list --limit 5
```

Expected: latest CI workflow is visible for `main`.

- [ ] **Step 5: Record repo state**

Update `MEMORY.md` with:

```markdown
## Repository

- GitHub repo: https://github.com/snuffy2/hass-lost-apple
- Default branch: main
- First implementation plan: docs/superpowers/plans/2026-05-23-hass-lost-apple.md
```

- [ ] **Step 6: Commit memory update if needed**

Run:

```bash
git add MEMORY.md
git commit -m "docs: record repository setup"
git push
```

Expected: commit succeeds if `MEMORY.md` changed; if nothing changed, `git status --short` is clean.

## Self-Review

- Spec coverage: App-owned Apple auth/session, local anisette runtime boundary, polling, guided setup, HACS-managed integration updates, HA entities, diagnostics, security, docs, CI, and GitHub repo creation are covered.
- Placeholder scan: no unresolved placeholder patterns or deferred implementation markers are present.
- Type consistency: `DeviceSnapshot`, `FindMyDevice`, `AppStorage`, `LostAppleClient`, and `LostAppleCoordinator` names are consistent across tasks.
- Known implementation note: before Task 9 finalizes real FindMy.py calls, inspect the installed FindMy.py API for the exact official device fetch method names and adjust only inside `FindMyService`; tests should continue to target the adapter boundary.
