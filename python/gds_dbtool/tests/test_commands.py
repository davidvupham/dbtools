"""Tests for various command modules."""

from __future__ import annotations

from gds_dbtool.main import app
from typer.testing import CliRunner

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
        assert result.exit_code == 5  # ExitCode.INVALID_INPUT
        assert "Unknown" in result.output

    def test_config_profiles(self):
        """Test config profiles command."""
        result = runner.invoke(app, ["config", "profiles"])
        assert result.exit_code == 0
        assert "default" in result.output

    def test_config_use_invalid_profile(self):
        """Test config use with invalid profile."""
        result = runner.invoke(app, ["config", "use", "nonexistent"])
        assert result.exit_code == 6  # ExitCode.RESOURCE_NOT_FOUND
        assert "not found" in result.output


class TestHealthCommands:
    """Tests for health command group."""

    def test_health_help(self):
        """Test health --help output."""
        result = runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        # Verify subcommands are listed
        assert "check" in result.output or "ad" in result.output

    def test_health_check_subcommand_help(self):
        """Test health check --help output has --deep."""
        result = runner.invoke(app, ["health", "check", "--help"])
        assert result.exit_code == 0
        assert "--deep" in result.output

    def test_health_ad_subcommand_exists(self):
        """Test that health ad subcommand exists."""
        result = runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "ad" in result.output


class TestSqlCommands:
    """Tests for sql command group."""

    def test_sql_help(self):
        """Test sql --help output."""
        result = runner.invoke(app, ["sql", "--help"])
        assert result.exit_code == 0
        assert "exec" in result.output

    def test_sql_exec_help(self):
        """Test sql exec --help output."""
        result = runner.invoke(app, ["sql", "exec", "--help"])
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


class TestInventoryCommands:
    """Tests for inventory command group."""

    def test_inventory_help(self):
        """Test inventory --help output."""
        result = runner.invoke(app, ["inventory", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "show" in result.output

    def test_inventory_list(self):
        """Test inventory list command."""
        result = runner.invoke(app, ["inventory", "list"])
        assert result.exit_code == 0
        assert "Inventory" in result.output or "postgres" in result.output

    def test_inventory_list_type_filter(self):
        """Test inventory list with --type filter."""
        result = runner.invoke(app, ["inventory", "list", "--type", "postgres"])
        assert result.exit_code == 0

    def test_inventory_show(self):
        """Test inventory show command."""
        result = runner.invoke(app, ["inventory", "show", "prod-postgres-01"])
        assert result.exit_code == 0
        assert "prod-postgres-01" in result.output
