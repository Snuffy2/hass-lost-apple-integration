"""Coordinator for Lost Apple device snapshots."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, cast

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.lost_apple.api_client import LostAppleClient
from custom_components.lost_apple.const import CONF_BASE_URL, CONF_PAIRING_TOKEN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class LostAppleCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Poll the Lost Apple App API for device snapshots."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Lost Apple coordinator."""
        self._client = LostAppleClient(
            session=async_get_clientsession(hass),
            base_url=cast("str", entry.data[CONF_BASE_URL]),
            token=cast("str", entry.data[CONF_PAIRING_TOKEN]),
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="Lost Apple devices",
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch the latest Lost Apple device snapshots."""
        return await self._client.devices()
