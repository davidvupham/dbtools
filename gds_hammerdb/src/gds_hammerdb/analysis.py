from typing import Any, Dict, Optional

from gds_benchmark.models import BenchmarkResult, BenchmarkStatus


class ResultAnalyzer:
    """Analyzes HammerDB benchmark results."""

    def analyze(self, result: BenchmarkResult, baseline_nopm: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyzes the result against a baseline.

        Args:
           result: The benchmark result.
           baseline_nopm: Optional target NOPM to compare against.

        Returns:
           Dict containing analysis details (pass/fail, deviations).
        """
        analysis = {"status": "UNKNOWN", "findings": []}

        if result.status == BenchmarkStatus.FAILED:
            analysis["status"] = "FAIL"
            analysis["findings"].append("Benchmark run failed unexpectedly.")
            return analysis

        # Find NOPM metric
        nopm_metric = next((m for m in result.metrics if m.name == "NOPM"), None)

        if not nopm_metric:
            analysis["status"] = "WARN"
            analysis["findings"].append("No NOPM metric found in results.")
            return analysis

        current_nopm = nopm_metric.value
        analysis["nopm"] = current_nopm

        if baseline_nopm:
            delta = current_nopm - baseline_nopm
            percent_diff = (delta / baseline_nopm) * 100
            analysis["baseline_diff_percent"] = round(percent_diff, 2)

            if percent_diff < -10.0:
                analysis["status"] = "REGRESSION"
                analysis["findings"].append(f"Performance regression: {abs(percent_diff)}% below baseline.")
            elif percent_diff > 10.0:
                analysis["status"] = "IMPROVED"
                analysis["findings"].append(f"Performance improvement: {percent_diff}% above baseline.")
            else:
                analysis["status"] = "PASS"
                analysis["findings"].append("Performance within acceptable range of baseline.")
        else:
            analysis["status"] = "PASS"
            analysis["findings"].append("No baseline provided. Run checks passed.")

        return analysis
