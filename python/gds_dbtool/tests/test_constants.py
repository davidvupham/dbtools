"""Tests for constants and exit codes."""

from __future__ import annotations

from gds_dbtool.constants import ErrorMessage, ExitCode


class TestExitCodes:
    """Tests for exit code constants."""

    def test_success_is_zero(self):
        """Test that SUCCESS is 0."""
        assert ExitCode.SUCCESS == 0

    def test_general_error_is_one(self):
        """Test that GENERAL_ERROR is 1."""
        assert ExitCode.GENERAL_ERROR == 1

    def test_auth_error_is_two(self):
        """Test that AUTH_ERROR is 2."""
        assert ExitCode.AUTH_ERROR == 2

    def test_connection_error_is_three(self):
        """Test that CONNECTION_ERROR is 3."""
        assert ExitCode.CONNECTION_ERROR == 3

    def test_permission_denied_is_four(self):
        """Test that PERMISSION_DENIED is 4."""
        assert ExitCode.PERMISSION_DENIED == 4

    def test_invalid_input_is_five(self):
        """Test that INVALID_INPUT is 5."""
        assert ExitCode.INVALID_INPUT == 5

    def test_resource_not_found_is_six(self):
        """Test that RESOURCE_NOT_FOUND is 6."""
        assert ExitCode.RESOURCE_NOT_FOUND == 6

    def test_exit_codes_are_unique(self):
        """Test that all exit codes are unique."""
        codes = [e.value for e in ExitCode]
        assert len(codes) == len(set(codes))


class TestErrorMessages:
    """Tests for error message templates."""

    def test_vault_auth_failed_format(self):
        """Test VAULT_AUTH_FAILED message formatting."""
        msg = ErrorMessage.VAULT_AUTH_FAILED.format(details="token expired")
        assert "VAULT_AUTH_FAILED" in msg
        assert "token expired" in msg

    def test_target_not_found_format(self):
        """Test TARGET_NOT_FOUND message formatting."""
        msg = ErrorMessage.TARGET_NOT_FOUND.format(target="prod-db-01")
        assert "TARGET_NOT_FOUND" in msg
        assert "prod-db-01" in msg

    def test_connection_timeout_format(self):
        """Test CONNECTION_TIMEOUT message formatting."""
        msg = ErrorMessage.CONNECTION_TIMEOUT.format(target="db.example.com")
        assert "CONNECTION_TIMEOUT" in msg
        assert "db.example.com" in msg

    def test_permission_denied_format(self):
        """Test PERMISSION_DENIED message formatting."""
        msg = ErrorMessage.PERMISSION_DENIED.format(resource="secret/data/passwords")
        assert "PERMISSION_DENIED" in msg
        assert "secret/data/passwords" in msg
