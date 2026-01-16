"""
Data models for gds_certs package.

This module defines the data structures used throughout the package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class SubjectInfo:
    """Certificate subject information."""

    common_name: str
    organization: str | None = None
    organizational_unit: str | None = None
    country: str | None = None
    state: str | None = None
    locality: str | None = None
    email: str | None = None


@dataclass
class CertificateResponse:
    """Response from CA after certificate issuance."""

    certificate_pem: str
    chain_pem: str | None = None
    serial_number: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    request_id: str | None = None

    def save(self, path: str | Path) -> None:
        """Save certificate to file in PEM format."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.certificate_pem)

    def save_chain(self, path: str | Path) -> None:
        """Save certificate chain to file in PEM format."""
        if not self.chain_pem:
            raise ValueError("No certificate chain available")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.chain_pem)

    def save_fullchain(self, path: str | Path) -> None:
        """Save certificate with chain to file in PEM format."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.certificate_pem
        if self.chain_pem:
            content += "\n" + self.chain_pem
        path.write_text(content)


@dataclass
class CSRMetadata:
    """Metadata to include with CSR submission."""

    requester: str | None = None
    department: str | None = None
    environment: str | None = None
    application: str | None = None
    ticket_id: str | None = None
    custom_fields: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for API submission."""
        result = {}
        if self.requester:
            result["requester"] = self.requester
        if self.department:
            result["department"] = self.department
        if self.environment:
            result["environment"] = self.environment
        if self.application:
            result["application"] = self.application
        if self.ticket_id:
            result["ticket_id"] = self.ticket_id
        result.update(self.custom_fields)
        return result
