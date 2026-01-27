"""Tests for alert triage commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestAlertTriage:
    """Tests for alert triage command."""

    def test_triage_no_args(self, invoke):
        """Triage without alert ID or target returns INVALID_INPUT."""
        result = invoke(["alert", "triage"])
        assert result.exit_code == ExitCode.INVALID_INPUT
        assert "Provide either" in result.output

    def test_triage_with_alert_id(self, invoke):
        """Triage with alert ID succeeds."""
        result = invoke(["alert", "triage", "ALT-123"])
        assert result.exit_code == 0
        assert "Triage complete" in result.output

    def test_triage_with_target(self, invoke):
        """Triage with --target succeeds."""
        result = invoke(["alert", "triage", "--target", "prod-db"])
        assert result.exit_code == 0
        assert "Triage complete" in result.output
