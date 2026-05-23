"""Tests for Lost Apple integration config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from homeassistant.helpers.selector import TextSelector

from custom_components.lost_apple.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
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


async def _create_config_entry(hass: HomeAssistant) -> ConfigEntry:
    """Create a Lost Apple config entry through the user flow."""
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
    entries = hass.config_entries.async_entries(DOMAIN)
    _assert_equal(
        actual=len(entries),
        expected=1,
        message="Successful flow should create exactly one Lost Apple config entry",
    )
    return entries[0]


async def test_config_flow_creates_entry(hass: HomeAssistant) -> None:
    """Config flow stores App URL and pairing token after health check."""
    entry = await _create_config_entry(hass)
    result = {
        "type": "create_entry",
        "title": entry.title,
        "data": dict(entry.data),
    }

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


async def test_config_entry_setup_succeeds_before_platforms_exist(
    hass: HomeAssistant,
) -> None:
    """Config entry setup should succeed even before platform modules are added."""
    entry = await _create_config_entry(hass)
    unload_result = await hass.config_entries.async_unload(entry.entry_id)

    setup_result = await hass.config_entries.async_setup(entry.entry_id)

    _assert_equal(
        actual=unload_result,
        expected=True,
        message="Lost Apple config entry should unload cleanly before re-setup",
    )
    _assert_equal(
        actual=setup_result,
        expected=True,
        message="Lost Apple config entry setup should succeed without platforms",
    )


async def test_config_flow_returns_invalid_response_error_for_bad_health_payload(
    hass: HomeAssistant,
) -> None:
    """Config flow should show a form error when the App health response is invalid."""
    with (
        patch(
            "custom_components.lost_apple.config_flow.async_get_clientsession",
            return_value=object(),
        ),
        patch(
            "custom_components.lost_apple.config_flow.LostAppleClient.health",
            AsyncMock(side_effect=TypeError("bad payload shape")),
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
        expected="form",
        message="Invalid App health data should keep the user on the form step",
    )
    _assert_equal(
        actual=result["errors"],
        expected={"base": "invalid_response"},
        message="Invalid App health data should show an invalid response error",
    )


async def test_config_flow_uses_password_selector_for_pairing_token(
    hass: HomeAssistant,
) -> None:
    """Config flow should render the pairing token as a password field."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )

    data_schema = result["data_schema"]
    selector = data_schema.schema["pairing_token"]

    _assert_equal(
        actual=isinstance(selector, TextSelector),
        expected=True,
        message="Pairing token field should use a text selector",
    )
    _assert_equal(
        actual=selector.serialize(),
        expected={
            "selector": {
                "text": {
                    "type": "password",
                    "multiline": False,
                    "multiple": False,
                }
            }
        },
        message="Pairing token selector should render as a password input",
    )
