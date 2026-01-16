"""
gds-certs: Certificate management library for CSR generation and CA integration.

This package provides tools for generating Certificate Signing Requests (CSRs),
submitting them to an internal CA API, and managing certificates.

Example:
    >>> from gds_certs import CertificateRequest, CAClient
    >>> from gds_certs.auth import APIKeyAuth
    >>>
    >>> # Generate CSR
    >>> req = CertificateRequest(
    ...     common_name="server.example.com",
    ...     organization="My Company",
    ...     san_dns=["server.example.com", "www.example.com"],
    ... )
    >>> req.generate()
    >>>
    >>> # Submit to CA
    >>> client = CAClient(
    ...     base_url="https://ca-api.internal",
    ...     auth=APIKeyAuth(api_key="your-key"),
    ... )
    >>> cert = client.submit_csr(req.csr_pem)
    >>>
    >>> # Save files
    >>> req.save_private_key("/path/to/key.pem", passphrase="secret")
    >>> cert.save("/path/to/cert.pem")
"""

from gds_certs.auth import APIKeyAuth, BaseAuth, BearerAuth
from gds_certs.client import CAClient
from gds_certs.csr import CertificateRequest
from gds_certs.exceptions import (
    CAAuthError,
    CAClientError,
    CertError,
    CertificateError,
    CSRGenerationError,
    KeyGenerationError,
)
from gds_certs.models import CertificateResponse, CSRMetadata, SubjectInfo

__version__ = "0.1.0"

__all__ = [
    "APIKeyAuth",
    "BaseAuth",
    "BearerAuth",
    "CAAuthError",
    "CAClient",
    "CAClientError",
    "CSRGenerationError",
    "CSRMetadata",
    "CertError",
    "CertificateError",
    "CertificateRequest",
    "CertificateResponse",
    "KeyGenerationError",
    "SubjectInfo",
]
