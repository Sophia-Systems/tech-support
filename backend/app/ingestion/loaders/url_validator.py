"""URL validation to prevent SSRF attacks."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from app.core.exceptions import CSBotError


class SSRFError(CSBotError):
    """Raised when a URL targets a private/reserved network address."""


def validate_url(url: str) -> str:
    """Validate that a URL is safe to fetch (no private/reserved IPs).

    Returns the validated URL string.
    Raises SSRFError if the URL targets a private or reserved address.
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Unsupported URL scheme: {parsed.scheme!r}")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError(f"No hostname in URL: {url}")

    try:
        resolved = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SSRFError(f"DNS resolution failed for {hostname}: {exc}") from exc

    for _family, _, _, _, sockaddr in resolved:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_reserved or ip.is_loopback or ip.is_link_local:
            raise SSRFError(
                f"URL {url} resolves to private/reserved address: {ip}"
            )

    return url
