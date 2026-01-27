"""Tests for shell commands."""

from __future__ import annotations


class TestShellConnect:
    """Tests for shell connect command."""

    def test_shell_normal(self, invoke):
        """Shell connect displays connection info."""
        result = invoke(["shell", "prod-postgres"])
        assert result.exit_code == 0
        assert "Would execute" in result.output

    def test_shell_quiet(self, invoke):
        """Shell connect in quiet mode skips status messages."""
        result = invoke(["--quiet", "shell", "prod-postgres"])
        assert result.exit_code == 0
        assert "Would execute" in result.output


class TestShellLogin:
    """Tests for shell login subcommand."""

    def test_login_redirects(self, invoke):
        """Login redirects to vault login."""
        result = invoke(["shell", "prod-db", "login"])
        assert result.exit_code == 0
        assert "vault login" in result.output
