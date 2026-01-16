"""
CSR (Certificate Signing Request) generation module.

This module provides functionality to generate private keys and CSRs
using the cryptography library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import ip_address
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID

from gds_certs.exceptions import CSRGenerationError, KeyGenerationError


@dataclass
class CertificateRequest:
    """
    Generate and manage Certificate Signing Requests (CSRs).

    This class handles private key generation and CSR creation with support
    for RSA and ECDSA keys, Subject Alternative Names (SANs), and various
    subject attributes.

    Example:
        >>> req = CertificateRequest(
        ...     common_name="server.example.com",
        ...     organization="My Company",
        ...     san_dns=["server.example.com", "www.example.com"],
        ... )
        >>> req.generate()
        >>> req.save_private_key("/path/to/key.pem", passphrase="secret")
        >>> print(req.csr_pem)
    """

    common_name: str
    organization: str | None = None
    organizational_unit: str | None = None
    country: str | None = None
    state: str | None = None
    locality: str | None = None
    email: str | None = None
    san_dns: list[str] = field(default_factory=list)
    san_ip: list[str] = field(default_factory=list)
    key_type: str = "rsa"  # "rsa" or "ecdsa"
    key_size: int = 2048  # RSA key size (2048, 4096)
    curve: str = "secp256r1"  # ECDSA curve

    _private_key: rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey | None = field(default=None, repr=False, compare=False)
    _csr: x509.CertificateSigningRequest | None = field(default=None, repr=False, compare=False)

    def generate(self) -> None:
        """
        Generate private key and CSR.

        Raises:
            KeyGenerationError: If key generation fails.
            CSRGenerationError: If CSR generation fails.
        """
        self._generate_private_key()
        self._generate_csr()

    def _generate_private_key(self) -> None:
        """Generate the private key based on key_type."""
        try:
            if self.key_type.lower() == "rsa":
                if self.key_size < 2048:
                    raise KeyGenerationError("RSA key size must be at least 2048 bits")
                self._private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=self.key_size,
                )
            elif self.key_type.lower() == "ecdsa":
                curves = {
                    "secp256r1": ec.SECP256R1(),
                    "secp384r1": ec.SECP384R1(),
                    "secp521r1": ec.SECP521R1(),
                }
                if self.curve not in curves:
                    raise KeyGenerationError(f"Unsupported curve: {self.curve}. Use: {list(curves.keys())}")
                self._private_key = ec.generate_private_key(curves[self.curve])
            else:
                raise KeyGenerationError(f"Unsupported key type: {self.key_type}. Use 'rsa' or 'ecdsa'")
        except KeyGenerationError:
            raise
        except Exception as e:
            raise KeyGenerationError(f"Failed to generate private key: {e}") from e

    def _generate_csr(self) -> None:
        """Generate the CSR using the private key."""
        if self._private_key is None:
            raise CSRGenerationError("Private key must be generated first")

        try:
            # Build subject name
            subject_attrs = [x509.NameAttribute(NameOID.COMMON_NAME, self.common_name)]

            if self.organization:
                subject_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization))
            if self.organizational_unit:
                subject_attrs.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.organizational_unit))
            if self.country:
                subject_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, self.country))
            if self.state:
                subject_attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state))
            if self.locality:
                subject_attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality))
            if self.email:
                subject_attrs.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.email))

            builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(subject_attrs))

            # Add Subject Alternative Names if provided
            san_list: list[x509.GeneralName] = []
            for dns in self.san_dns:
                san_list.append(x509.DNSName(dns))
            for ip in self.san_ip:
                san_list.append(x509.IPAddress(ip_address(ip)))

            if san_list:
                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )

            # Sign the CSR
            self._csr = builder.sign(self._private_key, hashes.SHA256())

        except CSRGenerationError:
            raise
        except Exception as e:
            raise CSRGenerationError(f"Failed to generate CSR: {e}") from e

    @property
    def csr_pem(self) -> str:
        """Return CSR in PEM format."""
        if self._csr is None:
            raise CSRGenerationError("CSR not generated. Call generate() first.")
        return self._csr.public_bytes(serialization.Encoding.PEM).decode()

    @property
    def csr_der(self) -> bytes:
        """Return CSR in DER format."""
        if self._csr is None:
            raise CSRGenerationError("CSR not generated. Call generate() first.")
        return self._csr.public_bytes(serialization.Encoding.DER)

    @property
    def private_key_pem(self) -> str:
        """Return private key in PEM format (unencrypted)."""
        if self._private_key is None:
            raise KeyGenerationError("Private key not generated. Call generate() first.")
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

    def save_private_key(self, path: str | Path, passphrase: str | None = None) -> None:
        """
        Save private key to file.

        Args:
            path: File path to save the key.
            passphrase: Optional passphrase to encrypt the key.
        """
        if self._private_key is None:
            raise KeyGenerationError("Private key not generated. Call generate() first.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if passphrase:
            encryption = serialization.BestAvailableEncryption(passphrase.encode())
        else:
            encryption = serialization.NoEncryption()

        key_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption,
        )
        path.write_bytes(key_bytes)
        # Set restrictive permissions
        path.chmod(0o600)

    def save_csr(self, path: str | Path) -> None:
        """
        Save CSR to file in PEM format.

        Args:
            path: File path to save the CSR.
        """
        if self._csr is None:
            raise CSRGenerationError("CSR not generated. Call generate() first.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.csr_pem)
