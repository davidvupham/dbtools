"""
Pytest configuration and fixtures for gds_certs tests.
"""

import pytest


@pytest.fixture
def sample_csr_params():
    """Sample parameters for CSR generation."""
    return {
        "common_name": "test.example.com",
        "organization": "Test Organization",
        "organizational_unit": "IT Department",
        "country": "US",
        "state": "California",
        "locality": "San Francisco",
        "san_dns": ["test.example.com", "www.test.example.com"],
    }
