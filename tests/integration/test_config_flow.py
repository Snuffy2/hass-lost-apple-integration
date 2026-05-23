"""Tests for Lost Apple integration config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from custom_components.lost_apple.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def _assert_equal(actual: object, expected: object, message: str) -> None:
    """Raise an AssertionError when two values do not match."""
    if actual != expected:
        equality_error = (
            message
            + " (got="
            + repr(actual)
            + ", expected="
            + repr(expected)
            + ")"
        )
        raise AssertionError(equality_error)


async def test_config_flow_creates_entry(hass: HomeAssistant) -> None:
    """Config flow stores App URL and pairing token after health check."""
    with (
        patch(
            "custom_components.lost_apple.config_flow.async_get_clientsession",
            return_value=object(),
        ),
        patch(
            "custom_components.lost_apple.config_flow.LostAppleClient.health",
            AsyncMock(return_value={"api_version": 1, "app_version": "0.1.0"}),
        ),
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

    _assert_equal(
        actual=result["type"],
        expected="create_entry",
        message="Config flow should create an entry after a healthy API check",
    )
    _assert_equal(
        actual=result["title"],
        expected="Lost Apple",
        message="Config flow should use the fixed integration title",
    )
    _assert_equal(
        actual=result["data"],
        expected={
            "base_url": "http://localhost:8099",
            "pairing_token": "secret-token",
        },
        message="Config flow should persist the submitted connection settings",
    )
