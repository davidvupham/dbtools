"""
Tests for CSR generation module.
"""

import tempfile
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from gds_certs import CertificateRequest
from gds_certs.exceptions import CSRGenerationError, KeyGenerationError


class TestCertificateRequest:
    """Tests for CertificateRequest class."""

    def test_generate_rsa_csr(self, sample_csr_params):
        """Test generating a CSR with RSA key."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        assert req.csr_pem is not None
        assert "-----BEGIN CERTIFICATE REQUEST-----" in req.csr_pem
        assert req.private_key_pem is not None
        assert "-----BEGIN RSA PRIVATE KEY-----" in req.private_key_pem

    def test_generate_ecdsa_csr(self, sample_csr_params):
        """Test generating a CSR with ECDSA key."""
        req = CertificateRequest(**sample_csr_params, key_type="ecdsa", curve="secp256r1")
        req.generate()

        assert req.csr_pem is not None
        assert "-----BEGIN CERTIFICATE REQUEST-----" in req.csr_pem

    def test_csr_contains_subject(self, sample_csr_params):
        """Test that generated CSR contains correct subject information."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        # Parse the CSR
        csr = x509.load_pem_x509_csr(req.csr_pem.encode())

        # Check subject
        cn = csr.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
        org = csr.subject.get_attributes_for_oid(x509.oid.NameOID.ORGANIZATION_NAME)[0].value

        assert cn == "test.example.com"
        assert org == "Test Organization"

    def test_csr_contains_san(self, sample_csr_params):
        """Test that generated CSR contains Subject Alternative Names."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        # Parse the CSR
        csr = x509.load_pem_x509_csr(req.csr_pem.encode())

        # Get SAN extension
        san = csr.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        dns_names = san.value.get_values_for_type(x509.DNSName)

        assert "test.example.com" in dns_names
        assert "www.test.example.com" in dns_names

    def test_csr_with_ip_san(self):
        """Test CSR generation with IP address in SAN."""
        req = CertificateRequest(
            common_name="server.local",
            san_ip=["192.168.1.100", "10.0.0.1"],
        )
        req.generate()

        csr = x509.load_pem_x509_csr(req.csr_pem.encode())
        san = csr.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        ip_addresses = san.value.get_values_for_type(x509.IPAddress)

        assert len(ip_addresses) == 2

    def test_invalid_key_size(self):
        """Test that small RSA key sizes are rejected."""
        req = CertificateRequest(common_name="test.example.com", key_size=1024)

        with pytest.raises(KeyGenerationError, match="at least 2048"):
            req.generate()

    def test_invalid_key_type(self):
        """Test that invalid key types are rejected."""
        req = CertificateRequest(common_name="test.example.com", key_type="invalid")

        with pytest.raises(KeyGenerationError, match="Unsupported key type"):
            req.generate()

    def test_invalid_curve(self):
        """Test that invalid ECDSA curves are rejected."""
        req = CertificateRequest(common_name="test.example.com", key_type="ecdsa", curve="invalid")

        with pytest.raises(KeyGenerationError, match="Unsupported curve"):
            req.generate()

    def test_csr_pem_before_generate_raises(self):
        """Test that accessing csr_pem before generate() raises error."""
        req = CertificateRequest(common_name="test.example.com")

        with pytest.raises(CSRGenerationError, match="not generated"):
            _ = req.csr_pem

    def test_save_private_key(self, sample_csr_params):
        """Test saving private key to file."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "test.key"
            req.save_private_key(key_path)

            assert key_path.exists()
            # Check permissions (should be 0o600)
            assert key_path.stat().st_mode & 0o777 == 0o600

            # Verify key can be loaded
            key_data = key_path.read_bytes()
            serialization.load_pem_private_key(key_data, password=None)

    def test_save_private_key_with_passphrase(self, sample_csr_params):
        """Test saving encrypted private key."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "test.key"
            passphrase = "test-passphrase"
            req.save_private_key(key_path, passphrase=passphrase)

            assert key_path.exists()

            # Verify key requires passphrase
            key_data = key_path.read_bytes()
            with pytest.raises(TypeError):
                serialization.load_pem_private_key(key_data, password=None)

            # Verify key loads with correct passphrase
            serialization.load_pem_private_key(key_data, password=passphrase.encode())

    def test_save_csr(self, sample_csr_params):
        """Test saving CSR to file."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            csr_path = Path(tmpdir) / "test.csr"
            req.save_csr(csr_path)

            assert csr_path.exists()
            content = csr_path.read_text()
            assert "-----BEGIN CERTIFICATE REQUEST-----" in content

    def test_csr_der_format(self, sample_csr_params):
        """Test getting CSR in DER format."""
        req = CertificateRequest(**sample_csr_params)
        req.generate()

        der_data = req.csr_der
        assert isinstance(der_data, bytes)
        # DER format doesn't have PEM headers
        assert b"-----BEGIN" not in der_data

    def test_4096_bit_key(self):
        """Test generating CSR with 4096-bit RSA key."""
        req = CertificateRequest(common_name="test.example.com", key_size=4096)
        req.generate()

        assert req.csr_pem is not None

    def test_different_ecdsa_curves(self):
        """Test ECDSA with different curves."""
        for curve in ["secp256r1", "secp384r1", "secp521r1"]:
            req = CertificateRequest(common_name="test.example.com", key_type="ecdsa", curve=curve)
            req.generate()
            assert req.csr_pem is not None
