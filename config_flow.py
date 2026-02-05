"""Config flow for Ajax Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import AjaxCloudClient
from .const import CONF_BACKEND_URL, CONF_TOKEN, DEFAULT_BACKEND_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Optional(CONF_BACKEND_URL, default=DEFAULT_BACKEND_URL): str,
    }
)


class AjaxCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ajax Cloud."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._email: str | None = None
        self._backend_url: str | None = None
        self._token: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._backend_url = user_input[CONF_BACKEND_URL]

            try:
                # Request registration/authentication
                session = async_get_clientsession(self.hass)
                client = AjaxCloudClient(session, self._backend_url, "")
                result = await client.async_authenticate(self._email)
                
                self._token = result.get("token")
                
                if result.get("status") == "pending":
                    return await self.async_step_pending()
                elif result.get("status") == "approved":
                    return self.async_create_entry(
                        title=f"Ajax Cloud ({self._email})",
                        data={
                            CONF_EMAIL: self._email,
                            CONF_BACKEND_URL: self._backend_url,
                            CONF_TOKEN: self._token,
                        },
                    )
            except Exception as err:
                _LOGGER.error("Error during authentication: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_pending(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle pending approval step."""
        if user_input is not None:
            try:
                # Check if approved
                session = async_get_clientsession(self.hass)
                client = AjaxCloudClient(session, self._backend_url, self._token)
                result = await client.async_check_status()
                
                if result.get("status") == "approved":
                    return self.async_create_entry(
                        title=f"Ajax Cloud ({self._email})",
                        data={
                            CONF_EMAIL: self._email,
                            CONF_BACKEND_URL: self._backend_url,
                            CONF_TOKEN: self._token,
                        },
                    )
                elif result.get("status") == "rejected":
                    return self.async_abort(reason="rejected")
            except Exception as err:
                _LOGGER.error("Error checking status: %s", err)
                return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="pending",
            description_placeholders={
                "email": self._email,
                "message": "Your registration is pending approval. Please wait for the administrator to approve your access.",
            },
        )
