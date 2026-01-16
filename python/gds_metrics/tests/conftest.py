"""Pytest configuration and shared fixtures for gds_metrics tests."""

import pytest


@pytest.fixture
def sample_metric_labels() -> dict:
    """Return sample metric labels for testing."""
    return {
        "environment": "test",
        "service": "test-service",
        "instance": "localhost",
    }
