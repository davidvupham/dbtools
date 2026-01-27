"""Tests for the main CLI application."""

from __future__ import annotations

import os
from unittest.mock import patch

from gds_dbtool import __version__
from gds_dbtool.main import app
from typer.testing import CliRunner

runner = CliRunner()


class TestGlobalOptions:
    """Tests for global CLI options."""

    def test_help_flag(self):
        """Test that --help displays help text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Database Reliability Engineering CLI tool" in result.output

    def test_help_short_flag(self):
        """Test that -h displays help text."""
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "Database Reliability Engineering CLI tool" in result.output

    def test_version_flag(self):
        """Test that --version displays version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_short_flag(self):
        """Test that -V displays version."""
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_no_args_shows_help(self):
        """Test that running without arguments shows help."""
        result = runner.invoke(app, [])
        # Typer uses exit code 2 for no_args_is_help
        assert result.exit_code in (0, 2)
        assert "Usage:" in result.output

    def test_debug_flag(self):
        """Test that --debug enables debug mode."""
        result = runner.invoke(app, ["--debug", "--help"])
        # Debug mode doesn't affect help output, but shouldn't error
        assert result.exit_code == 0


class TestEnvironmentVariables:
    """Tests for environment variable handling."""

    def test_dbtool_debug_env_var(self):
        """Test DBTOOL_DEBUG environment variable."""
        with patch.dict(os.environ, {"DBTOOL_DEBUG": "1"}):
            result = runner.invoke(app, ["--help"])
            assert result.exit_code == 0

    def test_no_color_env_var(self):
        """Test NO_COLOR environment variable."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            result = runner.invoke(app, ["--help"])
            assert result.exit_code == 0

    def test_dbtool_no_color_env_var(self):
        """Test DBTOOL_NO_COLOR environment variable."""
        with patch.dict(os.environ, {"DBTOOL_NO_COLOR": "true"}):
            result = runner.invoke(app, ["--help"])
            assert result.exit_code == 0


class TestSubcommands:
    """Tests for subcommand registration."""

    def test_vault_subcommand_exists(self):
        """Test that vault subcommand is registered."""
        result = runner.invoke(app, ["vault", "--help"])
        assert result.exit_code == 0
        assert "Vault secret management" in result.output or "vault" in result.output.lower()

    def test_config_subcommand_exists(self):
        """Test that config subcommand is registered."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0

    def test_check_subcommand_exists(self):
        """Test that check subcommand is registered."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0

    def test_sql_subcommand_exists(self):
        """Test that sql subcommand is registered."""
        result = runner.invoke(app, ["sql", "--help"])
        assert result.exit_code == 0

    def test_shell_subcommand_exists(self):
        """Test that shell subcommand is registered."""
        result = runner.invoke(app, ["shell", "--help"])
        assert result.exit_code == 0

    def test_maint_subcommand_exists(self):
        """Test that maint subcommand is registered."""
        result = runner.invoke(app, ["maint", "--help"])
        assert result.exit_code == 0

    def test_playbook_subcommand_exists(self):
        """Test that playbook subcommand is registered."""
        result = runner.invoke(app, ["playbook", "--help"])
        assert result.exit_code == 0

    def test_tf_subcommand_exists(self):
        """Test that tf subcommand is registered."""
        result = runner.invoke(app, ["tf", "--help"])
        assert result.exit_code == 0

    def test_lb_subcommand_exists(self):
        """Test that lb subcommand is registered."""
        result = runner.invoke(app, ["lb", "--help"])
        assert result.exit_code == 0


class TestAliases:
    """Tests for command aliases."""

    def test_vt_alias_for_vault(self):
        """Test that vt is an alias for vault."""
        result = runner.invoke(app, ["vt", "--help"])
        assert result.exit_code == 0

    def test_cfg_alias_for_config(self):
        """Test that cfg is an alias for config."""
        result = runner.invoke(app, ["cfg", "--help"])
        assert result.exit_code == 0

    def test_ck_alias_for_check(self):
        """Test that ck is an alias for check."""
        result = runner.invoke(app, ["ck", "--help"])
        assert result.exit_code == 0

    def test_sh_alias_for_shell(self):
        """Test that sh is an alias for shell."""
        result = runner.invoke(app, ["sh", "--help"])
        assert result.exit_code == 0

    def test_pb_alias_for_playbook(self):
        """Test that pb is an alias for playbook."""
        result = runner.invoke(app, ["pb", "--help"])
        assert result.exit_code == 0
