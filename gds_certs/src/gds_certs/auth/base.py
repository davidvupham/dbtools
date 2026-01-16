"""
Base authentication classes for CA API clients.

This module defines the abstract base class for authentication strategies,
allowing pluggable authentication mechanisms.
"""

from abc import ABC, abstractmethod

import httpx


class BaseAuth(ABC):
    """
    Abstract base class for authentication strategies.

    Implement this class to create custom authentication mechanisms
    for the CA API client.

    Example:
        >>> class CustomAuth(BaseAuth):
        ...     def __init__(self, token: str):
        ...         self.token = token
        ...
        ...     def apply(self, request: httpx.Request) -> httpx.Request:
        ...         request.headers["Authorization"] = f"Bearer {self.token}"
        ...         return request
    """

    @abstractmethod
    def apply(self, request: httpx.Request) -> httpx.Request:
        """
        Apply authentication to an HTTP request.

        Args:
            request: The httpx Request object to modify.

        Returns:
            The modified request with authentication applied.
        """
        pass

    def refresh(self) -> None:  # noqa: B027
        """
        Refresh authentication credentials if needed.

        Override this method for auth strategies that support token refresh.
        Default implementation does nothing.
        """
