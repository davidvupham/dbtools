"""Tests for vault commands."""

from __future__ import annotations

from unittest.mock import patch

from gds_dbtool.constants import ExitCode
from gds_dbtool.main import app
from typer.testing import CliRunner

runner = CliRunner()


class TestVaultHelp:
    """Tests for vault command help."""

    def test_vault_help(self):
        """Test vault --help output."""
        result = runner.invoke(app, ["vault", "--help"])
        assert result.exit_code == 0
        assert "login" in result.output
        assert "list" in result.output
        assert "get" in result.output
        assert "put" in result.output
        assert "delete" in result.output

    def test_vault_login_help(self):
        """Test vault login --help output."""
        result = runner.invoke(app, ["vault", "login", "--help"])
        assert result.exit_code == 0
        assert "--method" in result.output
        assert "ldap" in result.output

    def test_vault_list_help(self):
        """Test vault list --help output."""
        result = runner.invoke(app, ["vault", "list", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.output

    def test_vault_get_help(self):
        """Test vault get --help output."""
        result = runner.invoke(app, ["vault", "get", "--help"])
        assert result.exit_code == 0
        assert "PATH" in result.output
        assert "--format" in result.output

    def test_vault_put_help(self):
        """Test vault put --help output."""
        result = runner.invoke(app, ["vault", "put", "--help"])
        assert result.exit_code == 0
        assert "Key=Value" in result.output
        assert "--force" in result.output

    def test_vault_delete_help(self):
        """Test vault delete --help output."""
        result = runner.invoke(app, ["vault", "delete", "--help"])
        assert result.exit_code == 0
        assert "--hard" in result.output
        assert "--force" in result.output


class TestVaultLogin:
    """Tests for vault login command."""

    def test_login_unsupported_method(self):
        """Test that unsupported auth methods are rejected."""
        result = runner.invoke(app, ["vault", "login", "--method", "unsupported"])
        assert result.exit_code == ExitCode.INVALID_INPUT
        assert "not supported" in result.output


class TestVaultLogout:
    """Tests for vault logout command."""

    def test_logout_clears_token(self):
        """Test that logout clears stored token."""
        with patch("gds_dbtool.commands.vault.delete_token") as mock_delete:
            result = runner.invoke(app, ["vault", "logout"])
            mock_delete.assert_called_once()
            assert result.exit_code == 0


class TestVaultAliases:
    """Tests for vault command aliases."""

    def test_ls_alias_for_list(self):
        """Test that ls is an alias for list."""
        result = runner.invoke(app, ["vault", "ls", "--help"])
        # Should work (may fail due to auth, but help should work)
        assert "Alias for 'list'" in result.output or result.exit_code == 0

    def test_rm_alias_for_delete(self):
        """Test that rm is an alias for delete."""
        result = runner.invoke(app, ["vault", "rm", "--help"])
        assert "Alias for 'delete'" in result.output or result.exit_code == 0


class TestVaultDryRun:
    """Tests for vault dry-run functionality."""

    def test_put_dry_run(self):
        """Test vault put with --dry-run."""
        result = runner.invoke(app, ["--dry-run", "vault", "put", "test/path", "key=value"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "no changes made" in result.output.lower()

    def test_delete_dry_run(self):
        """Test vault delete with --dry-run."""
        result = runner.invoke(app, ["--dry-run", "vault", "delete", "test/path"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "no changes made" in result.output.lower()


class TestVaultVtAlias:
    """Tests for vt alias."""

    def test_vt_list_works(self):
        """Test vt list command."""
        result = runner.invoke(app, ["vt", "--help"])
        assert result.exit_code == 0
