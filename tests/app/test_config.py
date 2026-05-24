"""Tests for Lost Apple App configuration loading."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
import pytest

if TYPE_CHECKING:
    from pathlib import Path

from lost_apple_app.__main__ import build_app
from lost_apple_app.config import resolve_pairing_token

AUTHORIZATION_HEADER = "Authorization"
HTTP_STATUS_OK = 200
HTTP_STATUS_UNAUTHORIZED = 401


def _write_options_file(path: Path, token: str) -> None:
    """Persist the options payload to disk for the tested path."""
    with path.open("w", encoding="utf-8") as stream:
        json.dump({"pairing_token": token}, stream)


def _make_auth_headers(token: str) -> dict[str, str]:
    """Create an Authorization header for Bearer-token requests."""
    return {AUTHORIZATION_HEADER: f"Bearer {token}"}


def _assert_equal(actual: object, expected: object, message: str) -> None:
    """Raise assertion failures with a message format consistent with project style."""
    if actual != expected:
        equality_error = message + " (got=" + repr(actual) + ", expected=" + repr(expected) + ")"
        raise AssertionError(equality_error)


def _assert_status(response_status: int, expected_status: int) -> None:
    """Validate response status with explicit assertion style."""
    if response_status != expected_status:
        status_error = (
            "Unexpected status code: " + str(response_status) + ", expected " + str(expected_status)
        )
        raise AssertionError(status_error)


def test_resolve_pairing_token_prefers_env_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit env token should override options-file content."""
    options_path = tmp_path / "options.json"
    _write_options_file(options_path, "ignored-token")
    monkeypatch.setenv("LOST_APPLE_OPTIONS_PATH", str(options_path))
    monkeypatch.setenv("LOST_APPLE_PAIRING_TOKEN", "env-token")

    resolved = resolve_pairing_token()
    _assert_equal(
        actual=resolved,
        expected="env-token",
        message="Env override should win over options file",
    )


def test_resolve_pairing_token_reads_options_file(tmp_path: Path) -> None:
    """Options JSON should supply the pairing token when env override is absent."""
    options_path = tmp_path / "options.json"
    _write_options_file(options_path, "options-token")
    environment = {"LOST_APPLE_OPTIONS_PATH": str(options_path)}

    resolved = resolve_pairing_token(environment)
    _assert_equal(
        actual=resolved,
        expected="options-token",
        message="Options file token should be used without env override",
    )


def test_resolve_pairing_token_rejects_blank_option(tmp_path: Path) -> None:
    """Blank pairing token values should be rejected from options."""
    options_path = tmp_path / "options.json"
    _write_options_file(options_path, "   ")
    environment = {"LOST_APPLE_OPTIONS_PATH": str(options_path)}

    with pytest.raises(ValueError, match="pairing_token must be a non-empty value"):
        resolve_pairing_token(environment)


@pytest.mark.anyio
async def test_build_app_uses_options_json_for_authentication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """build_app() should use options-configured token for API auth."""
    options_path = tmp_path / "options.json"
    _write_options_file(options_path, "auth-token")
    monkeypatch.setenv("LOST_APPLE_OPTIONS_PATH", str(options_path))
    monkeypatch.setenv("LOST_APPLE_DB", str(tmp_path / "lost_apple.sqlite3"))

    app = await build_app()
    client = TestClient(app)

    unauthorized = client.get("/api/v1/health")
    _assert_status(unauthorized.status_code, HTTP_STATUS_UNAUTHORIZED)

    wrong_token = client.get(
        "/api/v1/health",
        headers=_make_auth_headers("invalid"),
    )
    _assert_status(wrong_token.status_code, HTTP_STATUS_UNAUTHORIZED)

    valid = client.get(
        "/api/v1/health",
        headers=_make_auth_headers("auth-token"),
    )
    _assert_status(valid.status_code, HTTP_STATUS_OK)
