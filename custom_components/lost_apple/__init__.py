"""Lost Apple integration setup for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from homeassistant.const import Platform

from custom_components.lost_apple.coordinator import LostAppleCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: Final[tuple[Platform, ...]] = (
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[LostAppleCoordinator],
) -> bool:
    """Set up Lost Apple from a config entry."""
    coordinator = LostAppleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[LostAppleCoordinator],
) -> bool:
    """Unload a Lost Apple config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
