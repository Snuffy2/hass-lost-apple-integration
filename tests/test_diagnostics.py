"""Tests for Lost Apple integration diagnostics redaction."""

from __future__ import annotations

import pytest

from custom_components.lost_apple.diagnostics import redact_diagnostics
from tests.helpers import assert_equal

_REDACTION_KEYS = (
    "pairing_token",
    "token",
    "password",
    "apple_id",
    "session",
)


@pytest.mark.parametrize("key", _REDACTION_KEYS)
def test_redact_diagnostics_redacts_sensitive_top_level_value(key: str) -> None:
    """Sensitive keys should be redacted in top-level diagnostics payload."""
    payload = {key: "secret", "keep": "safe"}

    redacted = redact_diagnostics(payload)

    assert_equal(
        actual=redacted[key],
        expected="**REDACTED**",
        message="Top-level sensitive key should be redacted",
    )
    assert_equal(
        actual=redacted["keep"],
        expected="safe",
        message="Non-sensitive top-level keys should remain",
    )
    assert_equal(
        actual=payload[key],
        expected="secret",
        message="Input payload should stay unchanged",
    )


def test_redact_diagnostics_redacts_nested_and_list_values() -> None:
    """Diagnostics traversal should redact sensitive values in nested structures."""
    payload = {
        "pairing_token": "top-secret",
        "nested": {
            "token": "nested-secret",
            "ignored": {"session": "nested-session"},
        },
        "items": [
            {"password": "pw-1"},
            {"apple_id": "id-1"},
            {"session": "s-1"},
            {"keep": "ok"},
        ],
    }

    redacted = redact_diagnostics(payload)

    assert_equal(
        actual=redacted["pairing_token"],
        expected="**REDACTED**",
        message="Top-level pairing token should be redacted",
    )
    assert_equal(
        actual=redacted["nested"]["token"],
        expected="**REDACTED**",
        message="Nested token should be redacted",
    )
    assert_equal(
        actual=redacted["nested"]["ignored"]["session"],
        expected="**REDACTED**",
        message="Deeply nested session should be redacted",
    )
    assert_equal(
        actual=redacted["items"][0]["password"],
        expected="**REDACTED**",
        message="List item password should be redacted",
    )
    assert_equal(
        actual=redacted["items"][1]["apple_id"],
        expected="**REDACTED**",
        message="List item apple id should be redacted",
    )
    assert_equal(
        actual=redacted["items"][2]["session"],
        expected="**REDACTED**",
        message="List item session should be redacted",
    )
    assert_equal(
        actual=redacted["items"][3]["keep"],
        expected="ok",
        message="Non-sensitive list values should remain",
    )
