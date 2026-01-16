"""
Tests for data models.
"""

import tempfile
from pathlib import Path

import pytest

from gds_certs.models import CertificateResponse, CSRMetadata, SubjectInfo


class TestSubjectInfo:
    """Tests for SubjectInfo class."""

    def test_minimal_subject(self):
        """Test creating subject with only common name."""
        subject = SubjectInfo(common_name="test.example.com")
        assert subject.common_name == "test.example.com"
        assert subject.organization is None

    def test_full_subject(self):
        """Test creating subject with all fields."""
        subject = SubjectInfo(
            common_name="test.example.com",
            organization="Test Org",
            organizational_unit="IT",
            country="US",
            state="CA",
            locality="SF",
            email="admin@example.com",
        )
        assert subject.common_name == "test.example.com"
        assert subject.organization == "Test Org"


class TestCSRMetadata:
    """Tests for CSRMetadata class."""

    def test_to_dict_empty(self):
        """Test converting empty metadata to dict."""
        metadata = CSRMetadata()
        result = metadata.to_dict()
        assert result == {}

    def test_to_dict_with_fields(self):
        """Test converting metadata with fields to dict."""
        metadata = CSRMetadata(
            requester="john.doe",
            department="Engineering",
            environment="production",
            application="web-app",
            ticket_id="TICKET-123",
        )
        result = metadata.to_dict()

        assert result["requester"] == "john.doe"
        assert result["department"] == "Engineering"
        assert result["environment"] == "production"
        assert result["application"] == "web-app"
        assert result["ticket_id"] == "TICKET-123"

    def test_to_dict_with_custom_fields(self):
        """Test metadata with custom fields."""
        metadata = CSRMetadata(
            requester="john.doe",
            custom_fields={"cost_center": "12345", "project": "alpha"},
        )
        result = metadata.to_dict()

        assert result["requester"] == "john.doe"
        assert result["cost_center"] == "12345"
        assert result["project"] == "alpha"


class TestCertificateResponse:
    """Tests for CertificateResponse class."""

    def test_save_certificate(self):
        """Test saving certificate to file."""
        cert_pem = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        response = CertificateResponse(certificate_pem=cert_pem)

        with tempfile.TemporaryDirectory() as tmpdir:
            cert_path = Path(tmpdir) / "cert.pem"
            response.save(cert_path)

            assert cert_path.exists()
            assert cert_path.read_text() == cert_pem

    def test_save_creates_parent_dirs(self):
        """Test that save creates parent directories."""
        cert_pem = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        response = CertificateResponse(certificate_pem=cert_pem)

        with tempfile.TemporaryDirectory() as tmpdir:
            cert_path = Path(tmpdir) / "subdir" / "nested" / "cert.pem"
            response.save(cert_path)

            assert cert_path.exists()

    def test_save_chain(self):
        """Test saving certificate chain."""
        cert_pem = "-----BEGIN CERTIFICATE-----\ncert\n-----END CERTIFICATE-----"
        chain_pem = "-----BEGIN CERTIFICATE-----\nchain\n-----END CERTIFICATE-----"
        response = CertificateResponse(certificate_pem=cert_pem, chain_pem=chain_pem)

        with tempfile.TemporaryDirectory() as tmpdir:
            chain_path = Path(tmpdir) / "chain.pem"
            response.save_chain(chain_path)

            assert chain_path.exists()
            assert chain_path.read_text() == chain_pem

    def test_save_chain_without_chain_raises(self):
        """Test that save_chain raises when no chain available."""
        response = CertificateResponse(certificate_pem="cert")

        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ValueError, match="No certificate chain"):
            response.save_chain(Path(tmpdir) / "chain.pem")

    def test_save_fullchain(self):
        """Test saving certificate with chain."""
        cert_pem = "-----BEGIN CERTIFICATE-----\ncert\n-----END CERTIFICATE-----"
        chain_pem = "-----BEGIN CERTIFICATE-----\nchain\n-----END CERTIFICATE-----"
        response = CertificateResponse(certificate_pem=cert_pem, chain_pem=chain_pem)

        with tempfile.TemporaryDirectory() as tmpdir:
            fullchain_path = Path(tmpdir) / "fullchain.pem"
            response.save_fullchain(fullchain_path)

            content = fullchain_path.read_text()
            assert cert_pem in content
            assert chain_pem in content

    def test_save_fullchain_without_chain(self):
        """Test saving fullchain when no chain (just saves cert)."""
        cert_pem = "-----BEGIN CERTIFICATE-----\ncert\n-----END CERTIFICATE-----"
        response = CertificateResponse(certificate_pem=cert_pem)

        with tempfile.TemporaryDirectory() as tmpdir:
            fullchain_path = Path(tmpdir) / "fullchain.pem"
            response.save_fullchain(fullchain_path)

            assert fullchain_path.read_text() == cert_pem
