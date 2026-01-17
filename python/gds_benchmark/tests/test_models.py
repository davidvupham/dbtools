from gds_benchmark.models import BenchmarkResult, BenchmarkStatus


def test_benchmark_result_creation():
    result = BenchmarkResult(
        run_id="test-run",
        tool_name="test-tool",
        status=BenchmarkStatus.PENDING,
        start_time=None,
    )
    assert result.run_id == "test-run"
    assert result.status == BenchmarkStatus.PENDING


def test_benchmark_result_add_metric():
    result = BenchmarkResult(
        run_id="test-run",
        tool_name="test-tool",
        status=BenchmarkStatus.COMPLETED,
        start_time=None,
    )
    result.add_metric("NOPM", 100.0, "orders/min", "New Orders Per Minute")

    assert len(result.metrics) == 1
    assert result.metrics[0].name == "NOPM"
    assert result.metrics[0].value == 100.0
