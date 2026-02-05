"""Sensor platform for Ajax Cloud."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_SIGNAL_STRENGTH, DEVICE_TYPE_TEMPERATURE, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ajax Cloud sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    devices = coordinator.data.get("devices", [])
    
    for device in devices:
        # Temperature sensors
        if device.get("type") == DEVICE_TYPE_TEMPERATURE or "temperature" in device:
            entities.append(AjaxTemperatureSensor(coordinator, device))
        
        # Battery sensors for all battery-powered devices
        if "battery" in device:
            entities.append(AjaxBatterySensor(coordinator, device))
        
        # Humidity sensors
        if "humidity" in device:
            entities.append(AjaxHumiditySensor(coordinator, device))
    
    async_add_entities(entities)


class AjaxTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Ajax temperature sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, device: dict[str, Any]) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ajax_temperature_{device['id']}"
        self._attr_name = f"{device.get('name', 'Ajax')} Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the temperature."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return None
            
        return device.get("temperature")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        return device is not None and device.get("online", False)


class AjaxBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of an Ajax battery sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, device: dict[str, Any]) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ajax_battery_{device['id']}"
        self._attr_name = f"{device.get('name', 'Ajax')} Battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return None
            
        return device.get("battery")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return {}
        
        attributes = {}
        if ATTR_SIGNAL_STRENGTH in device:
            attributes[ATTR_SIGNAL_STRENGTH] = device[ATTR_SIGNAL_STRENGTH]
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        return device is not None and device.get("online", False)


class AjaxHumiditySensor(CoordinatorEntity, SensorEntity):
    """Representation of an Ajax humidity sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, device: dict[str, Any]) -> None:
        """Initialize the humidity sensor."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ajax_humidity_{device['id']}"
        self._attr_name = f"{device.get('name', 'Ajax')} Humidity"

    @property
    def native_value(self) -> float | None:
        """Return the humidity."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        
        if not device:
            return None
            
        return device.get("humidity")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        devices = self.coordinator.data.get("devices", [])
        device = next((d for d in devices if d["id"] == self._device["id"]), None)
        return device is not None and device.get("online", False)
