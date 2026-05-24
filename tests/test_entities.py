"""Tests for Lost Apple entity platforms."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.lost_apple.const import DOMAIN
from custom_components.lost_apple.coordinator import LostAppleCoordinator
from tests.helpers import assert_equal, load_device_snapshot

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, State


def _build_snapshot(
    device_id: str,
    name: str,
    updates: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a Lost Apple device snapshot for integration tests."""
    snapshot = load_device_snapshot()
    snapshot["id"] = device_id
    snapshot["name"] = name
    if updates is not None:
        snapshot.update(updates)
    return snapshot


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

    assert_equal(
        actual=result["type"],
        expected="create_entry",
        message="Config flow should create a Lost Apple entry for entity setup tests",
    )
    entries = hass.config_entries.async_entries(DOMAIN)
    assert_equal(
        actual=len(entries),
        expected=1,
        message="Entity setup tests should create exactly one Lost Apple entry",
    )
    return entries[0]


async def _setup_entry_with_snapshot(hass: HomeAssistant) -> ConfigEntry:
    """Set up a Lost Apple config entry with one device snapshot."""
    snapshot = load_device_snapshot()
    entry = await _create_config_entry(hass, snapshot)
    setup_result = entry.state is ConfigEntryState.LOADED

    assert_equal(
        actual=setup_result,
        expected=True,
        message=("Lost Apple config entry should load during flow creation for entity tests"),
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
        message = f"Entity registry is missing {entity_domain} with unique ID {unique_id!r}"
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

    assert_equal(
        actual=state.name,
        expected="Keys",
        message="Lost Apple device tracker should use the snapshot device name",
    )
    assert_equal(
        actual=state.attributes["latitude"],
        expected=40.7128,
        message="Lost Apple device tracker should expose snapshot latitude",
    )
    assert_equal(
        actual=state.attributes["longitude"],
        expected=-74.006,
        message="Lost Apple device tracker should expose snapshot longitude",
    )
    assert_equal(
        actual=state.attributes["gps_accuracy"],
        expected=12.4,
        message="Lost Apple device tracker should expose snapshot GPS accuracy",
    )
    assert_equal(
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

    assert_equal(
        actual=state.name,
        expected="Keys Last Report",
        message="Lost Apple last report sensor should append a descriptive suffix",
    )
    assert_equal(
        actual=state.attributes["device_class"],
        expected="timestamp",
        message="Lost Apple last report sensor should use the timestamp device class",
    )
    assert_equal(
        actual=parsed_timestamp,
        expected=datetime(2026, 5, 23, 20, 30, tzinfo=UTC),
        message="Lost Apple last report sensor should parse the snapshot timestamp",
    )


async def test_entities_update_attributes_after_coordinator_refresh(
    hass: HomeAssistant,
) -> None:
    """Existing entities should refresh attributes from coordinator updates."""
    entry = await _setup_entry_with_snapshot(hass)
    coordinator: LostAppleCoordinator = entry.runtime_data
    updated_snapshot = _build_snapshot(
        "airtag-001",
        "Updated Keys",
        {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "accuracy_m": 5.25,
            "last_reported_at": "2026-05-23T21:15:00Z",
        },
    )

    coordinator.async_set_updated_data([updated_snapshot])
    await hass.async_block_till_done()

    tracker_state = _get_state_by_unique_id(
        hass,
        "device_tracker",
        "lost_apple_airtag-001_tracker",
    )
    sensor_state = _get_state_by_unique_id(
        hass,
        "sensor",
        "lost_apple_airtag-001_last_report",
    )
    parsed_timestamp = dt_util.parse_datetime(sensor_state.state)

    assert_equal(
        actual=tracker_state.attributes["latitude"],
        expected=34.0522,
        message="Tracker latitude should update from the latest snapshot",
    )
    assert_equal(
        actual=tracker_state.attributes["longitude"],
        expected=-118.2437,
        message="Tracker longitude should update from the latest snapshot",
    )
    assert_equal(
        actual=tracker_state.attributes["gps_accuracy"],
        expected=5.25,
        message="Tracker GPS accuracy should update from the latest snapshot",
    )
    assert_equal(
        actual=parsed_timestamp,
        expected=datetime(2026, 5, 23, 21, 15, tzinfo=UTC),
        message="Sensor timestamp should update from the latest snapshot",
    )


async def test_config_entry_uses_runtime_data_and_unloads_cleanly(
    hass: HomeAssistant,
) -> None:
    """Config entry setup should keep the coordinator in runtime_data only."""
    entry = await _setup_entry_with_snapshot(hass)

    assert_equal(
        actual=isinstance(entry.runtime_data, LostAppleCoordinator),
        expected=True,
        message=("Lost Apple config entry should expose its coordinator via runtime_data"),
    )
    assert_equal(
        actual=DOMAIN in hass.data,
        expected=False,
        message="Lost Apple integration should not store coordinators in hass.data",
    )

    unload_result = await hass.config_entries.async_unload(entry.entry_id)

    assert_equal(
        actual=unload_result,
        expected=True,
        message="Lost Apple config entry should unload cleanly",
    )
    assert_equal(
        actual=hasattr(entry, "runtime_data"),
        expected=False,
        message="Home Assistant should clear Lost Apple runtime_data after unload",
    )
    assert_equal(
        actual=DOMAIN in hass.data,
        expected=False,
        message="Lost Apple unload should leave hass.data clear for this domain",
    )


async def test_platforms_add_entities_for_new_devices_after_refresh(
    hass: HomeAssistant,
) -> None:
    """Coordinator refreshes should dynamically add entities for new devices."""
    entry = await _setup_entry_with_snapshot(hass)
    coordinator: LostAppleCoordinator = entry.runtime_data
    second_snapshot = _build_snapshot(
        "airtag-002",
        "Backpack",
        {
            "latitude": 41.8781,
            "longitude": -87.6298,
            "accuracy_m": 8.5,
            "last_reported_at": "2026-05-23T20:45:00Z",
            "last_polled_at": "2026-05-23T20:46:00Z",
        },
    )
    malformed_snapshot = {
        "id": "airtag-003",
        "latitude": 33.7488,
        "longitude": -84.3877,
    }
    duplicate_snapshot = dict(second_snapshot)

    coordinator.async_set_updated_data(
        [
            load_device_snapshot(),
            second_snapshot,
            malformed_snapshot,
            duplicate_snapshot,
        ]
    )
    await hass.async_block_till_done()

    second_tracker_state = _get_state_by_unique_id(
        hass,
        "device_tracker",
        "lost_apple_airtag-002_tracker",
    )
    second_sensor_state = _get_state_by_unique_id(
        hass,
        "sensor",
        "lost_apple_airtag-002_last_report",
    )
    entity_registry = er.async_get(hass)
    airtag_002_entities = [
        entry.entity_id
        for entry in entity_registry.entities.values()
        if entry.platform == DOMAIN and entry.unique_id.startswith("lost_apple_airtag-002_")
    ]

    assert_equal(
        actual=second_tracker_state.name,
        expected="Backpack",
        message="Coordinator refresh should register a tracker for a new device",
    )
    assert_equal(
        actual=second_sensor_state.name,
        expected="Backpack Last Report",
        message="Coordinator refresh should register a sensor for a new device",
    )
    assert_equal(
        actual=sorted(airtag_002_entities),
        expected=[
            "device_tracker.backpack",
            "sensor.backpack_last_report",
        ],
        message="Duplicate snapshots should create only one entity set for a device",
    )
    assert_equal(
        actual=entity_registry.async_get_entity_id(
            "device_tracker",
            DOMAIN,
            "lost_apple_airtag-003_tracker",
        ),
        expected=None,
        message="Malformed snapshots should not create tracker entities",
    )
    assert_equal(
        actual=entity_registry.async_get_entity_id(
            "sensor",
            DOMAIN,
            "lost_apple_airtag-003_last_report",
        ),
        expected=None,
        message="Malformed snapshots should not create sensor entities",
    )
