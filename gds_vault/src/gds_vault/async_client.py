import logging
import os
import time
from typing import TYPE_CHECKING, Any, Optional

try:
    import aiohttp
except ImportError:
    aiohttp = None

from gds_vault.auth import AsyncAppRoleAuth
from gds_vault.base import (
    AsyncAuthStrategy,
    AsyncResourceManager,
    AsyncSecretProvider,
    CacheProtocol,
    Configurable,
)
from gds_vault.cache import SecretCache
from gds_vault.exceptions import (
    VaultAuthError,
    VaultConfigurationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
)
from gds_vault.retry import RetryPolicy

if TYPE_CHECKING:
    from gds_metrics import MetricsCollector

    try:
        from gds_metrics import NoOpMetrics
    except ImportError:

        class NoOpMetrics:
            def increment(self, *args, **kwargs):
                pass

            def gauge(self, *args, **kwargs):
                pass

            def histogram(self, *args, **kwargs):
                pass

            def timing(self, *args, **kwargs):
                pass
else:
    try:
        from gds_metrics import MetricsCollector, NoOpMetrics
    except ImportError:

        class NoOpMetrics:
            def increment(self, *args, **kwargs):
                pass

            def gauge(self, *args, **kwargs):
                pass

            def histogram(self, *args, **kwargs):
                pass

            def timing(self, *args, **kwargs):
                pass


logger = logging.getLogger(__name__)


class AsyncVaultClient(AsyncSecretProvider, AsyncResourceManager, Configurable):
    """
    Asynchronous HashiCorp Vault client.

    Mirroring `VaultClient` features but with `async/await` syntax and `aiohttp`.

    Args:
        vault_addr: Vault server address
        auth: Async authentication strategy (defaults to AsyncAppRoleAuth)
        cache: Cache implementation
        retry_policy: Retry policy
        timeout: Request timeout in seconds
        config: Additional configuration
    """

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        auth: Optional[AsyncAuthStrategy] = None,
        cache: Optional[CacheProtocol] = None,  # Can use sync cache if thread-safe or simple dict
        retry_policy: Optional[RetryPolicy] = None,
        timeout: int = 10,
        config: Optional[dict[str, Any]] = None,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
        mount_point: Optional[str] = None,
        namespace: Optional[str] = None,
        metrics: Optional["MetricsCollector"] = None,
    ):
        Configurable.__init__(self)

        if aiohttp is None:
            raise ImportError("aiohttp is required for AsyncVaultClient")

        # Configuration
        self._config = config or {}
        self._vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self._timeout = timeout

        # SSL Configuration
        self._verify_ssl = verify_ssl
        self._ssl_cert_path = ssl_cert_path or os.getenv("VAULT_SSL_CERT")

        # Mount point and Namespace
        self._mount_point = mount_point or os.getenv("VAULT_MOUNT_POINT")
        self._namespace = namespace or os.getenv("VAULT_NAMESPACE")

        self._validate_configuration()

        # Components
        self._auth = auth or AsyncAppRoleAuth()
        self._cache = cache if cache is not None else SecretCache()
        self._retry_policy = retry_policy or RetryPolicy(max_retries=3)
        self._metrics = metrics or NoOpMetrics()

        # State
        self._token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._initialized = False
        self._authenticated = False

        # Async session
        self._session: Optional[aiohttp.ClientSession] = None

    def _validate_configuration(self) -> None:
        """Validate client configuration."""
        if not self._vault_addr:
            raise VaultConfigurationError("Vault address must be provided or set in VAULT_ADDR environment variable")
        if not self._vault_addr.startswith(("http://", "https://")):
            raise VaultConfigurationError(
                f"Invalid Vault address: {self._vault_addr}. Must start with http:// or https://"
            )

    async def initialize(self) -> None:
        """Initialize async resources (ClientSession)."""
        if not self._initialized:
            self._session = aiohttp.ClientSession()
            self._initialized = True
            if not self.is_authenticated:
                try:
                    await self.authenticate()
                except VaultAuthError:
                    logger.warning("Pre-authentication failed during initialization")

    async def cleanup(self) -> None:
        """Cleanup async resources."""
        if self._session:
            await self._session.close()
            self._session = None
        self._token = None
        self._authenticated = False
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if client resources are initialized."""
        return self._initialized

    @property
    def is_authenticated(self) -> bool:
        if not self._authenticated or not self._token:
            return False
        if self._token_expiry and time.time() >= self._token_expiry:
            self._authenticated = False
            return False
        return True

    async def authenticate(self) -> bool:
        try:

            async def _auth():
                return await self._auth.authenticate(
                    self._vault_addr,
                    self._timeout,
                    verify_ssl=self._verify_ssl,
                    ssl_cert_path=self._ssl_cert_path,
                )

            # Use retry policy (assuming it supports async/await or is generic enough?
            # The current RetryPolicy is synchronous. We need a simple async retry wrapper here or update RetryPolicy.
            # For Phase 4, let's implement a simple inline retry or assume RetryPolicy needs update.
            # Checking RetryPolicy in retry.py (not visible but usually sync).
            # I will assume I need to implement a simple async retry loop here for now.)

            # Simple async retry logic since RetryPolicy might be sync
            last_exception = None
            for attempt in range(self._retry_policy.max_retries + 1):
                try:
                    self._token, self._token_expiry = await _auth()
                    self._authenticated = True
                    self._metrics.increment("vault.auth.success")
                    return True
                except Exception as e:
                    last_exception = e
                    if attempt < self._retry_policy.max_retries:
                        import asyncio

                        await asyncio.sleep(self._retry_policy.backoff_factor * (2**attempt))

            raise last_exception

        except Exception as e:
            logger.error("Authentication failed: %s", e)
            self._metrics.increment("vault.auth.failure")
            self._authenticated = False
            raise VaultAuthError(f"Authentication failed: {e}") from e

    def _construct_secret_path(self, path: str) -> str:
        if self._mount_point and not path.startswith(f"{self._mount_point}/"):
            return f"{self._mount_point}/{path}"
        return path

    async def get_secret(
        self, path: str, use_cache: bool = True, version: Optional[int] = None, **kwargs
    ) -> dict[str, Any]:
        full_path = self._construct_secret_path(path)
        cache_key = f"{full_path}:v{version}" if version else full_path

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                # Rotation check skipped for simplicity in this iteration, or use sync check
                return cached

        logger.info("Fetching secret from Vault (Async): %s", full_path)

        async def _fetch():
            return await self._fetch_secret_from_vault(full_path, version)

        try:
            start_time = time.time()
            # Async retry loop
            secret_data = None
            last_exception = None
            for attempt in range(self._retry_policy.max_retries + 1):
                try:
                    secret_data = await _fetch()
                    break
                except aiohttp.ClientError as e:
                    last_exception = e
                    if attempt < self._retry_policy.max_retries:
                        import asyncio

                        await asyncio.sleep(self._retry_policy.backoff_factor * (2**attempt))

            if secret_data is None:
                raise last_exception

            duration = (time.time() - start_time) * 1000
            self._metrics.timing("vault.secret.fetch", duration, labels={"path": full_path})
            self._metrics.increment("vault.secret.hit", labels={"path": full_path})

            if use_cache:
                self._cache.set(cache_key, secret_data)

            return secret_data

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                raise VaultSecretNotFoundError(f"Secret not found: {full_path}") from e
            if e.status == 403:
                raise VaultPermissionError(f"Permission denied: {full_path}") from e
            raise VaultError(f"Failed to fetch secret {full_path}: {e}") from e
        except Exception as e:
            self._metrics.increment("vault.secret.error", labels={"type": "connection", "path": full_path})
            raise VaultConnectionError(f"Failed to connect to Vault: {e}") from e

    async def _fetch_secret_from_vault(self, secret_path: str, version: Optional[int] = None) -> dict[str, Any]:
        if not self.is_authenticated:
            await self.authenticate()

        if not self._session:
            await self.initialize()

        secret_url = f"{self._vault_addr}/v1/{secret_path}"
        headers = {"X-Vault-Token": self._token}
        if self._namespace:
            headers["X-Vault-Namespace"] = self._namespace

        params = {"version": str(version)} if version else None

        ssl_context = None
        if self._ssl_cert_path:
            import ssl

            ssl_context = ssl.create_default_context(cafile=self._ssl_cert_path)
        elif not self._verify_ssl:
            import ssl

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        async with self._session.get(
            secret_url,
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(total=self._timeout),
            ssl=ssl_context,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

            if "data" in data and "data" in data["data"]:
                return data["data"]["data"]
            if "data" in data:
                return data["data"]
            raise VaultError(f"Unexpected response format for secret {secret_path}")

    # Configurable implementation (same as synchronous)
    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        self._config[key] = value

    def get_all_config(self) -> dict[str, Any]:
        return {
            "vault_addr": self._vault_addr,
            "timeout": self._timeout,
            "verify_ssl": self._verify_ssl,
            **self._config,
        }
