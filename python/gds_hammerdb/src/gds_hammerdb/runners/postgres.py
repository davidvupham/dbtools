from typing import Any

from gds_benchmark.models import BenchmarkResult
from gds_hammerdb.constants import BM_TPCC, BM_TPCH
from gds_hammerdb.models import HammerDBConfig, PostgresConnectionConfig
from gds_hammerdb.runners.base import HammerDBRunner


class PostgresRunner(HammerDBRunner):
    """HammerDB Runner for PostgreSQL."""

    def run(self, config: dict[str, Any]) -> BenchmarkResult:
        """
        Runs the benchmark against PostgreSQL.

        Args:
           config: Dictionary containing:
               - hammerdb: Dict matching HammerDBConfig
               - postgres: Dict matching PostgresConnectionConfig
        """
        h_config = HammerDBConfig(**config.get("hammerdb", {}))
        pg_config = PostgresConnectionConfig(**config.get("postgres", {}))

        # Generate Script
        if h_config.benchmark_type == BM_TPCC:
            script = self.generator.generate_postgres_tpcc(h_config, pg_config)
        elif h_config.benchmark_type == BM_TPCH:
            script = self.generator.generate_postgres_tpch(h_config, pg_config)
        else:
            raise ValueError(f"Unsupported benchmark type: {h_config.benchmark_type}")

        # Execute
        return self._execute(script, h_config)

    def build_schema(self, config: dict[str, Any]) -> BenchmarkResult:
        """
        Builds the schema for PostgreSQL.
        """
        h_config = HammerDBConfig(**config.get("hammerdb", {}))
        pg_config = PostgresConnectionConfig(**config.get("postgres", {}))

        script = self.generator.generate_build_script(h_config, pg_config)
        return self._execute(script, h_config)
