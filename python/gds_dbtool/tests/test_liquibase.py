"""Tests for Liquibase commands."""

from __future__ import annotations


class TestLiquibaseUpdate:
    """Tests for lb update command."""

    def test_update_normal(self, invoke):
        """Update shows operation details."""
        result = invoke(["lb", "update", "myproj", "dev"])
        assert result.exit_code == 0
        assert "Liquibase Update" in result.output

    def test_update_quiet(self, invoke):
        """Update in quiet mode suppresses details."""
        result = invoke(["--quiet", "lb", "update", "myproj", "dev"])
        assert result.exit_code == 0

    def test_update_dry_run(self, invoke):
        """Update with dry-run shows SQL preview."""
        result = invoke(["--dry-run", "lb", "update", "myproj", "dev"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_update_with_count(self, invoke):
        """Update with --count shows changeset count."""
        result = invoke(["lb", "update", "myproj", "dev", "--count", "2"])
        assert result.exit_code == 0
        assert "2" in result.output

    def test_update_with_reason(self, invoke):
        """Update with audit reason shows reason."""
        result = invoke(["lb", "update", "myproj", "dev", "--reason", "TICK-1"])
        assert result.exit_code == 0
        assert "TICK-1" in result.output

    def test_update_prod_with_force(self, invoke):
        """Update prod with --force skips confirmation."""
        result = invoke(["lb", "update", "myproj", "prod", "--force"])
        assert result.exit_code == 0


class TestLiquibaseRollback:
    """Tests for lb rollback command."""

    def test_rollback_dry_run(self, invoke):
        """Rollback with dry-run shows SQL preview."""
        result = invoke(["--dry-run", "lb", "rollback", "myproj", "dev"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_rollback_normal_with_force(self, invoke):
        """Rollback with force skips confirmation."""
        result = invoke(["lb", "rollback", "myproj", "dev", "--force"])
        assert result.exit_code == 0
        assert "Liquibase Rollback" in result.output

    def test_rollback_quiet_with_force(self, invoke):
        """Rollback quiet mode with force."""
        result = invoke(["--quiet", "lb", "rollback", "myproj", "dev", "--force"])
        assert result.exit_code == 0

    def test_rollback_with_reason(self, invoke):
        """Rollback with audit reason shows reason."""
        result = invoke(["lb", "rollback", "myproj", "dev", "--force", "--reason", "R1"])
        assert result.exit_code == 0
        assert "R1" in result.output


class TestLiquibaseStatus:
    """Tests for lb status command."""

    def test_status_normal(self, invoke):
        """Status shows pending and applied changesets."""
        result = invoke(["lb", "status", "myproj", "dev"])
        assert result.exit_code == 0
        assert "Pending" in result.output

    def test_status_quiet(self, invoke):
        """Status in quiet mode shows counts."""
        result = invoke(["--quiet", "lb", "status", "myproj", "dev"])
        assert result.exit_code == 0
        assert "pending:" in result.output


class TestLiquibaseValidate:
    """Tests for lb validate command."""

    def test_validate_normal(self, invoke):
        """Validate shows validation result."""
        result = invoke(["lb", "validate", "myproj"])
        assert result.exit_code == 0
        assert "passed" in result.output

    def test_validate_quiet(self, invoke):
        """Validate in quiet mode produces no extra output."""
        result = invoke(["--quiet", "lb", "validate", "myproj"])
        assert result.exit_code == 0
