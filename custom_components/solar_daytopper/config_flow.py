from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from urllib.parse import urlparse
import aiohttp
import async_timeout
import logging
from .const import DOMAIN
from .utils import resolve_mdns_url

_LOGGER = logging.getLogger(__name__)
DEFAULT_HOST = "http://daytopper.local"

class DaytopperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Solar Daytopper config flow started")
        
        # Check if there's already a config entry
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
        
        errors = {}

        if user_input is not None:
            host = user_input["host"].rstrip("/")
            # Validate the host URL format
            if not self._is_valid_url(host):
                errors["host"] = "invalid_host"
            else:
                # Test connection with the provided address
                _LOGGER.debug("Starting connection test for: %s", host)
                connection_test = await self._test_connection(host)
                _LOGGER.debug("Connection test completed: %s", connection_test)
                if not connection_test:
                    errors["host"] = "cannot_connect"
                else:
                    # Make sure the host does not have a trailing slash
                    user_input["host"] = host
                    return self.async_create_entry(title="Solar Daytopper", data=user_input)

        schema = vol.Schema({
            vol.Required("host", default=DEFAULT_HOST): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    def _is_valid_url(self, url):
        """Validate if the URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    async def _test_connection(self, host):
        """Test the connection with the host."""
        _LOGGER.debug("Testing connection to: %s", host)

        # For .local hosts, try IP address resolution first
        test_url = host
        if ".local" in host:
            resolved_url = await resolve_mdns_url(host)
            if resolved_url:
                test_url = resolved_url
                _LOGGER.debug("Resolved %s to %s", host, test_url)
            else:
                _LOGGER.debug("Could not resolve mDNS for %s, trying original URL", host)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):  # Increase timeout for mDNS
                    async with session.get(test_url) as response:
                        _LOGGER.debug("Connection test result for %s: status %s", test_url, response.status)
                        return response.status < 400
        except Exception as err:
            _LOGGER.debug("Connection test failed for %s: %s", test_url, err)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DaytopperOptionsFlow()


class DaytopperOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            host = user_input["host"].rstrip("/")

            # Validate the host URL format
            if not self._is_valid_url(host):
                errors["host"] = "invalid_host"
            else:
                # Test connection with the provided address
                connection_test = await self._test_connection(host)
                if not connection_test:
                    errors["host"] = "cannot_connect"
                else:
                    # Update the config entry data instead of options
                    new_data = dict(self.config_entry.data)
                    new_data["host"] = host
                    
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, data=new_data
                    )
                    
                    # Reload the integration to apply new settings
                    await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                    
                    return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required("host", default=self.config_entry.data.get("host", DEFAULT_HOST)): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

    def _is_valid_url(self, url):
        """Validate if the URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    async def _test_connection(self, host):
        """Test the connection with the host."""
        _LOGGER.debug("Testing connection to: %s", host)

        # For .local hosts, try IP address resolution first
        test_url = host
        if ".local" in host:
            resolved_url = await resolve_mdns_url(host)
            if resolved_url:
                test_url = resolved_url
                _LOGGER.debug("Resolved %s to %s", host, test_url)
            else:
                _LOGGER.debug("Could not resolve mDNS for %s, trying original URL", host)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(10):  # Increase timeout for mDNS
                    async with session.get(test_url) as response:
                        _LOGGER.debug("Connection test result: status %s", response.status)
                        return response.status < 400
        except Exception as err:
            _LOGGER.debug("Connection test failed: %s", err)
            return False
