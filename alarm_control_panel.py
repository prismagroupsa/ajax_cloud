"""Alarm control panel platform for Ajax Cloud."""
from __future__ import annotations

from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ajax Cloud alarm control panels."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = []
    devices = coordinator.data.get("devices", [])
    
    for device in devices:
        if device.get("type") == "hub":
            entities.append(AjaxAlarmControlPanel(coordinator, client, device))
    
    async_add_entities(entities)


class AjaxAlarmControlPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of an Ajax alarm control panel."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
    )

    def __init__(self, coordinator, client, device: dict[str, Any]) -> None:
        """Initialize the alarm control panel."""
        super().__init__(coordinator)
        self._client = client
        self._device = device
        self._attr_unique_id = f"ajax_hub_{device['id']}"
        self._attr_name = device.get("name", "Ajax Hub")

    @property
    def state(self) -> str | None:
        """Return the state of the alarm."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return None
            
        mode = device.get("mode", "disarmed")
        
        if mode == "armed_away":
            return STATE_ALARM_ARMED_AWAY
        elif mode == "armed_home":
            return STATE_ALARM_ARMED_HOME
        elif mode == "armed_night":
            return STATE_ALARM_ARMED_NIGHT
        else:
            return STATE_ALARM_DISARMED

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self._client.async_disarm_alarm(self._device["id"])
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self._client.async_arm_alarm(self._device["id"], "armed_home")
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self._client.async_arm_alarm(self._device["id"], "armed_away")
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        await self._client.async_arm_alarm(self._device["id"], "armed_night")
        await self.coordinator.async_request_refresh()
