"""Utility functions for Solar Daytopper integration."""
import socket
import logging
from urllib.parse import urlparse, urlunparse

_LOGGER = logging.getLogger(__name__)

async def resolve_mdns_url(url):
    """Try to resolve .local domain to IP address."""
    try:
        parsed = urlparse(url)
        
        if ".local" in parsed.hostname:
            # Probeer het hostname te resolven naar een IP
            try:
                ip = socket.gethostbyname(parsed.hostname)
                # Vervang hostname met IP in de URL
                new_netloc = parsed.netloc.replace(parsed.hostname, ip)
                resolved_url = urlunparse((
                    parsed.scheme,
                    new_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                _LOGGER.debug("Resolved %s to %s", url, resolved_url)
                return resolved_url
            except socket.gaierror:
                _LOGGER.debug("Failed to resolve hostname: %s", parsed.hostname)
                return None
        
        return url
    except Exception as err:
        _LOGGER.debug("Error resolving mDNS URL: %s", err)
        return None
