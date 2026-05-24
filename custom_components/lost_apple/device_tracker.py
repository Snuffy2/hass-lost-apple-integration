"""Device tracker platform for Lost Apple snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.core import callback

from custom_components.lost_apple.coordinator import LostAppleCoordinator
from custom_components.lost_apple.entity import LostAppleEntity, float_value, string_value

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


def _build_new_trackers(
    coordinator: LostAppleCoordinator,
    seen_ids: set[str],
) -> list[LostAppleDeviceTracker]:
    """Build tracker entities for newly discovered valid devices."""
    entities: list[LostAppleDeviceTracker] = []

    for device in coordinator.data:
        device_id = string_value(device, "id")
        device_name = string_value(device, "name")
        if device_id is None or device_name is None or device_id in seen_ids:
            continue
        seen_ids.add(device_id)
        entities.append(LostAppleDeviceTracker(coordinator, device_id, device_name))

    return entities


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry[LostAppleCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Lost Apple device tracker entities from a config entry."""
    coordinator = entry.runtime_data
    seen_ids: set[str] = set()
    async_add_entities(_build_new_trackers(coordinator, seen_ids))

    @callback
    def _async_add_new_trackers() -> None:
        """Add tracker entities for devices discovered after setup."""
        new_entities = _build_new_trackers(coordinator, seen_ids)
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_trackers))


class LostAppleDeviceTracker(LostAppleEntity, TrackerEntity):
    """Represent one tracked Apple Find My device."""

    _attr_source_type: str = "gps"  # type: ignore[assignment]

    def __init__(
        self,
        coordinator: LostAppleCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the Lost Apple tracker entity."""
        super().__init__(coordinator, device_id, device_name, "tracker")
        self._attr_name = device_name
        self._update_from_device()

    def _update_from_device(self) -> None:
        """Update tracker attributes from the current device snapshot."""
        self._attr_latitude = float_value(self._device, "latitude")
        self._attr_longitude = float_value(self._device, "longitude")
        self._attr_location_accuracy = float_value(self._device, "accuracy_m")  # type: ignore[assignment]
