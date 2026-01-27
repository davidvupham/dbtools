"""Tests for Terraform commands."""

from __future__ import annotations

from gds_dbtool.constants import ExitCode


class TestTerraformPlan:
    """Tests for tf plan command."""

    def test_plan_normal(self, invoke):
        """Plan shows terraform plan output."""
        result = invoke(["tf", "plan", "myproj", "dev"])
        assert result.exit_code == 0
        assert "Terraform Plan" in result.output

    def test_plan_quiet(self, invoke):
        """Plan in quiet mode suppresses status."""
        result = invoke(["--quiet", "tf", "plan", "myproj", "dev"])
        assert result.exit_code == 0

    def test_plan_with_vars(self, invoke):
        """Plan with variables shows vars."""
        result = invoke(["tf", "plan", "myproj", "dev", "--var", "x=1"])
        assert result.exit_code == 0
        assert "x=1" in result.output


class TestTerraformApply:
    """Tests for tf apply command."""

    def test_apply_dry_run(self, invoke):
        """Apply with dry-run shows preview."""
        result = invoke(["--dry-run", "tf", "apply", "myproj", "dev"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_apply_dry_run_quiet(self, invoke):
        """Apply dry-run in quiet mode."""
        result = invoke(["--quiet", "--dry-run", "tf", "apply", "myproj", "dev"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_apply_dry_run_with_vars(self, invoke):
        """Apply dry-run shows variables."""
        result = invoke(["--dry-run", "tf", "apply", "myproj", "dev", "--var", "k=v"])
        assert result.exit_code == 0
        assert "k=v" in result.output

    def test_apply_dry_run_with_reason(self, invoke):
        """Apply dry-run with audit reason shows reason."""
        result = invoke(["--dry-run", "tf", "apply", "myproj", "dev", "--reason", "T1"])
        assert result.exit_code == 0
        assert "T1" in result.output


class TestTerraformOutput:
    """Tests for tf output command."""

    def test_output_table(self, invoke):
        """Output shows table format."""
        result = invoke(["tf", "output", "myproj", "dev"])
        assert result.exit_code == 0
        assert "Terraform Outputs" in result.output

    def test_output_json(self, invoke):
        """Output shows JSON format."""
        result = invoke(["tf", "output", "myproj", "dev", "--format", "json"])
        assert result.exit_code == 0
        assert "db_endpoint" in result.output

    def test_output_specific_name(self, invoke):
        """Output retrieves specific output value."""
        result = invoke(["tf", "output", "myproj", "dev", "db_endpoint"])
        assert result.exit_code == 0
        assert "prod-db.example.com" in result.output

    def test_output_name_not_found(self, invoke):
        """Output with unknown name returns RESOURCE_NOT_FOUND."""
        result = invoke(["tf", "output", "myproj", "dev", "nonexistent"])
        assert result.exit_code == ExitCode.RESOURCE_NOT_FOUND
        assert "not found" in result.output
