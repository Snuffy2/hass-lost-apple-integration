"""Lost Apple integration setup for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: Final[tuple[str, ...]] = ()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lost Apple from a config entry."""
    if not PLATFORMS:
        return True
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Lost Apple config entry."""
    if not PLATFORMS:
        return True
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
