"""Constants for the Ajax Cloud integration."""

DOMAIN = "ajax_cloud"

# Default backend URL (users can override during setup)
DEFAULT_BACKEND_URL = "https://ajax-backend.example.com"

# Configuration
CONF_BACKEND_URL = "backend_url"
CONF_TOKEN = "token"
CONF_EMAIL = "email"

# Device types
DEVICE_TYPE_HUB = "hub"
DEVICE_TYPE_MOTION = "motion_detector"
DEVICE_TYPE_DOOR = "door_sensor"
DEVICE_TYPE_LEAK = "leak_detector"
DEVICE_TYPE_FIRE = "fire_detector"
DEVICE_TYPE_TEMPERATURE = "temperature_sensor"

# Attributes
ATTR_BATTERY = "battery"
ATTR_SIGNAL_STRENGTH = "signal_strength"
ATTR_TAMPER = "tamper"
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
