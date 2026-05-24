"""Sensor platform for Lost Apple diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from custom_components.lost_apple.coordinator import LostAppleCoordinator
from custom_components.lost_apple.entity import LostAppleEntity, parsed_timestamp, string_value

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


def _build_new_sensors(
    coordinator: LostAppleCoordinator,
    seen_ids: set[str],
) -> list[LastReportSensor]:
    """Build diagnostic sensors for newly discovered valid devices."""
    entities: list[LastReportSensor] = []

    for device in coordinator.data:
        device_id = string_value(device, "id")
        device_name = string_value(device, "name")
        if device_id is None or device_name is None or device_id in seen_ids:
            continue
        seen_ids.add(device_id)
        entities.append(LastReportSensor(coordinator, device_id, device_name))

    return entities


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry[LostAppleCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Lost Apple sensor entities from a config entry."""
    coordinator = entry.runtime_data
    seen_ids: set[str] = set()
    async_add_entities(_build_new_sensors(coordinator, seen_ids))

    @callback
    def _async_add_new_sensors() -> None:
        """Add sensor entities for devices discovered after setup."""
        new_entities = _build_new_sensors(coordinator, seen_ids)
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_sensors))


class LastReportSensor(LostAppleEntity, SensorEntity):
    """Represent the last-report timestamp for one Lost Apple device."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: LostAppleCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the Lost Apple last-report sensor."""
        super().__init__(coordinator, device_id, device_name, "last_report")
        self._attr_name = f"{device_name} Last Report"
        self._update_from_device()

    def _update_from_device(self) -> None:
        """Update sensor attributes from the current device snapshot."""
        self._attr_native_value = parsed_timestamp(self._device, "last_reported_at")
