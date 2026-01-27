"""Tests for health check commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestHealthCheck:
    """Tests for health check command."""

    def test_check_normal(self, invoke):
        """Health check displays table output."""
        result = invoke(["health", "check", "prod-db"])
        assert result.exit_code == 0
        assert "Health Check" in result.output

    def test_check_deep(self, invoke):
        """Deep health check includes extended diagnostics."""
        result = invoke(["health", "check", "prod-db", "--deep"])
        assert result.exit_code == 0
        assert "CPU Usage" in result.output

    def test_check_quiet(self, invoke):
        """Quiet mode shows minimal output."""
        result = invoke(["--quiet", "health", "check", "prod-db"])
        assert result.exit_code == 0
        assert "OK" in result.output


class TestHealthAd:
    """Tests for AD account check command."""

    def test_ad_no_flags(self, invoke):
        """AD check without --status or --verify-password returns INVALID_INPUT."""
        result = invoke(["health", "ad", "testuser"])
        assert result.exit_code == ExitCode.INVALID_INPUT

    def test_ad_status(self, invoke):
        """AD status check shows account status."""
        result = invoke(["health", "ad", "testuser", "--status"])
        assert result.exit_code == 0
        assert "Active" in result.output

    def test_ad_status_quiet(self, invoke):
        """AD status in quiet mode shows just the status."""
        result = invoke(["--quiet", "health", "ad", "testuser", "--status"])
        assert result.exit_code == 0
        assert "Active" in result.output
