"""Tests for gds_mongodb.rhel_validator module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from gds_mongodb.rhel_validator import (
    CheckResult,
    CheckStatus,
    RHELConfigValidator,
    ValidationReport,
)

# ---------------------------------------------------------------------------
# CheckResult / ValidationReport unit tests
# ---------------------------------------------------------------------------


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_defaults(self):
        """CheckResult has sensible defaults for optional fields."""
        result = CheckResult(
            name="test",
            description="A test check",
            status=CheckStatus.PASS,
            expected="1",
            actual="1",
        )
        assert result.message == ""
        assert result.reference == ""

    def test_all_fields(self):
        """CheckResult stores all provided values."""
        result = CheckResult(
            name="sysctl_vm.swappiness",
            description="Kernel swap aggressiveness",
            status=CheckStatus.FAIL,
            expected="1",
            actual="60",
            message="Set vm.swappiness = 1",
            reference="https://example.com",
        )
        assert result.name == "sysctl_vm.swappiness"
        assert result.status == CheckStatus.FAIL
        assert result.actual == "60"


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    @pytest.fixture
    def mixed_report(self) -> ValidationReport:
        """Report with a mix of statuses."""
        report = ValidationReport(hostname="test-host")
        report.checks = [
            CheckResult("a", "desc", CheckStatus.PASS, "1", "1"),
            CheckResult("b", "desc", CheckStatus.PASS, "1", "1"),
            CheckResult("c", "desc", CheckStatus.FAIL, "1", "2"),
            CheckResult("d", "desc", CheckStatus.WARN, "1", "0"),
            CheckResult("e", "desc", CheckStatus.SKIP, "1", "?"),
        ]
        return report

    def test_counts(self, mixed_report: ValidationReport):
        """Report correctly counts each status type."""
        assert mixed_report.passed == 2
        assert mixed_report.failed == 1
        assert mixed_report.warned == 1
        assert mixed_report.skipped == 1
        assert mixed_report.total == 5

    def test_summary(self, mixed_report: ValidationReport):
        """Summary string contains all counts."""
        summary = mixed_report.summary()
        assert "5 checks" in summary
        assert "2 passed" in summary
        assert "1 failed" in summary

    def test_empty_report(self):
        """Empty report has zero counts."""
        report = ValidationReport()
        assert report.total == 0
        assert report.passed == 0


# ---------------------------------------------------------------------------
# RHELConfigValidator._parse_version
# ---------------------------------------------------------------------------


class TestParseVersion:
    """Tests for version string parsing."""

    def test_major_minor(self):
        """Parses standard major.minor version."""
        assert RHELConfigValidator._parse_version("7.0") == (7, 0)

    def test_major_minor_patch(self):
        """Parses major.minor.patch, ignoring patch."""
        assert RHELConfigValidator._parse_version("8.0.1") == (8, 0)

    def test_invalid_version_raises(self):
        """Invalid version string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid MongoDB version"):
            RHELConfigValidator._parse_version("latest")


# ---------------------------------------------------------------------------
# Filesystem checks
# ---------------------------------------------------------------------------


class TestCheckFilesystem:
    """Tests for filesystem validation."""

    @pytest.fixture
    def validator(self) -> RHELConfigValidator:
        """Default validator instance."""
        return RHELConfigValidator(mongodb_version="7.0", data_path="/var/lib/mongo")

    def test_xfs_with_options(self, validator: RHELConfigValidator):
        """XFS with noatime and nodiratime passes all checks."""
        mounts = "/dev/sda1 /var/lib/mongo xfs rw,noatime,nodiratime,attr2 0 0\n"
        with patch.object(RHELConfigValidator, "_read_file", return_value=mounts):
            results = validator.check_filesystem()

        assert len(results) == 3
        assert all(r.status == CheckStatus.PASS for r in results)

    def test_ext4_filesystem_fails(self, validator: RHELConfigValidator):
        """EXT4 filesystem fails the type check."""
        mounts = "/dev/sda1 /var/lib/mongo ext4 rw,noatime,nodiratime 0 0\n"
        with patch.object(RHELConfigValidator, "_read_file", return_value=mounts):
            results = validator.check_filesystem()

        type_check = next(r for r in results if r.name == "filesystem_type")
        assert type_check.status == CheckStatus.FAIL
        assert type_check.actual == "ext4"

    def test_missing_noatime(self, validator: RHELConfigValidator):
        """Missing noatime mount option fails."""
        mounts = "/dev/sda1 /var/lib/mongo xfs rw,nodiratime 0 0\n"
        with patch.object(RHELConfigValidator, "_read_file", return_value=mounts):
            results = validator.check_filesystem()

        noatime = next(r for r in results if r.name == "mount_noatime")
        assert noatime.status == CheckStatus.FAIL

    def test_unreadable_mounts_skips(self, validator: RHELConfigValidator):
        """Unreadable /proc/mounts results in skip."""
        with patch.object(RHELConfigValidator, "_read_file", return_value=None):
            results = validator.check_filesystem()

        assert len(results) == 1
        assert results[0].status == CheckStatus.SKIP

    def test_falls_back_to_root_mount(self, validator: RHELConfigValidator):
        """When data path has no dedicated mount, falls back to root."""
        mounts = "/dev/sda1 / xfs rw,noatime,nodiratime 0 0\n"
        with patch.object(RHELConfigValidator, "_read_file", return_value=mounts):
            results = validator.check_filesystem()

        type_check = next(r for r in results if r.name == "filesystem_type")
        assert type_check.actual == "xfs"


# ---------------------------------------------------------------------------
# THP checks
# ---------------------------------------------------------------------------


class TestCheckTHP:
    """Tests for Transparent Huge Pages validation."""

    def test_thp_never_for_7x(self):
        """MongoDB 7.0 expects THP disabled (never)."""
        validator = RHELConfigValidator(mongodb_version="7.0")
        with patch.object(RHELConfigValidator, "_read_file", return_value="always madvise [never]"):
            result = validator.check_thp()

        assert result.status == CheckStatus.PASS
        assert result.expected == "never"

    def test_thp_always_for_8x(self):
        """MongoDB 8.0 expects THP enabled (always)."""
        validator = RHELConfigValidator(mongodb_version="8.0")
        with patch.object(RHELConfigValidator, "_read_file", return_value="[always] madvise never"):
            result = validator.check_thp()

        assert result.status == CheckStatus.PASS
        assert result.expected == "always"

    def test_thp_wrong_for_7x(self):
        """MongoDB 7.0 with THP enabled fails."""
        validator = RHELConfigValidator(mongodb_version="7.0")
        with patch.object(RHELConfigValidator, "_read_file", return_value="[always] madvise never"):
            result = validator.check_thp()

        assert result.status == CheckStatus.FAIL
        assert result.actual == "always"

    def test_thp_wrong_for_8x(self):
        """MongoDB 8.0 with THP disabled fails."""
        validator = RHELConfigValidator(mongodb_version="8.0")
        with patch.object(RHELConfigValidator, "_read_file", return_value="always madvise [never]"):
            result = validator.check_thp()

        assert result.status == CheckStatus.FAIL

    def test_thp_unreadable_skips(self):
        """Unreadable THP file results in skip."""
        validator = RHELConfigValidator(mongodb_version="7.0")
        with patch.object(RHELConfigValidator, "_read_file", return_value=None):
            result = validator.check_thp()

        assert result.status == CheckStatus.SKIP


# ---------------------------------------------------------------------------
# Sysctl checks
# ---------------------------------------------------------------------------


class TestCheckSysctl:
    """Tests for sysctl parameter validation."""

    @pytest.fixture
    def validator(self) -> RHELConfigValidator:
        """Default validator instance."""
        return RHELConfigValidator(mongodb_version="7.0")

    def test_all_correct(self, validator: RHELConfigValidator):
        """All sysctl values at recommended settings pass."""
        values = {
            "vm.swappiness": "1",
            "vm.dirty_ratio": "15",
            "vm.dirty_background_ratio": "5",
            "vm.max_map_count": "128000",
            "vm.zone_reclaim_mode": "0",
            "fs.file-max": "98000",
            "kernel.pid_max": "64000",
            "kernel.threads-max": "64000",
            "net.core.somaxconn": "65535",
            "net.ipv4.tcp_keepalive_time": "120",
            "net.ipv4.tcp_max_syn_backlog": "4096",
        }

        def fake_read(key: str) -> str | None:
            return values.get(key)

        with patch.object(RHELConfigValidator, "_read_sysctl", side_effect=fake_read):
            results = validator.check_sysctl()

        assert all(r.status == CheckStatus.PASS for r in results)

    def test_swappiness_wrong(self, validator: RHELConfigValidator):
        """Wrong swappiness value fails."""

        def fake_read(key: str) -> str | None:
            if key == "vm.swappiness":
                return "60"
            return "0"

        with patch.object(RHELConfigValidator, "_read_sysctl", side_effect=fake_read):
            results = validator.check_sysctl()

        swap = next(r for r in results if r.name == "sysctl_vm.swappiness")
        assert swap.status == CheckStatus.FAIL
        assert swap.actual == "60"

    def test_gte_comparison(self, validator: RHELConfigValidator):
        """Values exceeding the minimum still pass for gte checks."""

        def fake_read(key: str) -> str | None:
            if key == "vm.max_map_count":
                return "256000"
            return "0"

        with patch.object(RHELConfigValidator, "_read_sysctl", side_effect=fake_read):
            results = validator.check_sysctl()

        mmap = next(r for r in results if r.name == "sysctl_vm.max_map_count")
        assert mmap.status == CheckStatus.PASS

    def test_unreadable_skips(self, validator: RHELConfigValidator):
        """Unreadable sysctl values are skipped."""
        with patch.object(RHELConfigValidator, "_read_sysctl", return_value=None):
            results = validator.check_sysctl()

        assert all(r.status == CheckStatus.SKIP for r in results)

    def test_non_integer_skips(self, validator: RHELConfigValidator):
        """Non-integer sysctl values are skipped."""
        with patch.object(RHELConfigValidator, "_read_sysctl", return_value="not_a_number"):
            results = validator.check_sysctl()

        assert all(r.status == CheckStatus.SKIP for r in results)


# ---------------------------------------------------------------------------
# Ulimit checks
# ---------------------------------------------------------------------------


class TestCheckUlimits:
    """Tests for mongod process ulimit validation."""

    @pytest.fixture
    def validator(self) -> RHELConfigValidator:
        """Default validator instance."""
        return RHELConfigValidator(mongodb_version="7.0")

    LIMITS_CONTENT = (
        "Limit                     Soft Limit           Hard Limit           Units\n"
        "Max open files            64000                64000                files\n"
        "Max processes             64000                64000                processes\n"
    )

    def test_adequate_limits_pass(self, validator: RHELConfigValidator):
        """Mongod with adequate limits passes."""
        with (
            patch.object(RHELConfigValidator, "_find_mongod_pid", return_value=12345),
            patch.object(RHELConfigValidator, "_read_file", return_value=self.LIMITS_CONTENT),
        ):
            results = validator.check_ulimits()

        assert all(r.status == CheckStatus.PASS for r in results)

    def test_low_limits_fail(self, validator: RHELConfigValidator):
        """Mongod with low limits fails."""
        low_limits = (
            "Limit                     Soft Limit           Hard Limit           Units\n"
            "Max open files            1024                 1024                 files\n"
            "Max processes             1024                 1024                 processes\n"
        )
        with (
            patch.object(RHELConfigValidator, "_find_mongod_pid", return_value=12345),
            patch.object(RHELConfigValidator, "_read_file", return_value=low_limits),
        ):
            results = validator.check_ulimits()

        assert all(r.status == CheckStatus.FAIL for r in results)

    def test_unlimited_passes(self, validator: RHELConfigValidator):
        """Unlimited limits pass."""
        unlimited = (
            "Limit                     Soft Limit           Hard Limit           Units\n"
            "Max open files            unlimited            unlimited            files\n"
            "Max processes             unlimited            unlimited            processes\n"
        )
        with (
            patch.object(RHELConfigValidator, "_find_mongod_pid", return_value=12345),
            patch.object(RHELConfigValidator, "_read_file", return_value=unlimited),
        ):
            results = validator.check_ulimits()

        assert all(r.status == CheckStatus.PASS for r in results)

    def test_mongod_not_running_skips(self, validator: RHELConfigValidator):
        """When mongod is not running, ulimit checks are skipped."""
        with patch.object(RHELConfigValidator, "_find_mongod_pid", return_value=None):
            results = validator.check_ulimits()

        assert all(r.status == CheckStatus.SKIP for r in results)
        assert len(results) == 2

    def test_unreadable_limits_skips(self, validator: RHELConfigValidator):
        """Unreadable limits file results in skip."""
        with (
            patch.object(RHELConfigValidator, "_find_mongod_pid", return_value=12345),
            patch.object(RHELConfigValidator, "_read_file", return_value=None),
        ):
            results = validator.check_ulimits()

        assert all(r.status == CheckStatus.SKIP for r in results)


# ---------------------------------------------------------------------------
# SELinux checks
# ---------------------------------------------------------------------------


class TestCheckSELinux:
    """Tests for SELinux validation."""

    @pytest.fixture
    def validator(self) -> RHELConfigValidator:
        """Default validator instance."""
        return RHELConfigValidator(mongodb_version="7.0")

    def test_enforcing_passes(self, validator: RHELConfigValidator):
        """SELinux in Enforcing mode passes."""
        mock_result = MagicMock(returncode=0, stdout="Enforcing\n")
        with patch("gds_mongodb.rhel_validator.subprocess.run", return_value=mock_result):
            result = validator.check_selinux()

        assert result.status == CheckStatus.PASS

    def test_permissive_warns(self, validator: RHELConfigValidator):
        """SELinux in Permissive mode warns."""
        mock_result = MagicMock(returncode=0, stdout="Permissive\n")
        with patch("gds_mongodb.rhel_validator.subprocess.run", return_value=mock_result):
            result = validator.check_selinux()

        assert result.status == CheckStatus.WARN

    def test_getenforce_missing_falls_back(self, validator: RHELConfigValidator):
        """Falls back to config file when getenforce is not available."""
        config_content = "# SELinux config\nSELINUX=enforcing\nSELINUXTYPE=targeted\n"
        with (
            patch("gds_mongodb.rhel_validator.subprocess.run", side_effect=FileNotFoundError),
            patch.object(RHELConfigValidator, "_read_file", return_value=config_content),
        ):
            result = validator.check_selinux()

        assert result.status == CheckStatus.PASS

    def test_no_selinux_skips(self, validator: RHELConfigValidator):
        """Non-RHEL system without SELinux skips."""
        with (
            patch("gds_mongodb.rhel_validator.subprocess.run", side_effect=FileNotFoundError),
            patch.object(RHELConfigValidator, "_read_file", return_value=None),
        ):
            result = validator.check_selinux()

        assert result.status == CheckStatus.SKIP


# ---------------------------------------------------------------------------
# run_all integration
# ---------------------------------------------------------------------------


class TestRunAll:
    """Tests for the full validation run."""

    def test_run_all_returns_report(self):
        """run_all returns a ValidationReport with all check categories."""
        validator = RHELConfigValidator(mongodb_version="7.0")

        with (
            patch.object(
                validator,
                "check_filesystem",
                return_value=[
                    CheckResult("fs", "desc", CheckStatus.PASS, "xfs", "xfs"),
                ],
            ),
            patch.object(
                validator,
                "check_thp",
                return_value=CheckResult(
                    "thp",
                    "desc",
                    CheckStatus.PASS,
                    "never",
                    "never",
                ),
            ),
            patch.object(
                validator,
                "check_sysctl",
                return_value=[
                    CheckResult("sysctl", "desc", CheckStatus.PASS, "1", "1"),
                ],
            ),
            patch.object(
                validator,
                "check_ulimits",
                return_value=[
                    CheckResult("ulimit", "desc", CheckStatus.SKIP, "64000", "n/a"),
                ],
            ),
            patch.object(
                validator,
                "check_selinux",
                return_value=CheckResult(
                    "selinux",
                    "desc",
                    CheckStatus.PASS,
                    "Enforcing",
                    "Enforcing",
                ),
            ),
            patch.object(RHELConfigValidator, "_get_hostname", return_value="test-node"),
        ):
            report = validator.run_all()

        assert isinstance(report, ValidationReport)
        assert report.hostname == "test-node"
        assert report.total == 5
        assert report.passed == 4
        assert report.skipped == 1


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


class TestFromYaml:
    """Tests for loading configuration from YAML files."""

    @pytest.fixture
    def config_file(self, tmp_path: Path) -> Path:
        """Write a minimal best-practices YAML config and return its path."""
        config = {
            "mongodb_version": "8.0",
            "mongodb_data_path": "/data/mongo",
            "mongodb_sysctl": {
                "vm.swappiness": {
                    "value": 1,
                    "comparison": "eq",
                    "description": "Swap aggressiveness",
                    "reference": "https://example.com",
                },
                "vm.max_map_count": {
                    "value": 256000,
                    "comparison": "gte",
                    "description": "Max map count",
                },
            },
            "mongodb_ulimits": {
                "nofile": 128000,
                "nproc": 128000,
            },
        }
        path = tmp_path / "test-config.yml"
        path.write_text(yaml.dump(config))
        return path

    def test_from_yaml_loads_version(self, config_file: Path):
        """from_yaml picks up mongodb_version from the config."""
        validator = RHELConfigValidator.from_yaml(str(config_file))
        assert validator._mongodb_version == "8.0"
        assert validator._major_minor == (8, 0)

    def test_from_yaml_loads_data_path(self, config_file: Path):
        """from_yaml picks up mongodb_data_path from the config."""
        validator = RHELConfigValidator.from_yaml(str(config_file))
        assert validator._data_path == "/data/mongo"

    def test_from_yaml_loads_sysctl(self, config_file: Path):
        """from_yaml populates SYSCTL_EXPECTATIONS from the config."""
        validator = RHELConfigValidator.from_yaml(str(config_file))
        assert "vm.swappiness" in validator.SYSCTL_EXPECTATIONS
        assert validator.SYSCTL_EXPECTATIONS["vm.swappiness"]["expected"] == 1
        assert "vm.max_map_count" in validator.SYSCTL_EXPECTATIONS
        assert validator.SYSCTL_EXPECTATIONS["vm.max_map_count"]["comparison"] == "gte"
        # Should only contain the two keys from the config, not the defaults
        assert len(validator.SYSCTL_EXPECTATIONS) == 2

    def test_from_yaml_loads_ulimits(self, config_file: Path):
        """from_yaml populates ULIMIT_MINIMUMS from the config."""
        validator = RHELConfigValidator.from_yaml(str(config_file))
        assert validator.ULIMIT_MINIMUMS["Max open files"] == 128000
        assert validator.ULIMIT_MINIMUMS["Max processes"] == 128000

    def test_from_yaml_missing_file_raises(self):
        """from_yaml raises FileNotFoundError for missing config."""
        with pytest.raises(FileNotFoundError):
            RHELConfigValidator.from_yaml("/nonexistent/path.yml")

    def test_constructor_without_config_uses_defaults(self):
        """Constructor without config_path uses built-in defaults."""
        validator = RHELConfigValidator(mongodb_version="7.0")
        assert len(validator.SYSCTL_EXPECTATIONS) == 11
        assert validator.ULIMIT_MINIMUMS["Max open files"] == 64000

    def test_constructor_with_config_path(self, config_file: Path):
        """Constructor with config_path loads from YAML."""
        validator = RHELConfigValidator(
            mongodb_version="7.0",
            config_path=str(config_file),
        )
        # Config overrides the constructor version
        assert validator._mongodb_version == "8.0"
        assert len(validator.SYSCTL_EXPECTATIONS) == 2

    def test_yaml_loaded_validator_runs_checks(self, config_file: Path):
        """Validator loaded from YAML can run sysctl checks using YAML values."""
        validator = RHELConfigValidator.from_yaml(str(config_file))

        def fake_read(key: str) -> str | None:
            return {"vm.swappiness": "1", "vm.max_map_count": "256000"}.get(key)

        with patch.object(RHELConfigValidator, "_read_sysctl", side_effect=fake_read):
            results = validator.check_sysctl()

        assert len(results) == 2
        assert all(r.status == CheckStatus.PASS for r in results)

    def test_real_config_file_loads(self):
        """The actual shared config file loads without errors."""
        config_path = Path(__file__).resolve().parents[3] / "config" / "mongodb" / "rhel-best-practices.yml"
        if not config_path.exists():
            pytest.skip("Shared config file not found")
        validator = RHELConfigValidator.from_yaml(str(config_path))
        assert len(validator.SYSCTL_EXPECTATIONS) == 11
        assert validator._mongodb_version == "7.0"
