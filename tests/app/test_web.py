"""Tests for web-facing routes in the Lost Apple App."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from pathlib import Path

from lost_apple_app.__main__ import build_app
from lost_apple_app.web import HACS_INSTALL_URL

HTTP_STATUS_OK = 200


def _make_expected_fragments() -> tuple[str, str, str]:
    """Return response body fragments used in setup-page assertions."""
    return (
        "Lost Apple",
        "Install through HACS",
        "My Home Assistant",
    )


def _assert_status_and_markup(response_text: str, response_status: int) -> None:
    """Validate setup response status and required markup fragments."""
    if response_status != HTTP_STATUS_OK:
        status_error = (
            f"Setup route should return HTTP 200. Got {response_status!r} instead."
        )
        raise AssertionError(status_error)

    for fragment in _make_expected_fragments():
        if fragment not in response_text:
            fragment_error = f"Setup page body is missing required fragment: {fragment}"
            raise AssertionError(fragment_error)

    if HACS_INSTALL_URL not in response_text:
        install_error = "Setup page should include the HACS install URL."
        raise AssertionError(install_error)


@pytest.mark.anyio
async def test_setup_page_returns_install_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The setup page should be readable without pairing token headers."""
    monkeypatch.setenv("LOST_APPLE_DB", str(tmp_path / "lost_apple.sqlite3"))
    monkeypatch.setenv("LOST_APPLE_PAIRING_TOKEN", "test-token")

    app = await build_app()
    client = TestClient(app)

    response = client.get("/setup")

    _assert_status_and_markup(
        response_text=response.text,
        response_status=response.status_code,
    )
