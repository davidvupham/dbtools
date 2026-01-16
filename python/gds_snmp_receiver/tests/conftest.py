"""Pytest configuration and shared fixtures for gds_snmp_receiver tests."""

import pytest


@pytest.fixture
def sample_snmp_config() -> dict:
    """Return sample SNMP configuration for testing."""
    return {
        "host": "0.0.0.0",
        "port": 162,
        "community": "public",
    }


@pytest.fixture
def sample_trap_oid() -> str:
    """Return a sample SNMP trap OID for testing."""
    return "1.3.6.1.4.1.12345.1.1"
