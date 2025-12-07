from typing import Any

from .constants import DB_MSSQL_LINUX, DB_POSTGRES
from .models import HammerDBConfig, MSSQLConnectionConfig, PostgresConnectionConfig


class ScriptGenerator:
    """Generates Tcl scripts for HammerDB."""

    @staticmethod
    def _format_diset(component: str, parameter: str, value: Any) -> str:
        return f'diset {component} {parameter} "{value}"'

    def generate_postgres_tpcc(
        self, config: HammerDBConfig, pg_config: PostgresConnectionConfig
    ) -> str:
        lines = []
        lines.append("#!/bin/tclsh")
        lines.append('puts "SETTING CONFIGURATION"')
        lines.append(f"dbset db {DB_POSTGRES}")

        # Connection
        lines.append(self._format_diset("connection", "pg_host", pg_config.host))
        lines.append(self._format_diset("connection", "pg_port", pg_config.port))
        lines.append(
            self._format_diset("connection", "pg_user", pg_config.superuser)
        )  # Note: checks if this is for build or run
        if pg_config.password:
            lines.append(
                self._format_diset("connection", "pg_pass", pg_config.password)
            )

        # Config
        # Note: In HammerDB, some params like pg_count_ware are for building,
        # others for running. Assuming this is for RUNNING workload.
        lines.append(self._format_diset("tpcc", "pg_rampup", config.rampup_minutes))
        lines.append(self._format_diset("tpcc", "pg_duration", config.duration_minutes))

        # Logging to temp is crucial for CLI performance
        lines.append("vuset logtotemp 1")

        lines.append('puts "LOADING SCRIPT"')
        lines.append("loadscript")

        lines.append('puts "STARTING RUN"')
        lines.append(f"vuset vu {config.virtual_users}")
        lines.append("vucreate")
        lines.append("vurun")
        lines.append("vudestroy")
        lines.append('puts "RUN COMPLETE"')

        return "\n".join(lines)

    def generate_mssql_tpcc(
        self, config: HammerDBConfig, mssql_config: MSSQLConnectionConfig
    ) -> str:
        lines = []
        lines.append("#!/bin/tclsh")
        lines.append('puts "SETTING CONFIGURATION"')
        lines.append(f"dbset db {DB_MSSQL_LINUX}")

        # Connection
        lines.append(
            self._format_diset("connection", "mssqls_server", mssql_config.server)
        )
        lines.append(self._format_diset("connection", "mssqls_uid", mssql_config.uid))
        if mssql_config.password:
            lines.append(
                self._format_diset("connection", "mssqls_pass", mssql_config.password)
            )

        lines.append(self._format_diset("tpcc", "mssqls_rampup", config.rampup_minutes))
        lines.append(
            self._format_diset("tpcc", "mssqls_duration", config.duration_minutes)
        )

        lines.append("vuset logtotemp 1")
        lines.append('puts "LOADING SCRIPT"')
        lines.append("loadscript")

        lines.append('puts "STARTING RUN"')
        lines.append(f"vuset vu {config.virtual_users}")
        lines.append("vucreate")
        lines.append("vurun")
        lines.append("vudestroy")
        lines.append('puts "RUN COMPLETE"')

        return "\n".join(lines)

    def generate_postgres_tpch(
        self, config: HammerDBConfig, pg_config: PostgresConnectionConfig
    ) -> str:
        """Generate TPC-H script for PostgreSQL."""
        lines = []
        lines.append("#!/bin/tclsh")
        lines.append('puts "SETTING CONFIGURATION"')
        lines.append(f"dbset db {DB_POSTGRES}")
        lines.append("dbset bm TPC-H")

        # Connection
        lines.append(self._format_diset("connection", "pg_host", pg_config.host))
        lines.append(self._format_diset("connection", "pg_port", pg_config.port))
        lines.append(self._format_diset("connection", "pg_user", pg_config.superuser))
        if pg_config.password:
            lines.append(
                self._format_diset("connection", "pg_pass", pg_config.password)
            )

        # TPC-H Settings
        lines.append(
            self._format_diset("tpch", "pg_scale_fact", config.tpch_scale_factor)
        )
        lines.append(self._format_diset("tpch", "pg_total_querysets", 1))

        lines.append("vuset logtotemp 1")
        lines.append('puts "LOADING SCRIPT"')
        lines.append("loadscript")

        lines.append('puts "STARTING RUN"')
        lines.append(f"vuset vu {config.virtual_users}")
        lines.append("vucreate")
        lines.append("vurun")
        lines.append("vudestroy")
        lines.append('puts "RUN COMPLETE"')

        return "\n".join(lines)

    def generate_mssql_tpch(
        self, config: HammerDBConfig, mssql_config: MSSQLConnectionConfig
    ) -> str:
        """Generate TPC-H script for SQL Server."""
        lines = []
        lines.append("#!/bin/tclsh")
        lines.append('puts "SETTING CONFIGURATION"')
        lines.append(f"dbset db {DB_MSSQL_LINUX}")
        lines.append("dbset bm TPC-H")

        # Connection
        lines.append(
            self._format_diset("connection", "mssqls_server", mssql_config.server)
        )
        lines.append(self._format_diset("connection", "mssqls_uid", mssql_config.uid))
        if mssql_config.password:
            lines.append(
                self._format_diset("connection", "mssqls_pass", mssql_config.password)
            )

        # TPC-H Settings
        lines.append(
            self._format_diset("tpch", "mssqls_scale_fact", config.tpch_scale_factor)
        )

        lines.append("vuset logtotemp 1")
        lines.append('puts "LOADING SCRIPT"')
        lines.append("loadscript")

        lines.append('puts "STARTING RUN"')
        lines.append(f"vuset vu {config.virtual_users}")
        lines.append("vucreate")
        lines.append("vurun")
        lines.append("vudestroy")
        lines.append('puts "RUN COMPLETE"')

        return "\n".join(lines)

    def generate_build_script(self, config: HammerDBConfig, db_config: Any) -> str:
        """Generate schema build script (drops and recreates database)."""
        lines = []
        lines.append("#!/bin/tclsh")
        lines.append('puts "SETTING CONFIGURATION FOR SCHEMA BUILD"')

        if config.db_type == DB_POSTGRES:
            lines.append(f"dbset db {DB_POSTGRES}")
            lines.append(self._format_diset("connection", "pg_host", db_config.host))
            lines.append(self._format_diset("connection", "pg_port", db_config.port))
            lines.append(
                self._format_diset("connection", "pg_user", db_config.superuser)
            )
            if db_config.password:
                lines.append(
                    self._format_diset("connection", "pg_pass", db_config.password)
                )

            if config.benchmark_type == "TPC-C":
                lines.append("dbset bm TPC-C")
                lines.append(self._format_diset("tpcc", "pg_count_ware", 10))
                lines.append(
                    self._format_diset("tpcc", "pg_num_vu", config.virtual_users)
                )
            else:
                lines.append("dbset bm TPC-H")
                lines.append(
                    self._format_diset(
                        "tpch", "pg_scale_fact", config.tpch_scale_factor
                    )
                )
                lines.append(
                    self._format_diset("tpch", "pg_num_vu", config.virtual_users)
                )

        elif config.db_type == DB_MSSQL_LINUX:
            lines.append(f"dbset db {DB_MSSQL_LINUX}")
            lines.append(
                self._format_diset("connection", "mssqls_server", db_config.server)
            )
            lines.append(self._format_diset("connection", "mssqls_uid", db_config.uid))
            if db_config.password:
                lines.append(
                    self._format_diset("connection", "mssqls_pass", db_config.password)
                )

            if config.benchmark_type == "TPC-C":
                lines.append("dbset bm TPC-C")
                lines.append(self._format_diset("tpcc", "mssqls_count_ware", 10))
                lines.append(
                    self._format_diset("tpcc", "mssqls_num_vu", config.virtual_users)
                )
            else:
                lines.append("dbset bm TPC-H")
                lines.append(
                    self._format_diset(
                        "tpch", "mssqls_scale_fact", config.tpch_scale_factor
                    )
                )
                lines.append(
                    self._format_diset("tpch", "mssqls_num_vu", config.virtual_users)
                )

        lines.append('puts "BUILDING SCHEMA"')
        lines.append("buildschema")
        lines.append("waittocomplete")
        lines.append('puts "BUILD COMPLETE"')

        return "\n".join(lines)
