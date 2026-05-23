"""Web routes for the Lost Apple App."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.responses import HTMLResponse

HACS_INSTALL_URL = (
    "https://my.home-assistant.io/redirect/hacs_repository/"
    "?owner=snuffy2&repository=hass-lost-apple&category=integration"
)

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_web_routes(app: FastAPI) -> None:
    """Register web setup routes on the given FastAPI app."""

    @app.get("/setup", response_class=HTMLResponse)
    async def setup() -> str:
        """Return a small setup page that links to the HACS repository."""
        return (
            "<!doctype html>"
            '<html lang="en">'
            "<head>"
            '<meta charset="utf-8">'
            "<title>Lost Apple Setup</title>"
            "</head>"
            "<body>"
            "<h1>Lost Apple</h1>"
            "<p>Complete setup using the My Home Assistant flow.</p>"
            f'<a href="{HACS_INSTALL_URL}">Install through HACS</a>'
            "</body>"
            "</html>"
        )
