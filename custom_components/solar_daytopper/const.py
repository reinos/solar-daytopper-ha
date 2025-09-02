from datetime import timedelta
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "solar_daytopper"
# The Daytopper module does fetch data every 5 minutes
# So we can also set this interval to 5 minutes as it make no sense to fetch data more often
SCAN_INTERVAL = timedelta(seconds=300)

# Main reading sensors - primary energy data
MAIN_SENSORS = [
    ("Solar Daytopper Current", ["solarReadingTotal", "current"], "W", "power", "measurement", 1, None),
    ("Solar Daytopper Total", ["solarReadingTotal", "total"], "kWh", "energy", "total_increasing", 1000, None),
]

# Diagnostic sensors - device and system information
DIAGNOSTIC_SENSORS = [
    ("Solar Daytopper WiFi Strength", ["system", "wifiStrengthRaw"], "dBm", "signal_strength", "measurement", 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper WiFi Status", ["system", "wifiStrength"], None, None, None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper Hostname", ["system", "wifiHostname"], None, None, None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper Uptime", ["system", "upSince"], None, "timestamp", None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper Last API Call", ["system", "lastApiCall"], None, "timestamp", None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper Firmware Version", ["system", "firmwareVersion"], None, None, None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper IP", ["system", "ip"], None, None, None, 1, EntityCategory.DIAGNOSTIC),
    ("Solar Daytopper Last Updated", ["_last_update"], None, "timestamp", None, 1, EntityCategory.DIAGNOSTIC),
]

# Template for dynamic inverter sensors
INVERTER_SENSOR_TEMPLATE = [
    ("Current", "current", "W", "power", "measurement", 1, None),
    ("Total", "total", "kWh", "energy", "total_increasing", 1000, None),
]