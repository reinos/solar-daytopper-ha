import aiohttp
import asyncio
import logging
from datetime import timedelta, datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .utils import resolve_mdns_url

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api_url = entry.data.get("host")

    if not api_url:
        _LOGGER.error("No host given for Daytopper.")
        raise ConfigEntryNotReady("No host address available.")

    async def async_update_data():
        _LOGGER.debug("Fetching data from: %s", api_url)
        
        # Resolve mDNS if needed
        fetch_url = await resolve_mdns_url(api_url)
        if fetch_url != api_url:
            _LOGGER.debug("Using resolved URL: %s", fetch_url)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(fetch_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    _LOGGER.debug("Received response with status: %s", response.status)
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Add timestamp when data was fetched
                    data["_last_update"] = datetime.now().isoformat()
                    
                    _LOGGER.debug("Successfully fetched data: %s keys", list(data.keys()) if isinstance(data, dict) else "non-dict data")
                    return data
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching data from Daytopper API (%s)", fetch_url)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP error fetching data from Daytopper API (%s): %s", fetch_url, err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error fetching data from Daytopper API (%s): %s", fetch_url, err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    _LOGGER.debug("Starting first refresh")
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("First refresh completed successfully")
    except Exception as err:
        _LOGGER.error("First refresh failed: %s", err)
        raise ConfigEntryNotReady from err

    _LOGGER.debug("Storing coordinator data")
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "host": api_url,
    }

    _LOGGER.debug("Setting up sensor platform")
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    # Set up config entry update listener
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    _LOGGER.debug("Solar Daytopper setup completed successfully")

    return True

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
