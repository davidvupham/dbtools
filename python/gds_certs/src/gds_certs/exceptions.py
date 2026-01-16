"""
Exception classes for gds_certs package.

This module defines a hierarchy of exceptions for different error scenarios,
enabling precise error handling and better debugging.
"""


class CertError(Exception):
    """
    Base exception for all certificate-related errors.

    This is the parent class for all custom exceptions in the package,
    allowing users to catch all package-specific errors with a single handler.
    """

    pass


class CSRGenerationError(CertError):
    """
    Exception raised when CSR generation fails.

    Raised when:
    - Invalid key parameters provided
    - Subject information is invalid
    - Cryptographic operation fails
    """

    pass


class KeyGenerationError(CertError):
    """
    Exception raised when private key generation fails.

    Raised when:
    - Invalid key size specified
    - Cryptographic library error
    """

    pass


class CAClientError(CertError):
    """
    Exception raised for CA API communication errors.

    Raised when:
    - Network error connecting to CA
    - API timeout
    - Unexpected response format
    """

    pass


class CAAuthError(CertError):
    """
    Exception raised for CA authentication failures.

    Raised when:
    - API key is invalid
    - Token has expired
    - Authentication endpoint returns error
    """

    pass


class CertificateError(CertError):
    """
    Exception raised for certificate-related errors.

    Raised when:
    - Certificate parsing fails
    - Certificate validation fails
    - Certificate format is invalid
    """

    pass
