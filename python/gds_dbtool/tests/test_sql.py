"""Tests for SQL execution commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestSqlExec:
    """Tests for sql exec command."""

    def test_exec_with_query(self, invoke):
        """Execute SQL query succeeds."""
        result = invoke(["sql", "exec", "prod-db", "SELECT 1"])
        assert result.exit_code == 0
        assert "Query Results" in result.output

    def test_exec_no_query_no_file(self, invoke):
        """Execute without query or file returns INVALID_INPUT."""
        result = invoke(["sql", "exec", "prod-db"])
        assert result.exit_code == ExitCode.INVALID_INPUT
        assert "Provide either" in result.output

    def test_exec_json_format(self, invoke):
        """Execute with JSON format outputs JSON."""
        result = invoke(["sql", "exec", "prod-db", "SELECT 1", "--format", "json"])
        assert result.exit_code == 0

    def test_exec_csv_format(self, invoke):
        """Execute with CSV format outputs CSV."""
        result = invoke(["sql", "exec", "prod-db", "SELECT 1", "--format", "csv"])
        assert result.exit_code == 0
        assert "id" in result.output

    def test_exec_yaml_format(self, invoke):
        """Execute with YAML format outputs YAML."""
        result = invoke(["sql", "exec", "prod-db", "SELECT 1", "--format", "yaml"])
        assert result.exit_code == 0

    def test_exec_quiet(self, invoke):
        """Execute in quiet mode shows tab-separated output."""
        result = invoke(["--quiet", "sql", "exec", "prod-db", "SELECT 1"])
        assert result.exit_code == 0

    def test_exec_with_reason(self, invoke):
        """Execute with audit reason shows reason."""
        result = invoke(["sql", "exec", "prod-db", "SELECT 1", "--reason", "TICKET-123"])
        assert result.exit_code == 0
        assert "TICKET-123" in result.output

    def test_exec_file_not_found(self, invoke):
        """Execute with nonexistent file returns RESOURCE_NOT_FOUND."""
        result = invoke(["sql", "exec", "prod-db", "--file", "/nonexistent.sql"])
        assert result.exit_code == ExitCode.RESOURCE_NOT_FOUND

    def test_exec_query_and_file(self, invoke, tmp_path):
        """Execute with both query and file returns INVALID_INPUT."""
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT 1")
        result = invoke(["sql", "exec", "prod-db", "SELECT 1", "--file", str(sql_file)])
        assert result.exit_code == ExitCode.INVALID_INPUT

    def test_exec_with_file(self, invoke, tmp_path):
        """Execute with SQL file succeeds."""
        sql_file = tmp_path / "query.sql"
        sql_file.write_text("SELECT * FROM users")
        result = invoke(["sql", "exec", "prod-db", "--file", str(sql_file)])
        assert result.exit_code == 0
