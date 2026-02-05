"""Binary sensor platform for Ajax Cloud."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BATTERY,
    ATTR_SIGNAL_STRENGTH,
    ATTR_TAMPER,
    DEVICE_TYPE_DOOR,
    DEVICE_TYPE_FIRE,
    DEVICE_TYPE_LEAK,
    DEVICE_TYPE_MOTION,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ajax Cloud binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    devices = coordinator.data.get("devices", [])
    
    for device in devices:
        device_type = device.get("type")
        if device_type in [DEVICE_TYPE_MOTION, DEVICE_TYPE_DOOR, DEVICE_TYPE_LEAK, DEVICE_TYPE_FIRE]:
            entities.append(AjaxBinarySensor(coordinator, device))
    
    async_add_entities(entities)


class AjaxBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Ajax binary sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device: dict[str, Any]) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ajax_{device['type']}_{device['id']}"
        self._attr_name = device.get("name", f"Ajax {device['type']}")
        
        # Set device class based on type
        device_type = device.get("type")
        if device_type == DEVICE_TYPE_MOTION:
            self._attr_device_class = BinarySensorDeviceClass.MOTION
        elif device_type == DEVICE_TYPE_DOOR:
            self._attr_device_class = BinarySensorDeviceClass.DOOR
        elif device_type == DEVICE_TYPE_LEAK:
            self._attr_device_class = BinarySensorDeviceClass.MOISTURE
        elif device_type == DEVICE_TYPE_FIRE:
            self._attr_device_class = BinarySensorDeviceClass.SMOKE

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return None
            
        return device.get("state", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return {}
        
        attributes = {}
        
        if ATTR_BATTERY in device:
            attributes[ATTR_BATTERY] = device[ATTR_BATTERY]
        if ATTR_SIGNAL_STRENGTH in device:
            attributes[ATTR_SIGNAL_STRENGTH] = device[ATTR_SIGNAL_STRENGTH]
        if ATTR_TAMPER in device:
            attributes[ATTR_TAMPER] = device[ATTR_TAMPER]
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        return device is not None and device.get("online", False)
