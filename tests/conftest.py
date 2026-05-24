"""Shared pytest fixtures for Home Assistant integration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant import bootstrap, loader
from homeassistant.core import HomeAssistant
import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path


@pytest.fixture
async def hass(tmp_path: Path) -> AsyncIterator[HomeAssistant]:
    """Create a minimal Home Assistant instance for config flow tests."""
    hass = HomeAssistant(str(tmp_path))
    loader.async_setup(hass)
    configured = await bootstrap.async_from_config_dict({"homeassistant": {}}, hass)
    if configured is None:
        message = "Home Assistant bootstrap failed"
        raise RuntimeError(message)
    await hass.async_start()
    try:
        yield hass
    finally:
        for entry in list(hass.config_entries.async_entries()):
            await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        await hass.async_stop()
