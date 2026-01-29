from typing import Any

from gds_benchmark.models import BenchmarkResult

from gds_hammerdb.constants import BM_TPCC, BM_TPCH
from gds_hammerdb.models import HammerDBConfig, MSSQLConnectionConfig
from gds_hammerdb.runners.base import HammerDBRunner


class MSSQLRunner(HammerDBRunner):
    """HammerDB Runner for SQL Server."""

    def run(self, config: dict[str, Any]) -> BenchmarkResult:
        """
        Runs the benchmark against SQL Server.

        Args:
           config: Dictionary containing:
               - hammerdb: Dict matching HammerDBConfig
               - mssql: Dict matching MSSQLConnectionConfig
        """
        h_config = HammerDBConfig(**config.get("hammerdb", {}))
        ms_config = MSSQLConnectionConfig(**config.get("mssql", {}))

        # Generate Script
        if h_config.benchmark_type == BM_TPCC:
            script = self.generator.generate_mssql_tpcc(h_config, ms_config)
        elif h_config.benchmark_type == BM_TPCH:
            script = self.generator.generate_mssql_tpch(h_config, ms_config)
        else:
            raise ValueError(f"Unsupported benchmark type: {h_config.benchmark_type}")

        # Execute
        return self._execute(script, h_config)

    def build_schema(self, config: dict[str, Any]) -> BenchmarkResult:
        """
        Builds the schema for SQL Server.
        """
        h_config = HammerDBConfig(**config.get("hammerdb", {}))
        ms_config = MSSQLConnectionConfig(**config.get("mssql", {}))

        script = self.generator.generate_build_script(h_config, ms_config)
        return self._execute(script, h_config)
