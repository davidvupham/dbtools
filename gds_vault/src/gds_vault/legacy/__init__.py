"""
Legacy module for backward compatibility.
"""

from .vault import VaultClient, get_secret_from_vault, retry_with_backoff

__all__ = ["VaultClient", "get_secret_from_vault", "retry_with_backoff"]
