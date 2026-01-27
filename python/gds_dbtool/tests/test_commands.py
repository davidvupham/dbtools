"""Tests for various command modules."""
from __future__ import annotations

from typer.testing import CliRunner

from gds_dbtool.main import app

runner = CliRunner()


class TestConfigCommands:
    """Tests for config command group."""

    def test_config_list(self):
        """Test config list command."""
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "config_path" in result.output or "Configuration" in result.output

    def test_config_get_profile(self):
        """Test config get command."""
        result = runner.invoke(app, ["config", "get", "profile"])
        assert result.exit_code == 0
        assert "default" in result.output

    def test_config_get_unknown_key(self):
        """Test config get with unknown key."""
        result = runner.invoke(app, ["config", "get", "unknown_key"])
        assert result.exit_code == 1
        assert "Unknown" in result.output

    def test_config_profiles(self):
        """Test config profiles command."""
        result = runner.invoke(app, ["config", "profiles"])
        assert result.exit_code == 0
        assert "default" in result.output

    def test_config_use_invalid_profile(self):
        """Test config use with invalid profile."""
        result = runner.invoke(app, ["config", "use", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestCheckCommands:
    """Tests for check command group."""

    def test_check_help(self):
        """Test check --help output."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "--deep" in result.output

    def test_check_ad_subcommand_exists(self):
        """Test that check ad subcommand exists."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "ad" in result.output


class TestSqlCommands:
    """Tests for sql command group."""

    def test_sql_help(self):
        """Test sql --help output."""
        result = runner.invoke(app, ["sql", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.output
        assert "--file" in result.output
        assert "--reason" in result.output


class TestShellCommands:
    """Tests for shell command group."""

    def test_shell_help(self):
        """Test shell --help output."""
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0
        assert "TARGET" in result.output


class TestMaintCommands:
    """Tests for maint command group."""

    def test_maint_help(self):
        """Test maint --help output."""
        result = runner.invoke(app, ["maint", "--help"])
        assert result.exit_code == 0
        assert "start" in result.output
        assert "status" in result.output

    def test_maint_start_help(self):
        """Test maint start --help output."""
        result = runner.invoke(app, ["maint", "start", "--help"])
        assert result.exit_code == 0
        assert "vacuum" in result.output or "TASK" in result.output


class TestPlaybookCommands:
    """Tests for playbook command group."""

    def test_playbook_help(self):
        """Test playbook --help output."""
        result = runner.invoke(app, ["playbook", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        assert "list" in result.output

    def test_playbook_list(self):
        """Test playbook list command."""
        result = runner.invoke(app, ["playbook", "list"])
        assert result.exit_code == 0
        assert "Playbook" in result.output or "os-patch" in result.output


class TestTerraformCommands:
    """Tests for tf command group."""

    def test_tf_help(self):
        """Test tf --help output."""
        result = runner.invoke(app, ["tf", "--help"])
        assert result.exit_code == 0
        assert "plan" in result.output
        assert "apply" in result.output

    def test_tf_plan_help(self):
        """Test tf plan --help output."""
        result = runner.invoke(app, ["tf", "plan", "--help"])
        assert result.exit_code == 0
        assert "PROJECT" in result.output
        assert "ENV" in result.output


class TestLiquibaseCommands:
    """Tests for lb command group."""

    def test_lb_help(self):
        """Test lb --help output."""
        result = runner.invoke(app, ["lb", "--help"])
        assert result.exit_code == 0
        assert "update" in result.output
        assert "rollback" in result.output
        assert "status" in result.output

    def test_lb_update_help(self):
        """Test lb update --help output."""
        result = runner.invoke(app, ["lb", "update", "--help"])
        assert result.exit_code == 0
        assert "--count" in result.output
        assert "--reason" in result.output
