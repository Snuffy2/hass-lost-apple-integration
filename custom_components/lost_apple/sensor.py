"""Sensor platform for Lost Apple diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from custom_components.lost_apple.const import DOMAIN
from custom_components.lost_apple.coordinator import LostAppleCoordinator

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


def _string_value(device: dict[str, Any], key: str) -> str | None:
    """Return a string value from a device snapshot when present."""
    value = device.get(key)
    if isinstance(value, str) and value:
        return value
    return None


def _parsed_timestamp(device: dict[str, Any], key: str) -> datetime | None:
    """Return a parsed UTC timestamp from a device snapshot."""
    value = _string_value(device, key)
    if value is None:
        return None
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    return dt_util.as_utc(parsed)


def _build_new_sensors(
    coordinator: LostAppleCoordinator,
    seen_ids: set[str],
) -> list[LastReportSensor]:
    """Build diagnostic sensors for newly discovered valid devices."""
    entities: list[LastReportSensor] = []

    for device in coordinator.data:
        device_id = _string_value(device, "id")
        device_name = _string_value(device, "name")
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


class LastReportSensor(CoordinatorEntity[LostAppleCoordinator], SensorEntity):
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
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._fallback_name = device_name
        self._attr_unique_id = f"lost_apple_{device_id}_last_report"
        self._attr_name = f"{device_name} Last Report"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
        )

    @property
    def name(self) -> str:
        """Return the current sensor name."""
        device = self._current_device
        if device is None:
            return f"{self._fallback_name} Last Report"
        device_name = _string_value(device, "name") or self._fallback_name
        return f"{device_name} Last Report"

    @property
    def native_value(self) -> datetime | None:
        """Return the latest parsed last-report timestamp."""
        device = self._current_device
        if device is None:
            return None
        return _parsed_timestamp(device, "last_reported_at")

    @property
    def _current_device(self) -> dict[str, Any] | None:
        """Return the current snapshot for this device."""
        for device in self.coordinator.data:
            if _string_value(device, "id") == self._device_id:
                return device
        return None
