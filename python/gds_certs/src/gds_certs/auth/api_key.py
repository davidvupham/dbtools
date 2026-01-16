"""
API Key authentication for CA API clients.
"""

import httpx

from gds_certs.auth.base import BaseAuth


class APIKeyAuth(BaseAuth):
    """
    API Key authentication strategy.

    Adds an API key to requests via a configurable header.

    Example:
        >>> auth = APIKeyAuth(api_key="your-api-key")
        >>> client = CAClient(base_url="https://ca.example.com", auth=auth)

        >>> # Custom header name
        >>> auth = APIKeyAuth(api_key="your-api-key", header_name="Authorization")
    """

    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        """
        Initialize API Key authentication.

        Args:
            api_key: The API key value.
            header_name: The header name to use (default: X-API-Key).
        """
        self.api_key = api_key
        self.header_name = header_name

    def apply(self, request: httpx.Request) -> httpx.Request:
        """Apply API key header to request."""
        request.headers[self.header_name] = self.api_key
        return request
