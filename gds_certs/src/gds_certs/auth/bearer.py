"""
Bearer token authentication for CA API clients.
"""

import httpx

from gds_certs.auth.base import BaseAuth


class BearerAuth(BaseAuth):
    """
    Bearer token authentication strategy.

    Adds a Bearer token to the Authorization header.

    Example:
        >>> auth = BearerAuth(token="your-jwt-token")
        >>> client = CAClient(base_url="https://ca.example.com", auth=auth)
    """

    def __init__(self, token: str):
        """
        Initialize Bearer token authentication.

        Args:
            token: The bearer token value.
        """
        self.token = token

    def apply(self, request: httpx.Request) -> httpx.Request:
        """Apply Bearer token to request."""
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request
