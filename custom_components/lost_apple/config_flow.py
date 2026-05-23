"""Config flow for the Lost Apple integration."""

from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.lost_apple.api_client import LostAppleClient
from custom_components.lost_apple.const import CONF_BASE_URL, CONF_PAIRING_TOKEN, DOMAIN

DEFAULT_BASE_URL = "http://localhost:8099"


class LostAppleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Lost Apple config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, str] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle manual setup initiated by a user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = LostAppleClient(
                session=async_get_clientsession(self.hass),
                base_url=user_input[CONF_BASE_URL],
                token=user_input[CONF_PAIRING_TOKEN],
            )
            try:
                await client.health()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Lost Apple", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                    vol.Required(CONF_PAIRING_TOKEN): str,
                }
            ),
            errors=errors,
        )
