"""Base entity helpers for the Lost Apple Integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from custom_components.lost_apple.const import DOMAIN
from custom_components.lost_apple.coordinator import LostAppleCoordinator

if TYPE_CHECKING:
    from datetime import datetime


def float_value(device: dict[str, Any] | None, key: str) -> float | None:
    """Return a numeric value from a device snapshot as a float."""
    if device is None:
        return None
    value = device.get(key)
    if isinstance(value, int | float):
        return float(value)
    return None


def parsed_timestamp(device: dict[str, Any] | None, key: str) -> datetime | None:
    """Return a parsed UTC timestamp from a device snapshot."""
    value = string_value(device, key)
    if value is None:
        return None
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    return dt_util.as_utc(parsed)


def string_value(device: dict[str, Any] | None, key: str) -> str | None:
    """Return a string value from a device snapshot when present."""
    if device is None:
        return None
    value = device.get(key)
    if isinstance(value, str) and value:
        return value
    return None


class LostAppleEntity(CoordinatorEntity[LostAppleCoordinator]):
    """Base entity for one Lost Apple device snapshot."""

    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LostAppleCoordinator,
        device_id: str,
        device_name: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize a Lost Apple entity."""
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._fallback_name = device_name
        self._device = self._device_from_coordinator()
        self._attr_unique_id = f"lost_apple_{device_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
        )

    def _device_from_coordinator(self) -> dict[str, Any] | None:
        """Return the current snapshot for this entity's device."""
        for device in self.coordinator.data:
            if string_value(device, "id") == self._device_id:
                return device
        return None

    def _handle_coordinator_update(self) -> None:
        """Update entity attributes from the latest coordinator data."""
        self._device = self._device_from_coordinator()
        self._update_from_device()
        super()._handle_coordinator_update()

    def _update_from_device(self) -> None:
        """Update entity-specific attributes from the current device snapshot."""
