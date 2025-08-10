# Solar Daytopper Home Assistant Integration

This Home Assistant integration connects your Solar Daytopper device to Home Assistant, allowing you to monitor your solar panel data directly in your smart home dashboard.

## About Solar Daytopper

With the Solar Daytopper module and accompanying app, you can compare the output of your solar panels with that of others. Through our unique system, you will find yourself in a real game of generating solar energy (gamification of your solar panels). You can earn badges, score points, and level up to ultimately become the daily or weekly winner. Do you have a smaller system than someone else? No problem, our system takes that into account, so you can still score enough points to become the weekly winner even with a smaller system.

## Features

This integration provides sensors for:
- **Individual inverter data**: Current power and total energy for each connected inverter (Solax, Enphase, etc.)
- **Total solar production**: Combined current power and total energy from all inverters
- **System information**: WiFi strength, IP address, hostname, uptime, and firmware version

## Installation

### Via HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations" 
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/reinos/solar-daytopper-hacs`
6. Select "Integration" as category
7. Click "Add"
8. Find "Solar Daytopper" in the integration list and install it

### Manual Installation
1. Copy the `custom_components/solar_daytopper` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Solar Daytopper" and add it

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Solar Daytopper"
3. Enter your Solar Daytopper device IP address (e.g., `http://192.168.1.100`)
4. The integration will automatically detect all connected inverters and create sensors

## Sensors Created

The integration automatically creates sensors based on your setup:

### System Sensors
- `Solar Daytopper Current` - Total current power production (W)
- `Solar Daytopper Total` - Total energy produced (kWh)
- `Solar Daytopper WiFi Strength` - WiFi signal strength (dBm)
- `Solar Daytopper Hostname` - Device hostname
- `Solar Daytopper IP` - Device IP address
- `Solar Daytopper Uptime` - Device uptime
- `Solar Daytopper Firmware Version` - Firmware version

### Dynamic Inverter Sensors
For each connected inverter (e.g., Solax, Enphase):
- `Solar [Inverter] Current` - Current power production (W)
- `Solar [Inverter] Total` - Total energy produced (kWh)

## Support

For issues related to this Home Assistant integration, please use the [GitHub Issues](https://github.com/reinos/solar-daytopper-hacs/issues).

For questions about the Solar Daytopper device itself, visit [solar-daytopper.nl](https://www.solar-daytopper.com/faq/connecting-to-home-assistant).