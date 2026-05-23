"""Device tracker platform for Lost Apple snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.lost_apple.const import DOMAIN
from custom_components.lost_apple.coordinator import LostAppleCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


def _string_value(device: dict[str, Any], key: str) -> str | None:
    """Return a string value from a device snapshot when present."""
    value = device.get(key)
    if isinstance(value, str) and value:
        return value
    return None


def _float_value(device: dict[str, Any], key: str) -> float | None:
    """Return a numeric value from a device snapshot as a float."""
    value = device.get(key)
    if isinstance(value, int | float):
        return float(value)
    return None


def _build_new_trackers(
    coordinator: LostAppleCoordinator,
    seen_ids: set[str],
) -> list[LostAppleDeviceTracker]:
    """Build tracker entities for newly discovered valid devices."""
    entities: list[LostAppleDeviceTracker] = []

    for device in coordinator.data:
        device_id = _string_value(device, "id")
        device_name = _string_value(device, "name")
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


class LostAppleDeviceTracker(CoordinatorEntity[LostAppleCoordinator], TrackerEntity):
    """Represent one tracked Apple Find My device."""

    _attr_source_type: str = "gps"  # type: ignore[assignment]

    def __init__(
        self,
        coordinator: LostAppleCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the Lost Apple tracker entity."""
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._fallback_name = device_name
        self._attr_unique_id = f"lost_apple_{device_id}_tracker"
        self._attr_name = device_name
        self._attr_device_info: DeviceInfo = DeviceInfo(  # type: ignore[assignment]
            identifiers={(DOMAIN, device_id)},
            name=device_name,
        )

    @property
    def latitude(self) -> float | None:
        """Return the latest device latitude."""
        device = self._current_device
        if device is None:
            return None
        return _float_value(device, "latitude")

    @property
    def location_accuracy(self) -> float | None:  # type: ignore[override]
        """Return the latest device location accuracy in meters."""
        device = self._current_device
        if device is None:
            return None
        return _float_value(device, "accuracy_m")

    @property
    def longitude(self) -> float | None:
        """Return the latest device longitude."""
        device = self._current_device
        if device is None:
            return None
        return _float_value(device, "longitude")

    @property
    def name(self) -> str:
        """Return the current device name."""
        device = self._current_device
        if device is None:
            return self._fallback_name
        return _string_value(device, "name") or self._fallback_name

    @property
    def _current_device(self) -> dict[str, Any] | None:
        """Return the current snapshot for this device."""
        for device in self.coordinator.data:
            if _string_value(device, "id") == self._device_id:
                return device
        return None
