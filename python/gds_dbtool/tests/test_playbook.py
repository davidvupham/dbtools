"""Tests for playbook commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestPlaybookRun:
    """Tests for playbook run command."""

    def test_run_valid_playbook(self, invoke):
        """Run valid playbook succeeds."""
        result = invoke(["playbook", "run", "os-patch", "host1"])
        assert result.exit_code == 0

    def test_run_invalid_playbook(self, invoke):
        """Run nonexistent playbook returns RESOURCE_NOT_FOUND."""
        result = invoke(["playbook", "run", "nonexistent", "host1"])
        assert result.exit_code == ExitCode.RESOURCE_NOT_FOUND
        assert "not found" in result.output

    def test_run_dry_run(self, invoke):
        """Run with dry-run shows preview."""
        result = invoke(["--dry-run", "playbook", "run", "os-patch", "host1"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_run_quiet(self, invoke):
        """Run in quiet mode suppresses extra output."""
        result = invoke(["--quiet", "playbook", "run", "os-patch", "host1"])
        assert result.exit_code == 0

    def test_run_with_extra_vars(self, invoke):
        """Run with extra vars shows variables."""
        result = invoke(["playbook", "run", "os-patch", "host1", "--extra-vars", "ver=1.2"])
        assert result.exit_code == 0
        assert "ver=1.2" in result.output

    def test_run_with_reason(self, invoke):
        """Run with audit reason shows reason."""
        result = invoke(["playbook", "run", "os-patch", "host1", "--reason", "TICK-1"])
        assert result.exit_code == 0
        assert "TICK-1" in result.output


class TestPlaybookList:
    """Tests for playbook list command."""

    def test_list_normal(self, invoke):
        """List shows available playbooks table."""
        result = invoke(["playbook", "list"])
        assert result.exit_code == 0
        assert "os-patch" in result.output

    def test_list_quiet(self, invoke):
        """List in quiet mode shows just names."""
        result = invoke(["--quiet", "playbook", "list"])
        assert result.exit_code == 0
        assert "os-patch" in result.output
