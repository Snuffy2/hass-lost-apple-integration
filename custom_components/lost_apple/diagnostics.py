"""Diagnostics redaction helpers for Lost Apple integration payloads."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

_REDACTED_VALUE = "**REDACTED**"
_SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "pairing_token",
        "token",
        "password",
        "apple_id",
        "session",
    }
)


def _redact_payload_value(value: object) -> object:
    """Return a redacted copy of a diagnostics value."""
    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for key, inner_value in value.items():
            if isinstance(key, str) and key in _SENSITIVE_KEYS:
                redacted[key] = _REDACTED_VALUE
            elif isinstance(key, str):
                redacted[key] = _redact_payload_value(inner_value)
            else:
                redacted[repr(key)] = _redact_payload_value(inner_value)
        return redacted
    if isinstance(value, list):
        return [_redact_payload_value(inner) for inner in value]

    return value


def redact_diagnostics(payload: Mapping[str, object]) -> dict[str, Any]:
    """Return diagnostics payload with credentials scrubbed.

    Args:
        payload: The raw diagnostics payload from the integration.

    Returns:
        A copy of ``payload`` where sensitive key values are replaced with
        ``"**REDACTED**"``.

    """
    return cast("dict[str, Any]", _redact_payload_value(payload))
