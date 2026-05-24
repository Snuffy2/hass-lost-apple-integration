"""Shared test utilities for Lost Apple tests."""

from __future__ import annotations

import json
from pathlib import Path

_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "device_snapshot.json"


def assert_equal(actual: object, expected: object, message: str) -> None:
    """Raise an AssertionError when two values do not match."""
    if actual != expected:
        equality_error = message + " (got=" + repr(actual) + ", expected=" + repr(expected) + ")"
        raise AssertionError(equality_error)


def load_device_snapshot() -> dict[str, object]:
    """Load the shared Lost Apple device snapshot fixture."""
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        message = "Device snapshot fixture must decode to an object"
        raise TypeError(message)
    return payload
