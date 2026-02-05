"""Ajax Cloud Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .api_client import AjaxCloudClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

UPDATE_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ajax Cloud from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize the API client
    session = async_get_clientsession(hass)
    client = AjaxCloudClient(
        session=session,
        backend_url=entry.data.get("backend_url", "https://your-backend.example.com"),
        token=entry.data["token"]
    )
    
    # Create coordinator for data updates
    coordinator = AjaxCloudCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    
    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class AjaxCloudCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ajax Cloud data."""

    def __init__(self, hass: HomeAssistant, client: AjaxCloudClient) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from API."""
        return await self.client.async_get_devices()
