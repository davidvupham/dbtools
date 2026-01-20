"""Shared fixtures for gds_benchmark tests."""

from datetime import datetime

import pytest

from gds_benchmark.models import BenchmarkResult, BenchmarkStatus


@pytest.fixture
def sample_result():
    """Create a sample BenchmarkResult for testing."""
    return BenchmarkResult(
        run_id="test-run-001",
        tool_name="test-tool",
        status=BenchmarkStatus.COMPLETED,
        start_time=datetime.now(),
    )
