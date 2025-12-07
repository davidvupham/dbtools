"""
Authentication strategies for HashiCorp Vault.

This module implements various authentication methods using the Strategy pattern,
allowing flexible authentication without modifying client code.
"""

import logging
import os
import time
from typing import Optional

import requests

from gds_vault.base import AsyncAuthStrategy, AuthStrategy
from gds_vault.exceptions import VaultAuthError

try:
    import aiohttp
except ImportError:
    aiohttp = None  # Handle optional dependency


logger = logging.getLogger(__name__)


class AppRoleAuth(AuthStrategy):
    """
    AppRole authentication strategy for HashiCorp Vault.

    AppRole is designed for machine authentication, making it ideal for
    servers, applications, and automation workflows.

    Args:
        role_id: AppRole role_id (or None to use VAULT_ROLE_ID env var)
        secret_id: AppRole secret_id (or None to use VAULT_SECRET_ID env var)
        namespace: Vault namespace (or None to use VAULT_NAMESPACE env var)

    Example:
        auth = AppRoleAuth(role_id="my-role-id", secret_id="my-secret-id")
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """

    def __init__(
        self,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        """Initialize AppRole authentication."""
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        self.namespace = namespace or os.getenv("VAULT_NAMESPACE")

        if not self.role_id or not self.secret_id:
            raise VaultAuthError(
                "AppRole credentials must be provided or set in "
                "VAULT_ROLE_ID and VAULT_SECRET_ID environment variables"
            )

    def authenticate(
        self,
        vault_addr: str,
        timeout: int,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ) -> tuple[str, float]:
        """
        Authenticate with Vault using AppRole.

        Args:
            vault_addr: Vault server address
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            ssl_cert_path: Path to SSL certificate bundle

        Returns:
            tuple: (token, expiry_timestamp)

        Raises:
            VaultAuthError: If authentication fails
        """
        logger.info("Authenticating with Vault using AppRole at %s", vault_addr)
        if self.namespace:
            logger.debug("Using Vault namespace: %s", self.namespace)

        login_url = f"{vault_addr}/v1/auth/approle/login"
        login_payload = {"role_id": self.role_id, "secret_id": self.secret_id}

        # Add namespace header if configured
        headers = {}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        # Configure SSL verification
        verify = ssl_cert_path if ssl_cert_path else verify_ssl

        try:
            resp = requests.post(
                login_url,
                json=login_payload,
                headers=headers,
                timeout=timeout,
                verify=verify,
            )
        except requests.RequestException as e:
            logger.error("Network error during AppRole authentication: %s", e)
            raise VaultAuthError(f"Failed to connect to Vault: {e}") from e

        if not resp.ok:
            logger.error(
                "AppRole authentication failed with status %s: %s",
                resp.status_code,
                resp.text,
            )
            raise VaultAuthError(f"Vault AppRole login failed: {resp.text}")

        auth_data = resp.json()["auth"]
        token = auth_data["client_token"]

        # Calculate token expiry with 5-minute early refresh buffer
        lease_duration = auth_data.get("lease_duration", 3600)
        expiry = time.time() + lease_duration - 300

        logger.info(
            "Successfully authenticated with AppRole. Token valid for %ss",
            lease_duration,
        )
        logger.debug("Token will expire at timestamp: %s", expiry)

        return token, expiry

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        role_id_masked = f"{self.role_id[:8]}..." if self.role_id else "None"
        return f"AppRoleAuth(role_id='{role_id_masked}')"

    def __str__(self) -> str:
        """User-friendly representation."""
        return "AppRole Authentication"


class TokenAuth(AuthStrategy):
    """
    Direct token authentication strategy.

    Use this when you already have a Vault token (e.g., from environment
    or a previous authentication). The token is used directly without
    additional authentication.

    Args:
        token: Vault token
        ttl: Token time-to-live in seconds (default: 3600)

    Example:
        auth = TokenAuth(token="hvs.CAESIF...")
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """

    def __init__(self, token: str, ttl: int = 3600):
        """Initialize token authentication."""
        if not token:
            raise VaultAuthError("Token must be provided")
        self.token = token
        self.ttl = ttl

    def authenticate(
        self,
        vault_addr: str,
        timeout: int,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ) -> tuple[str, float]:
        """
        Return the provided token with calculated expiry.

        Args:
            vault_addr: Vault server address (not used)
            timeout: Request timeout (not used)
            verify_ssl: Whether to verify SSL certificates (not used)
            ssl_cert_path: Path to SSL certificate bundle (not used)

        Returns:
            tuple: (token, expiry_timestamp)
        """
        logger.info("Using direct token authentication")
        expiry = time.time() + self.ttl - 300  # 5-minute early refresh
        return self.token, expiry

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        token_masked = f"{self.token[:8]}..." if self.token else "None"
        return f"TokenAuth(token='{token_masked}', ttl={self.ttl})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return "Direct Token Authentication"


class EnvironmentAuth(AuthStrategy):
    """
    Authentication using VAULT_TOKEN environment variable.

    This is convenient for development and testing where the token
    is provided via environment variables.

    Example:
        # Set VAULT_TOKEN environment variable
        auth = EnvironmentAuth()
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """

    def __init__(self, ttl: int = 3600):
        """Initialize environment-based authentication."""
        self.ttl = ttl
        self.token = os.getenv("VAULT_TOKEN")
        if not self.token:
            raise VaultAuthError("VAULT_TOKEN environment variable must be set")

    def authenticate(
        self,
        vault_addr: str,
        timeout: int,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ) -> tuple[str, float]:
        """
        Return token from environment with calculated expiry.

        Args:
            vault_addr: Vault server address (not used)
            timeout: Request timeout (not used)
            verify_ssl: Whether to verify SSL certificates (not used)
            ssl_cert_path: Path to SSL certificate bundle (not used)

        Returns:
            tuple: (token, expiry_timestamp)
        """
        logger.info("Using token from VAULT_TOKEN environment variable")
        expiry = time.time() + self.ttl - 300
        return self.token, expiry

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        token_masked = f"{self.token[:8]}..." if self.token else "None"
        return f"EnvironmentAuth(token='{token_masked}', ttl={self.ttl})"

    def __str__(self) -> str:
        """User-friendly representation."""
        return "Environment Variable Token Authentication"


class AsyncAppRoleAuth(AsyncAuthStrategy):
    """
    Async AppRole authentication strategy for HashiCorp Vault.

    Requires 'aiohttp' to be installed.
    """

    def __init__(
        self,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        """Initialize Async AppRole authentication."""
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        self.namespace = namespace or os.getenv("VAULT_NAMESPACE")

        if not self.role_id or not self.secret_id:
            raise VaultAuthError(
                "AppRole credentials must be provided or set in "
                "VAULT_ROLE_ID and VAULT_SECRET_ID environment variables"
            )

    async def authenticate(
        self,
        vault_addr: str,
        timeout: int,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
    ) -> tuple[str, float]:
        """Authenticate with Vault using AppRole asynchronously."""
        if aiohttp is None:
            raise ImportError("aiohttp is required for async support")

        logger.info("Authenticating with Vault using AppRole (Async) at %s", vault_addr)

        login_url = f"{vault_addr}/v1/auth/approle/login"
        login_payload = {"role_id": self.role_id, "secret_id": self.secret_id}

        headers = {}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        ssl_context = None
        if ssl_cert_path:
            import ssl

            ssl_context = ssl.create_default_context(cafile=ssl_cert_path)
        elif not verify_ssl:
            import ssl

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    login_url,
                    json=login_payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=ssl_context,
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(
                            "AppRole authentication failed with status %s: %s",
                            resp.status,
                            text,
                        )
                        raise VaultAuthError(f"Vault AppRole login failed: {text}")

                    data = await resp.json()
                    auth_data = data["auth"]
                    token = auth_data["client_token"]
                    lease_duration = auth_data.get("lease_duration", 3600)
                    expiry = time.time() + lease_duration - 300

                    logger.info(
                        "Successfully authenticated with AppRole (Async). Token valid for %ss",
                        lease_duration,
                    )
                    return token, expiry

        except aiohttp.ClientError as e:
            logger.error("Network error during Async AppRole authentication: %s", e)
            raise VaultAuthError(f"Failed to connect to Vault: {e}") from e
