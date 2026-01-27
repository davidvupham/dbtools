"""Tests for maintenance commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestMaintStart:
    """Tests for maint start command."""

    def test_start_valid_task(self, invoke):
        """Start vacuum task succeeds."""
        result = invoke(["maint", "start", "vacuum", "prod-db"])
        assert result.exit_code == 0
        assert "Started" in result.output

    def test_start_invalid_task(self, invoke):
        """Start invalid task returns INVALID_INPUT."""
        result = invoke(["maint", "start", "invalid", "prod-db"])
        assert result.exit_code == ExitCode.INVALID_INPUT
        assert "Unknown task" in result.output

    def test_start_dry_run(self, invoke):
        """Start with dry-run shows preview."""
        result = invoke(["--dry-run", "maint", "start", "vacuum", "prod-db"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_start_quiet(self, invoke):
        """Start in quiet mode suppresses non-essential output."""
        result = invoke(["--quiet", "maint", "start", "reindex", "prod-db"])
        assert result.exit_code == 0

    def test_start_with_reason(self, invoke):
        """Start with audit reason shows reason."""
        result = invoke(["maint", "start", "analyze", "prod-db", "--reason", "TICK-1"])
        assert result.exit_code == 0
        assert "TICK-1" in result.output


class TestMaintStatus:
    """Tests for maint status command."""

    def test_status_normal(self, invoke):
        """Status shows task details table."""
        result = invoke(["maint", "status", "maint-123"])
        assert result.exit_code == 0
        assert "Task Status" in result.output

    def test_status_quiet(self, invoke):
        """Status in quiet mode shows just the status."""
        result = invoke(["--quiet", "maint", "status", "maint-123"])
        assert result.exit_code == 0
        assert "running" in result.output


class TestMaintList:
    """Tests for maint list command."""

    def test_list_normal(self, invoke):
        """List shows maintenance tasks table."""
        result = invoke(["maint", "list"])
        assert result.exit_code == 0
        assert "Maintenance Tasks" in result.output

    def test_list_quiet(self, invoke):
        """List in quiet mode shows tab-separated output."""
        result = invoke(["--quiet", "maint", "list"])
        assert result.exit_code == 0
        assert "maint-12345" in result.output
