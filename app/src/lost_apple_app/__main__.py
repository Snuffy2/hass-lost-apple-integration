"""Application entrypoint for the Lost Apple App."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

import uvicorn

from lost_apple_app.api import create_app
from lost_apple_app.config import resolve_pairing_token
from lost_apple_app.storage import AppStorage
from lost_apple_app.web import register_web_routes

if TYPE_CHECKING:
    from fastapi import FastAPI

DEFAULT_DATABASE_PATH: Final = "/data/lost_apple.sqlite3"
DEFAULT_APP_VERSION: Final = "0.1.0"


def _resolve_database_path() -> Path:
    """Return the configured database path from the environment."""
    configured = os.getenv("LOST_APPLE_DB", DEFAULT_DATABASE_PATH)
    return Path(configured)


def _resolve_app_version() -> str:
    """Return the app version from env or default."""
    return os.getenv("LOST_APPLE_APP_VERSION", DEFAULT_APP_VERSION)


async def build_app() -> FastAPI:
    """Create and return the ASGI app for FastAPI startup."""
    storage = AppStorage(_resolve_database_path())
    await storage.initialize()
    app = create_app(
        storage=storage,
        pairing_token=resolve_pairing_token(dict(os.environ)),
        app_version=_resolve_app_version(),
    )
    register_web_routes(app)
    return app


def main() -> None:
    """Run the ASGI app with uvicorn in factory mode."""
    uvicorn.run(
        "lost_apple_app.__main__:build_app",
        host="0.0.0.0",  # noqa: S104
        port=8099,
        factory=True,
    )


if __name__ == "__main__":
    main()
