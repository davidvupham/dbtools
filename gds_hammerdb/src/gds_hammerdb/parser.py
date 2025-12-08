import re

from gds_benchmark.models import BenchmarkResult, BenchmarkStatus

from .models import HammerDBConfig


class ResultParser:
    """Parses HammerDB output to extract metrics."""

    def parse(self, stdout: str, config: HammerDBConfig, run_id: str) -> BenchmarkResult:
        """
        Parses the stdout from HammerDB CLI.

        Args:
            stdout: The standard output from the run.
            config: The configuration used for the run.
            run_id: Unique identifier for the run.

        Returns:
            BenchmarkResult: The populated result object.
        """
        result = BenchmarkResult(
            run_id=run_id,
            tool_name="hammerdb",
            status=BenchmarkStatus.FAILED,  # Default to fail until confirmed pass
            start_time=None,  # In a real implementation we might capture this from logic or log
            raw_output=stdout,
        )

        # Check for success
        # HammerDB usually prints "TEST RESULT : PASS" or similar.
        # "System Under Test" output usually marks valid run.
        if "TEST RESULT : PASS" in stdout or "System Under Test" in stdout:
            result.status = BenchmarkStatus.COMPLETED

        # Extract NOPM
        # Pattern: "System Under Test : PostgreSQL" ... "Count : 123456" "NOPM : 123456" "TPM : 234567"
        # The output format can be tricky, it's often:
        # "NOPM": <value>
        # "TPM": <value>

        # Extract NOPM and TPM
        # In Autopilot, these might appear multiple times.
        # We will capture all valid samples.

        # Regex to find all occurrences of NOPM and TPM
        # Expected format lines like: "NOPM : 123456"
        nopm_matches = re.findall(r"NOPM\s*[:=]\s*(\d+)", stdout)
        tpm_matches = re.findall(r"TPM\s*[:=]\s*(\d+)", stdout)

        if nopm_matches:
            nopm_values = [float(v) for v in nopm_matches]
            peak_nopm = max(nopm_values)
            result.add_metric("NOPM", peak_nopm, "orders/min", "New Orders Per Minute (Peak)")
            result.metadata["nopm_samples"] = nopm_values

        if tpm_matches:
            tpm_values = [float(v) for v in tpm_matches]
            peak_tpm = max(tpm_values)
            result.add_metric("TPM", peak_tpm, "trans/min", "Transactions Per Minute (Peak)")
            result.metadata["tpm_samples"] = tpm_values

        return result
        return result
