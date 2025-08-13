from datetime import timedelta

DOMAIN = "solar_daytopper"
# The Daytopper module does fetch data every 5 minutes
# So we can also set this interval to 5 minutes as it make no sense to fetch data more often
SCAN_INTERVAL = timedelta(seconds=300)

# Main totals first
MAIN_SENSORS = [
    ("Solar Daytopper Current", ["solarReadingTotal", "current"], "W", "power", "measurement", 1),
    ("Solar Daytopper Total", ["solarReadingTotal", "total"], "kWh", "energy", "total_increasing", 1000),
]

# System info sensors last
SYSTEM_SENSORS = [
    ("Solar Daytopper WiFi Strength", ["system", "wifiStrengthRaw"], "dBm", "signal_strength", "measurement", 1),
    ("Solar Daytopper WiFi Status", ["system", "wifiStrength"], None, None, None, 1),
    ("Solar Daytopper Hostname", ["system", "wifiHostname"], None, None, None, 1),
    ("Solar Daytopper Uptime", ["system", "upSince"], None, "timestamp", None, 1),
    ("Solar Daytopper Last API Call", ["system", "lastApiCall"], None, "timestamp", None, 1),
    ("Solar Daytopper Firmware Version", ["system", "firmwareVersion"], None, None, None, 1),
    ("Solar Daytopper IP", ["system", "ip"], None, None, None, 1),
    ("Solar Daytopper Last Updated", ["_last_update"], None, "timestamp", None, 1),
]

# Template for dynamic inverter sensors
INVERTER_SENSOR_TEMPLATE = [
    ("Current", "current", "W", "power", "measurement", 1),
    ("Total", "total", "kWh", "energy", "total_increasing", 1000),
]