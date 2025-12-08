import uuid
from datetime import datetime
from typing import Any, Dict

from gds_benchmark.interfaces import BenchmarkRunner
from gds_benchmark.models import BenchmarkResult, BenchmarkStatus

from .cli import HammerDBExecutor
from .generator import ScriptGenerator
from .models import HammerDBConfig
from .parser import ResultParser


class HammerDBRunner(BenchmarkRunner):
    """Base class for HammerDB runners."""

    def __init__(self, executor: HammerDBExecutor = None):
        self.executor = executor or HammerDBExecutor()
        self.generator = ScriptGenerator()
        self.parser = ResultParser()

    def run(self, config: Dict[str, Any]) -> BenchmarkResult:
        """
        Executes the HammerDB benchmark.

        Args:
           config: Expects a dictionary that can be mapped to HammerDBConfig
                   and specific DB config.
        """
        # This is a template method. Subclasses should handle specific config parsing
        # and calling _execute.
        raise NotImplementedError("Subclasses must implement run()")

    def build_schema(self, config: Dict[str, Any]) -> BenchmarkResult:
        """
        Builds the schema (Drop and Recreate) for the target database.

        Args:
            config: Same config dictionary as run().
        """
        raise NotImplementedError("Subclasses must implement build_schema()")

    def run_with_rebuild(self, config: Dict[str, Any]) -> BenchmarkResult:
        """
        Orchestrates a schema build followed by a benchmark run.

        Args:
            config: Configuration dictionary.

        Returns:
            BenchmarkResult: The result of the benchmark run (build result is checked but not returned as primary).
                             If build fails, returns build result (which indicates failure).
        """
        # 1. Build Schema
        build_result = self.build_schema(config)
        if build_result.status != BenchmarkStatus.COMPLETED:
            return build_result

        # 2. Run Benchmark
        return self.run(config)

    def _execute(self, script_content: str, hammerdb_config: HammerDBConfig) -> BenchmarkResult:
        run_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            stdout = self.executor.run_script(script_content)
            result = self.parser.parse(stdout, hammerdb_config, run_id)
            result.start_time = start_time
            result.end_time = datetime.now()
            return result
        except Exception as e:
            return BenchmarkResult(
                run_id=run_id,
                tool_name="hammerdb",
                status=BenchmarkStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e),
            )

    def validate_config(self, config: Dict[str, Any]) -> bool:
        # basic validation
        return True
