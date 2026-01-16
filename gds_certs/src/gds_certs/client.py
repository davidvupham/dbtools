"""
CA (Certificate Authority) API client.

This module provides a client for interacting with the internal CA REST API
to submit CSRs and retrieve signed certificates.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from gds_certs.auth.base import BaseAuth
from gds_certs.exceptions import CAAuthError, CAClientError
from gds_certs.models import CertificateResponse, CSRMetadata

logger = logging.getLogger(__name__)


class CAClient:
    """
    Client for interacting with the internal Certificate Authority API.

    This client handles CSR submission and certificate retrieval from the CA.

    Example:
        >>> from gds_certs import CAClient
        >>> from gds_certs.auth import APIKeyAuth
        >>>
        >>> client = CAClient(
        ...     base_url="https://ca-api.internal",
        ...     auth=APIKeyAuth(api_key="your-api-key"),
        ... )
        >>> response = client.submit_csr(csr_pem)
        >>> response.save("/path/to/cert.pem")
    """

    def __init__(
        self,
        base_url: str,
        auth: BaseAuth | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """
        Initialize the CA client.

        Args:
            base_url: Base URL of the CA API.
            auth: Authentication strategy to use.
            timeout: Request timeout in seconds.
            verify_ssl: Whether to verify SSL certificates.
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def _build_client(self) -> httpx.Client:
        """Build an httpx client with configured settings."""
        return httpx.Client(
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

    def _send_request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
    ) -> httpx.Response:
        """
        Send an authenticated request to the CA API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path.
            json: JSON body to send.

        Returns:
            The HTTP response.

        Raises:
            CAAuthError: If authentication fails.
            CAClientError: If the request fails.
        """
        url = f"{self.base_url}{endpoint}"

        with self._build_client() as client:
            request = client.build_request(method, url, json=json)

            if self.auth:
                request = self.auth.apply(request)

            try:
                response = client.send(request)
            except httpx.TimeoutException as e:
                raise CAClientError(f"Request timed out: {e}") from e
            except httpx.RequestError as e:
                raise CAClientError(f"Request failed: {e}") from e

            # Handle authentication errors
            if response.status_code == 401:
                raise CAAuthError("Authentication failed: Invalid credentials")
            if response.status_code == 403:
                raise CAAuthError("Authentication failed: Insufficient permissions")

            # Handle other errors
            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                raise CAClientError(f"CA API error ({response.status_code}): {error_detail}")

            return response

    def submit_csr(
        self,
        csr_pem: str,
        metadata: CSRMetadata | None = None,
        template: str | None = None,
    ) -> CertificateResponse:
        """
        Submit a CSR to the CA for signing.

        Args:
            csr_pem: The CSR in PEM format.
            metadata: Optional metadata to include with the request.
            template: Optional certificate template name.

        Returns:
            CertificateResponse containing the signed certificate.

        Raises:
            CAClientError: If the submission fails.
            CAAuthError: If authentication fails.

        Note:
            Update the endpoint path and request/response format to match
            your internal CA API specification.
        """
        # Build request payload
        # TODO: Adjust payload structure to match your CA API
        payload: dict = {"csr": csr_pem}

        if template:
            payload["template"] = template

        if metadata:
            payload["metadata"] = metadata.to_dict()

        logger.info("Submitting CSR to CA")
        response = self._send_request("POST", "/api/v1/certificates", json=payload)

        # Parse response
        # TODO: Adjust response parsing to match your CA API
        data = response.json()

        return CertificateResponse(
            certificate_pem=data.get("certificate"),
            chain_pem=data.get("chain"),
            serial_number=data.get("serial_number"),
            request_id=data.get("request_id"),
        )

    def get_certificate(self, request_id: str) -> CertificateResponse:
        """
        Retrieve a certificate by request ID.

        Useful for async issuance workflows where the certificate
        is not immediately available.

        Args:
            request_id: The request ID from a previous CSR submission.

        Returns:
            CertificateResponse containing the signed certificate.

        Raises:
            CAClientError: If the retrieval fails.
        """
        logger.info(f"Retrieving certificate for request: {request_id}")
        response = self._send_request("GET", f"/api/v1/certificates/{request_id}")

        data = response.json()
        return CertificateResponse(
            certificate_pem=data.get("certificate"),
            chain_pem=data.get("chain"),
            serial_number=data.get("serial_number"),
            request_id=request_id,
        )

    def health_check(self) -> bool:
        """
        Check if the CA API is available.

        Returns:
            True if the API is healthy, False otherwise.
        """
        try:
            response = self._send_request("GET", "/api/v1/health")
            return response.status_code == 200
        except CAClientError:
            return False
