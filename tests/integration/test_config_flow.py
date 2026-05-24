"""Tests for Lost Apple integration config flow."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, cast
from unittest.mock import AsyncMock, patch

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import TextSelector

from custom_components.lost_apple.const import DOMAIN
from tests.helpers import assert_equal, load_device_snapshot

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class DataSchema(Protocol):
    """Config-flow data schema object with a selector mapping."""

    schema: Mapping[str, object]


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
        patch(
            "custom_components.lost_apple.api_client.LostAppleClient.devices",
            AsyncMock(return_value=[]),
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

    assert_equal(
        actual=result["type"],
        expected="create_entry",
        message="Config flow should create an entry after a healthy API check",
    )
    entries = hass.config_entries.async_entries(DOMAIN)
    assert_equal(
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

    assert_equal(
        actual=result["type"],
        expected="create_entry",
        message="Config flow should create an entry after a healthy API check",
    )
    assert_equal(
        actual=result["title"],
        expected="Lost Apple",
        message="Config flow should use the fixed integration title",
    )
    assert_equal(
        actual=result["data"],
        expected={
            "base_url": "http://localhost:8099",
            "pairing_token": "secret-token",
        },
        message="Config flow should persist the submitted connection settings",
    )


async def test_config_entry_setup_registers_entity_platforms(
    hass: HomeAssistant,
) -> None:
    """Config entry setup should load Lost Apple entity platforms."""
    entry = await _create_config_entry(hass)
    unload_result = await hass.config_entries.async_unload(entry.entry_id)

    with patch(
        "custom_components.lost_apple.api_client.LostAppleClient.devices",
        AsyncMock(return_value=[load_device_snapshot()]),
    ):
        setup_result = await hass.config_entries.async_setup(entry.entry_id)

    entity_registry = er.async_get(hass)
    tracker_entity_id = entity_registry.async_get_entity_id(
        "device_tracker",
        DOMAIN,
        "lost_apple_airtag-001_tracker",
    )
    sensor_entity_id = entity_registry.async_get_entity_id(
        "sensor",
        DOMAIN,
        "lost_apple_airtag-001_last_report",
    )

    assert_equal(
        actual=unload_result,
        expected=True,
        message="Lost Apple config entry should unload cleanly before re-setup",
    )
    assert_equal(
        actual=setup_result,
        expected=True,
        message="Lost Apple config entry setup should succeed with entity platforms",
    )
    assert_equal(
        actual=tracker_entity_id is not None,
        expected=True,
        message="Config entry setup should register a Lost Apple device tracker entity",
    )
    assert_equal(
        actual=sensor_entity_id is not None,
        expected=True,
        message="Config entry setup should register a Lost Apple sensor entity",
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

    assert_equal(
        actual=result["type"],
        expected="form",
        message="Invalid App health data should keep the user on the form step",
    )
    assert_equal(
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

    data_schema = cast("DataSchema", result["data_schema"])
    selector = cast("TextSelector", data_schema.schema["pairing_token"])

    assert_equal(
        actual=isinstance(selector, TextSelector),
        expected=True,
        message="Pairing token field should use a text selector",
    )
    assert_equal(
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
