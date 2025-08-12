import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MAIN_SENSORS, SYSTEM_SENSORS, INVERTER_SENSOR_TEMPLATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Setting up Solar Daytopper sensors")
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host_url = hass.data[DOMAIN][entry.entry_id]["host"]

    entities = []
    
    # 1. Add main total sensors first
    _LOGGER.debug("Adding main total sensors")
    for name, path, unit, device_class, state_class, multiplier in MAIN_SENSORS:
        unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"
        entities.append(
            SolarDaytopperSensor(
                coordinator,
                name,
                path,
                unit,
                device_class,
                state_class,
                unique_id,
                multiplier,
                host_url,
            )
        )

    # 2. Add dynamic inverter sensors
    _LOGGER.debug("Checking for dynamic inverter sensors")
    if coordinator.data and "solarReadings" in coordinator.data:
        solar_readings = coordinator.data["solarReadings"]
        _LOGGER.debug("Found solarReadings data: %s", list(solar_readings.keys()))
        
        for inverter_name in solar_readings.keys():
            # Create sensors for each inverter
            for sensor_type, field, unit, device_class, state_class, multiplier in INVERTER_SENSOR_TEMPLATE:
                name = f"Solar Daytopper {inverter_name.title()} {sensor_type}"
                path = ["solarReadings", inverter_name, field]
                unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"
                
                entities.append(
                    SolarDaytopperSensor(
                        coordinator,
                        name,
                        path,
                        unit,
                        device_class,
                        state_class,
                        unique_id,
                        multiplier,
                        host_url,
                    )
                )
                
        _LOGGER.info("Created sensors for %d inverter(s): %s", 
                    len(solar_readings), list(solar_readings.keys()))
    else:
        _LOGGER.debug("No solarReadings data found or coordinator data is empty")

    # 3. Add system info sensors last
    _LOGGER.debug("Adding system info sensors")
    for name, path, unit, device_class, state_class, multiplier in SYSTEM_SENSORS:
        unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"
        entities.append(
            SolarDaytopperSensor(
                coordinator,
                name,
                path,
                unit,
                device_class,
                state_class,
                unique_id,
                multiplier,
                host_url,
            )
        )

    _LOGGER.debug("Adding %d entities to Home Assistant", len(entities))
    async_add_entities(entities, True)
    _LOGGER.debug("Solar Daytopper sensor setup completed")

class SolarDaytopperSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, path, unit, device_class, state_class, unique_id, multiplier, host_url=None):
        super().__init__(coordinator)
        self._attr_name = name
        self._path = path
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._multiplier = multiplier
        self._last_value = None 
        
        # Add device info
        system_data = coordinator.data.get("system", {}) if coordinator.data else {}
        chip_id = system_data.get("chipId", "solar_daytopper_default")
        _LOGGER.debug("Creating device with chipId: %s", chip_id)
        
        # Ensure proper URL format for configuration_url
        config_url = host_url
        if host_url and not host_url.startswith(('http://', 'https://')):
            config_url = f"http://{host_url}"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, chip_id)},
            name="Solar Daytopper",
            manufacturer="Solar Daytopper",
            model="Solar Monitor",
            sw_version=str(system_data.get("firmwareVersion", "Unknown")),
            configuration_url=config_url,
        ) 

    @property
    def native_value(self):
        data = self.coordinator.data
        try:
            # Special handling for the last update timestamp
            if self._path == ["_last_update"]:
                timestamp_str = data.get("_last_update")
                if timestamp_str:
                    try:
                        # Parse the ISO string and add timezone info
                        dt = datetime.fromisoformat(timestamp_str)
                        # If no timezone info, assume local timezone
                        if dt.tzinfo is None:
                            dt = dt_util.as_local(dt)
                        return dt
                    except ValueError as err:
                        _LOGGER.warning("Error parsing timestamp %s: %s", timestamp_str, err)
                        return None
                return None
            
            for key in self._path:
                data = data.get(key, {})

            if isinstance(data, (int, float)):
                value = data / self._multiplier if self._multiplier else data

                # For total_increasing sensors: ensure the value never decreases
                if self._attr_state_class == "total_increasing":
                    # If the new value is 0 and we had a previous value, keep the old value
                    if value == 0 and self._last_value not in (None, 0):
                        _LOGGER.debug("Total sensor %s: value is 0, keeping last value %s", self._attr_name, self._last_value)
                        return self._last_value

                    # If the new value is lower than the previous value, keep the old value
                    if self._last_value is not None and value < self._last_value:
                        _LOGGER.debug("Total sensor %s: new value %s is lower than previous %s, keeping previous", 
                                    self._attr_name, value, self._last_value)
                        return self._last_value

                # Update the last_value for all numeric sensors
                self._last_value = value
                return value

            return data

        except Exception as err:
            _LOGGER.warning("Error accessing sensor path %s: %s", self._path, err)
            return None
