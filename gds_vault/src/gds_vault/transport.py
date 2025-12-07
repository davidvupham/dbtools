"""
HTTP transport abstraction for Vault operations.

Provides a reusable requests.Session and centralizes SSL verification and
namespace header handling. Optional for the modern VaultClient; if not
provided, the client continues to use requests directly.
"""

import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class VaultTransport:
    """
    Simple HTTP transport for Vault.

    Args:
        verify_ssl: Whether to verify SSL certs (default True)
        ssl_cert_path: Path to CA bundle to use for verification
        namespace: Optional Vault namespace header
        session: Optional preconfigured requests.Session
    """

    def __init__(
        self,
        verify_ssl: bool = True,
        ssl_cert_path: Optional[str] = None,
        namespace: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._session = session or requests.Session()
        self._verify_ssl = verify_ssl
        self._ssl_cert_path = ssl_cert_path
        self._namespace = namespace

    @property
    def verify(self) -> Any:
        """Resolve verify parameter for requests based on SSL config."""
        return self._ssl_cert_path if self._ssl_cert_path else self._verify_ssl

    def _with_namespace(self, headers: Optional[dict[str, str]]) -> dict[str, str]:
        merged = dict(headers or {})
        if self._namespace and "X-Vault-Namespace" not in merged:
            merged["X-Vault-Namespace"] = self._namespace
        return merged

    def post(
        self,
        url: str,
        *,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self._session.post(
            url,
            json=json,
            headers=self._with_namespace(headers),
            timeout=timeout,
            verify=self.verify,
        )

    def get(
        self,
        url: str,
        *,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self._session.get(
            url,
            headers=self._with_namespace(headers),
            params=params,
            timeout=timeout,
            verify=self.verify,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self._session.request(
            method,
            url,
            headers=self._with_namespace(headers),
            params=params,
            json=json,
            timeout=timeout,
            verify=self.verify,
        )
