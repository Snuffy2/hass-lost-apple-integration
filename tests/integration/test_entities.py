"""Tests for Lost Apple entity platforms."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.lost_apple.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, State

_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "device_snapshot.json"
)


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


def _load_device_snapshot() -> dict[str, object]:
    """Load the shared Lost Apple device snapshot fixture."""
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        message = "Device snapshot fixture must decode to an object"
        raise TypeError(message)
    return payload


async def _create_config_entry(
    hass: HomeAssistant,
    snapshot: dict[str, object],
) -> ConfigEntry:
    """Create and set up a Lost Apple config entry through the user flow."""
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
            AsyncMock(return_value=[snapshot]),
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
        message="Config flow should create a Lost Apple entry for entity setup tests",
    )
    entries = hass.config_entries.async_entries(DOMAIN)
    _assert_equal(
        actual=len(entries),
        expected=1,
        message="Entity setup tests should create exactly one Lost Apple entry",
    )
    return entries[0]


async def _setup_entry_with_snapshot(hass: HomeAssistant) -> ConfigEntry:
    """Set up a Lost Apple config entry with one device snapshot."""
    snapshot = _load_device_snapshot()
    entry = await _create_config_entry(hass, snapshot)
    setup_result = entry.state is ConfigEntryState.LOADED

    _assert_equal(
        actual=setup_result,
        expected=True,
        message=(
            "Lost Apple config entry should load during flow creation "
            "for entity tests"
        ),
    )
    return entry


def _get_state_by_unique_id(
    hass: HomeAssistant,
    entity_domain: str,
    unique_id: str,
) -> State:
    """Return an entity state by unique ID or raise an AssertionError."""
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(entity_domain, DOMAIN, unique_id)
    if entity_id is None:
        message = (
            "Entity registry is missing "
            f"{entity_domain} with unique ID {unique_id!r}"
        )
        raise AssertionError(message)

    state = hass.states.get(entity_id)
    if state is None:
        message = f"Home Assistant state machine is missing entity {entity_id!r}"
        raise AssertionError(message)
    return state


async def test_device_tracker_exposes_coordinates_from_snapshot(
    hass: HomeAssistant,
) -> None:
    """Device tracker entity should expose the latest GPS snapshot details."""
    await _setup_entry_with_snapshot(hass)

    state = _get_state_by_unique_id(
        hass,
        "device_tracker",
        "lost_apple_airtag-001_tracker",
    )

    _assert_equal(
        actual=state.name,
        expected="Keys",
        message="Lost Apple device tracker should use the snapshot device name",
    )
    _assert_equal(
        actual=state.attributes["latitude"],
        expected=40.7128,
        message="Lost Apple device tracker should expose snapshot latitude",
    )
    _assert_equal(
        actual=state.attributes["longitude"],
        expected=-74.006,
        message="Lost Apple device tracker should expose snapshot longitude",
    )
    _assert_equal(
        actual=state.attributes["gps_accuracy"],
        expected=12.4,
        message="Lost Apple device tracker should expose snapshot GPS accuracy",
    )
    _assert_equal(
        actual=state.attributes["source_type"],
        expected="gps",
        message="Lost Apple device tracker should report a GPS source type",
    )


async def test_last_report_sensor_exposes_timestamp_from_snapshot(
    hass: HomeAssistant,
) -> None:
    """Last report sensor should parse and expose the latest timestamp."""
    await _setup_entry_with_snapshot(hass)

    state = _get_state_by_unique_id(
        hass,
        "sensor",
        "lost_apple_airtag-001_last_report",
    )
    parsed_timestamp = dt_util.parse_datetime(state.state)

    _assert_equal(
        actual=state.name,
        expected="Keys Last Report",
        message="Lost Apple last report sensor should append a descriptive suffix",
    )
    _assert_equal(
        actual=state.attributes["device_class"],
        expected="timestamp",
        message="Lost Apple last report sensor should use the timestamp device class",
    )
    _assert_equal(
        actual=parsed_timestamp,
        expected=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
        message="Lost Apple last report sensor should parse the snapshot timestamp",
    )
