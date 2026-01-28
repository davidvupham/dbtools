"""
RHEL configuration validator for MongoDB deployments.

Compares current Linux system settings against MongoDB best practices
documented in the RHEL configuration guide. Each check returns a structured
result indicating whether the current value matches the recommended setting.

Best-practice values can be loaded from a shared YAML configuration file
(``config/mongodb/rhel-best-practices.yml``) so that both this validator
and the Ansible role ``mongodb_rhel`` use the same source of truth.

This module reads system files (sysctl, sysfs, /proc, /etc/fstab) and
compares values against MongoDB production recommendations for:
- Filesystem configuration (XFS, mount options)
- Kernel and memory settings (THP, swappiness, dirty ratios, NUMA)
- Systemd resource limits (open files, processes)
- Network tuning (somaxconn, keepalive, backlog)
- Security (SELinux mode)

Reference: https://www.mongodb.com/docs/manual/administration/production-notes/
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

import yaml

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Result status for a configuration check."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a single configuration check.

    Attributes:
        name: Short identifier for the check.
        description: Human-readable description of what is being validated.
        status: Whether the check passed, failed, warned, or was skipped.
        expected: The recommended value or description.
        actual: The current system value.
        message: Additional context or remediation guidance.
        reference: URL to official MongoDB documentation.
    """

    name: str
    description: str
    status: CheckStatus
    expected: str
    actual: str
    message: str = ""
    reference: str = ""


@dataclass
class ValidationReport:
    """Aggregated report of all configuration checks.

    Attributes:
        checks: List of individual check results.
        hostname: System hostname where validation was run.
    """

    checks: list[CheckResult] = field(default_factory=list)
    hostname: str = ""

    @property
    def passed(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)

    @property
    def failed(self) -> int:
        """Count of failed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)

    @property
    def warned(self) -> int:
        """Count of warned checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)

    @property
    def skipped(self) -> int:
        """Count of skipped checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.SKIP)

    @property
    def total(self) -> int:
        """Total number of checks."""
        return len(self.checks)

    def summary(self) -> str:
        """Return a one-line summary of the validation results."""
        return (
            f"{self.total} checks: {self.passed} passed, {self.failed} failed, "
            f"{self.warned} warnings, {self.skipped} skipped"
        )


class RHELConfigValidator:
    """Validates RHEL system configuration against MongoDB best practices.

    Reads system files and kernel parameters to compare current values
    against recommended settings. Settings can be loaded from a shared
    YAML configuration file or fall back to built-in defaults.

    Args:
        mongodb_version: Major.minor version string (e.g. "7.0" or "8.0").
            Controls version-dependent checks like THP.
        data_path: MongoDB data directory path. Defaults to /var/lib/mongo.
        config_path: Optional path to a YAML best-practices config file.
            When provided, sysctl expectations and ulimit minimums are
            loaded from the file instead of using built-in defaults.

    Example:
        >>> # Using built-in defaults
        >>> validator = RHELConfigValidator(mongodb_version="7.0")
        >>> report = validator.run_all()
        >>> print(report.summary())

        >>> # Loading from shared YAML config
        >>> validator = RHELConfigValidator.from_yaml(
        ...     "config/mongodb/rhel-best-practices.yml"
        ... )
        >>> report = validator.run_all()
    """

    # Built-in defaults — used when no YAML config is provided
    _DEFAULT_SYSCTL: ClassVar[dict[str, dict[str, Any]]] = {
        "vm.swappiness": {
            "expected": 1,
            "description": "Kernel swap aggressiveness",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "vm.dirty_ratio": {
            "expected": 15,
            "description": "Maximum dirty page ratio before synchronous writeback",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "vm.dirty_background_ratio": {
            "expected": 5,
            "description": "Dirty page ratio before background writeback starts",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "vm.max_map_count": {
            "expected": 128000,
            "comparison": "gte",
            "description": "Maximum memory map areas per process",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "vm.zone_reclaim_mode": {
            "expected": 0,
            "description": "NUMA zone reclaim mode (must be 0 for MongoDB)",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/#configuring-numa-on-linux",
        },
        "fs.file-max": {
            "expected": 98000,
            "comparison": "gte",
            "description": "System-wide maximum open file descriptors",
            "reference": "https://www.mongodb.com/docs/manual/reference/ulimit/",
        },
        "kernel.pid_max": {
            "expected": 64000,
            "comparison": "gte",
            "description": "Maximum PID value",
            "reference": "https://www.mongodb.com/docs/manual/reference/ulimit/",
        },
        "kernel.threads-max": {
            "expected": 64000,
            "comparison": "gte",
            "description": "System-wide maximum threads",
            "reference": "https://www.mongodb.com/docs/manual/reference/ulimit/",
        },
        "net.core.somaxconn": {
            "expected": 65535,
            "comparison": "gte",
            "description": "Maximum socket listen backlog",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "net.ipv4.tcp_keepalive_time": {
            "expected": 120,
            "description": "TCP keepalive interval in seconds",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
        "net.ipv4.tcp_max_syn_backlog": {
            "expected": 4096,
            "comparison": "gte",
            "description": "Maximum TCP SYN backlog",
            "reference": "https://www.mongodb.com/docs/manual/administration/production-notes/",
        },
    }

    _DEFAULT_ULIMITS: ClassVar[dict[str, int]] = {
        "Max open files": 64000,
        "Max processes": 64000,
    }

    def __init__(
        self,
        mongodb_version: str = "7.0",
        data_path: str = "/var/lib/mongo",
        config_path: str | None = None,
    ) -> None:
        self._mongodb_version = mongodb_version
        self._data_path = data_path
        self._major_minor = self._parse_version(mongodb_version)

        if config_path is not None:
            self._load_yaml(config_path)
        else:
            self.SYSCTL_EXPECTATIONS = dict(self._DEFAULT_SYSCTL)
            self.ULIMIT_MINIMUMS = dict(self._DEFAULT_ULIMITS)

    # ------------------------------------------------------------------
    # YAML loading
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(cls, config_path: str) -> RHELConfigValidator:
        """Create a validator with settings loaded from a YAML config file.

        The YAML file should contain ``mongodb_version``, ``mongodb_data_path``,
        ``mongodb_sysctl``, and ``mongodb_ulimits`` keys matching the schema
        defined in ``config/mongodb/rhel-best-practices.yml``.

        Args:
            config_path: Path to the YAML best-practices config file.

        Returns:
            Configured RHELConfigValidator instance.

        Raises:
            FileNotFoundError: If the config file does not exist.
            yaml.YAMLError: If the file is not valid YAML.
        """
        data = cls._read_yaml(config_path)
        version = str(data.get("mongodb_version", "7.0"))
        data_path = str(data.get("mongodb_data_path", "/var/lib/mongo"))
        return cls(mongodb_version=version, data_path=data_path, config_path=config_path)

    @staticmethod
    def _read_yaml(config_path: str) -> dict[str, Any]:
        """Read and parse a YAML file.

        Args:
            config_path: Path to the YAML file.

        Returns:
            Parsed YAML data as a dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If the file is not valid YAML.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with path.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected a YAML mapping, got {type(data).__name__}")
        return data

    def _load_yaml(self, config_path: str) -> None:
        """Load sysctl and ulimit expectations from a YAML config file.

        Args:
            config_path: Path to the YAML best-practices config file.
        """
        data = self._read_yaml(config_path)

        # Build SYSCTL_EXPECTATIONS from mongodb_sysctl section
        sysctl_data = data.get("mongodb_sysctl", {})
        self.SYSCTL_EXPECTATIONS = {}
        for key, spec in sysctl_data.items():
            self.SYSCTL_EXPECTATIONS[key] = {
                "expected": spec["value"],
                "comparison": spec.get("comparison", "eq"),
                "description": spec.get("description", key),
                "reference": spec.get("reference", ""),
            }

        # Build ULIMIT_MINIMUMS from mongodb_ulimits section
        ulimits_data = data.get("mongodb_ulimits", {})
        self.ULIMIT_MINIMUMS = {}
        if "nofile" in ulimits_data:
            self.ULIMIT_MINIMUMS["Max open files"] = int(ulimits_data["nofile"])
        if "nproc" in ulimits_data:
            self.ULIMIT_MINIMUMS["Max processes"] = int(ulimits_data["nproc"])

        # Override version and data path if present
        if "mongodb_version" in data:
            self._mongodb_version = str(data["mongodb_version"])
            self._major_minor = self._parse_version(self._mongodb_version)
        if "mongodb_data_path" in data:
            self._data_path = str(data["mongodb_data_path"])

    @staticmethod
    def _parse_version(version: str) -> tuple[int, int]:
        """Parse a version string into (major, minor) tuple.

        Args:
            version: Version string like "7.0" or "8.0.1".

        Returns:
            Tuple of (major, minor) integers.

        Raises:
            ValueError: If version string cannot be parsed.
        """
        match = re.match(r"^(\d+)\.(\d+)", version)
        if not match:
            raise ValueError(f"Invalid MongoDB version string: {version!r}")
        return int(match.group(1)), int(match.group(2))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_file(path: str) -> str | None:
        """Read a file and return stripped contents, or None on failure."""
        try:
            return Path(path).read_text().strip()
        except (OSError, PermissionError) as e:
            logger.debug(f"Cannot read {path}: {e}")
            return None

    @staticmethod
    def _read_sysctl(key: str) -> str | None:
        """Read a sysctl value via /proc/sys.

        Args:
            key: Sysctl key using dot notation (e.g. "vm.swappiness").

        Returns:
            The current value as a string, or None if unreadable.
        """
        proc_path = "/proc/sys/" + key.replace(".", "/")
        try:
            return Path(proc_path).read_text().strip()
        except (OSError, PermissionError) as e:
            logger.debug(f"Cannot read sysctl {key} from {proc_path}: {e}")
            return None

    @staticmethod
    def _find_mongod_pid() -> int | None:
        """Find the PID of a running mongod process.

        Returns:
            The PID as an integer, or None if mongod is not running.
        """
        try:
            result = subprocess.run(
                ["pgrep", "-x", "mongod"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().splitlines()[0])
        except (OSError, ValueError) as e:
            logger.debug(f"Cannot find mongod PID: {e}")
        return None

    @staticmethod
    def _get_hostname() -> str:
        """Return the system hostname."""
        try:
            return Path("/etc/hostname").read_text().strip()
        except OSError:
            return "unknown"

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def check_filesystem(self) -> list[CheckResult]:
        """Check that the MongoDB data path uses XFS with recommended mount options.

        Verifies:
        - Filesystem type is XFS.
        - Mount options include noatime.
        - Mount options include nodiratime.

        Returns:
            List of CheckResult for filesystem checks.
        """
        results: list[CheckResult] = []
        reference = "https://www.mongodb.com/docs/manual/administration/production-notes/#kernel-and-file-systems"

        # Try to determine filesystem type and mount options from /proc/mounts
        mount_info = self._read_file("/proc/mounts")
        if mount_info is None:
            results.append(
                CheckResult(
                    name="filesystem_type",
                    description="Data volume filesystem type",
                    status=CheckStatus.SKIP,
                    expected="xfs",
                    actual="unknown",
                    message="Cannot read /proc/mounts",
                    reference=reference,
                )
            )
            return results

        # Find the mount entry for the data path (or its parent)
        fs_type = None
        mount_options = ""
        data_path = self._data_path.rstrip("/")

        # Walk up the path to find the mount point
        for line in mount_info.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                mount_point = parts[1]
                if data_path.startswith(mount_point) and mount_point != "/":
                    fs_type = parts[2]
                    mount_options = parts[3]
                    break

        # Fall back to root mount
        if fs_type is None:
            for line in mount_info.splitlines():
                parts = line.split()
                if len(parts) >= 4 and parts[1] == "/":
                    fs_type = parts[2]
                    mount_options = parts[3]
                    break

        actual_type = fs_type or "unknown"
        results.append(
            CheckResult(
                name="filesystem_type",
                description="Data volume filesystem type",
                status=CheckStatus.PASS if actual_type == "xfs" else CheckStatus.FAIL,
                expected="xfs",
                actual=actual_type,
                message="" if actual_type == "xfs" else f"Format {self._data_path} as XFS for WiredTiger",
                reference=reference,
            )
        )

        options_list = mount_options.split(",")
        for option in ("noatime", "nodiratime"):
            present = option in options_list
            results.append(
                CheckResult(
                    name=f"mount_{option}",
                    description=f"Mount option '{option}' on data volume",
                    status=CheckStatus.PASS if present else CheckStatus.FAIL,
                    expected=option,
                    actual="present" if present else "absent",
                    message="" if present else f"Add '{option}' to mount options for {self._data_path}",
                    reference=reference,
                )
            )

        return results

    def check_thp(self) -> CheckResult:
        """Check Transparent Huge Pages setting based on MongoDB version.

        MongoDB 8.0+ benefits from THP enabled; 7.0 and earlier requires THP disabled.

        Returns:
            CheckResult for the THP check.
        """
        reference = "https://www.mongodb.com/docs/manual/tutorial/transparent-huge-pages/"
        thp_path = "/sys/kernel/mm/transparent_hugepage/enabled"

        content = self._read_file(thp_path)
        if content is None:
            return CheckResult(
                name="thp",
                description="Transparent Huge Pages setting",
                status=CheckStatus.SKIP,
                expected="",
                actual="unknown",
                message=f"Cannot read {thp_path}",
                reference=reference,
            )

        # Parse the active setting: e.g. "always madvise [never]"
        match = re.search(r"\[(\w+)]", content)
        active = match.group(1) if match else "unknown"

        if self._major_minor >= (8, 0):
            expected = "always"
            message = "MongoDB 8.0+ benefits from THP enabled (always)"
        else:
            expected = "never"
            message = "MongoDB 7.0 and earlier requires THP disabled (never)"

        return CheckResult(
            name="thp",
            description="Transparent Huge Pages setting",
            status=CheckStatus.PASS if active == expected else CheckStatus.FAIL,
            expected=expected,
            actual=active,
            message="" if active == expected else message,
            reference=reference,
        )

    def check_sysctl(self) -> list[CheckResult]:
        """Check all recommended sysctl kernel parameters.

        Validates vm.swappiness, vm.dirty_ratio, vm.dirty_background_ratio,
        vm.max_map_count, vm.zone_reclaim_mode, fs.file-max, kernel.pid_max,
        kernel.threads-max, and network tuning parameters.

        Returns:
            List of CheckResult for each sysctl parameter.
        """
        results: list[CheckResult] = []

        for key, spec in self.SYSCTL_EXPECTATIONS.items():
            raw_value = self._read_sysctl(key)

            if raw_value is None:
                results.append(
                    CheckResult(
                        name=f"sysctl_{key}",
                        description=spec["description"],
                        status=CheckStatus.SKIP,
                        expected=str(spec["expected"]),
                        actual="unreadable",
                        message=f"Cannot read {key} from /proc/sys",
                        reference=spec.get("reference", ""),
                    )
                )
                continue

            try:
                actual_int = int(raw_value)
            except ValueError:
                results.append(
                    CheckResult(
                        name=f"sysctl_{key}",
                        description=spec["description"],
                        status=CheckStatus.SKIP,
                        expected=str(spec["expected"]),
                        actual=raw_value,
                        message=f"Non-integer value for {key}",
                        reference=spec.get("reference", ""),
                    )
                )
                continue

            expected_int = spec["expected"]
            comparison = spec.get("comparison", "eq")

            if comparison == "gte":
                passed = actual_int >= expected_int
                op_desc = f">= {expected_int}"
            else:
                passed = actual_int == expected_int
                op_desc = str(expected_int)

            results.append(
                CheckResult(
                    name=f"sysctl_{key}",
                    description=spec["description"],
                    status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                    expected=op_desc,
                    actual=str(actual_int),
                    message="" if passed else f"Set {key} = {expected_int} in /etc/sysctl.d/99-mongodb.conf",
                    reference=spec.get("reference", ""),
                )
            )

        return results

    def check_ulimits(self) -> list[CheckResult]:
        """Check mongod process ulimits (open files and max processes).

        Reads /proc/<mongod_pid>/limits to verify the running process has
        adequate resource limits. Requires mongod to be running.

        Returns:
            List of CheckResult for each ulimit check.
        """
        results: list[CheckResult] = []
        reference = "https://www.mongodb.com/docs/manual/reference/ulimit/"

        pid = self._find_mongod_pid()
        if pid is None:
            for limit_name, minimum in self.ULIMIT_MINIMUMS.items():
                results.append(
                    CheckResult(
                        name=f"ulimit_{limit_name.lower().replace(' ', '_')}",
                        description=f"mongod {limit_name}",
                        status=CheckStatus.SKIP,
                        expected=f">= {minimum}",
                        actual="mongod not running",
                        message="Start mongod to check process limits",
                        reference=reference,
                    )
                )
            return results

        limits_content = self._read_file(f"/proc/{pid}/limits")
        if limits_content is None:
            for limit_name, minimum in self.ULIMIT_MINIMUMS.items():
                results.append(
                    CheckResult(
                        name=f"ulimit_{limit_name.lower().replace(' ', '_')}",
                        description=f"mongod {limit_name}",
                        status=CheckStatus.SKIP,
                        expected=f">= {minimum}",
                        actual="unreadable",
                        message=f"Cannot read /proc/{pid}/limits (try running as root)",
                        reference=reference,
                    )
                )
            return results

        for limit_name, minimum in self.ULIMIT_MINIMUMS.items():
            check_name = f"ulimit_{limit_name.lower().replace(' ', '_')}"

            # Parse the limits file: "Max open files            64000                64000                files"
            pattern = rf"^{re.escape(limit_name)}\s+(\S+)\s+(\S+)"
            match = re.search(pattern, limits_content, re.MULTILINE)

            if not match:
                results.append(
                    CheckResult(
                        name=check_name,
                        description=f"mongod {limit_name}",
                        status=CheckStatus.SKIP,
                        expected=f">= {minimum}",
                        actual="not found",
                        message=f"Cannot parse {limit_name} from /proc/{pid}/limits",
                        reference=reference,
                    )
                )
                continue

            soft_str = match.group(1)
            if soft_str.lower() == "unlimited":
                actual_val = float("inf")
                actual_display = "unlimited"
            else:
                try:
                    actual_val = int(soft_str)
                    actual_display = str(actual_val)
                except ValueError:
                    results.append(
                        CheckResult(
                            name=check_name,
                            description=f"mongod {limit_name}",
                            status=CheckStatus.SKIP,
                            expected=f">= {minimum}",
                            actual=soft_str,
                            message=f"Cannot parse value for {limit_name}",
                            reference=reference,
                        )
                    )
                    continue

            passed = actual_val >= minimum
            results.append(
                CheckResult(
                    name=check_name,
                    description=f"mongod {limit_name}",
                    status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                    expected=f">= {minimum}",
                    actual=actual_display,
                    message="" if passed else "Set LimitNOFILE/LimitNPROC=64000 via systemctl edit mongod",
                    reference=reference,
                )
            )

        return results

    def check_selinux(self) -> CheckResult:
        """Check that SELinux is in Enforcing mode.

        Returns:
            CheckResult for the SELinux check.
        """
        reference = "https://www.mongodb.com/docs/manual/tutorial/install-mongodb-enterprise-on-red-hat/"

        # Try getenforce first, fall back to /etc/selinux/config
        try:
            result = subprocess.run(
                ["getenforce"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                mode = result.stdout.strip()
                return CheckResult(
                    name="selinux",
                    description="SELinux mode",
                    status=CheckStatus.PASS if mode == "Enforcing" else CheckStatus.WARN,
                    expected="Enforcing",
                    actual=mode,
                    message="" if mode == "Enforcing" else "SELinux should be in Enforcing mode",
                    reference=reference,
                )
        except FileNotFoundError:
            pass

        # Fall back to config file
        config = self._read_file("/etc/selinux/config")
        if config is None:
            return CheckResult(
                name="selinux",
                description="SELinux mode",
                status=CheckStatus.SKIP,
                expected="Enforcing",
                actual="unknown",
                message="Cannot determine SELinux status (not RHEL?)",
                reference=reference,
            )

        match = re.search(r"^SELINUX=(\w+)", config, re.MULTILINE)
        mode = match.group(1) if match else "unknown"
        return CheckResult(
            name="selinux",
            description="SELinux mode",
            status=CheckStatus.PASS if mode == "enforcing" else CheckStatus.WARN,
            expected="enforcing",
            actual=mode,
            message="" if mode == "enforcing" else "Set SELINUX=enforcing in /etc/selinux/config",
            reference=reference,
        )

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self) -> ValidationReport:
        """Run all RHEL configuration checks and return an aggregated report.

        Returns:
            ValidationReport containing results from all checks.

        Example:
            >>> validator = RHELConfigValidator(mongodb_version="7.0")
            >>> report = validator.run_all()
            >>> for c in report.checks:
            ...     print(
            ...         f"[{c.status.value:4s}] {c.name}: expected={c.expected} actual={c.actual}"
            ...     )
        """
        report = ValidationReport(hostname=self._get_hostname())

        # Filesystem checks
        report.checks.extend(self.check_filesystem())

        # Transparent Huge Pages
        report.checks.append(self.check_thp())

        # Sysctl parameters (swappiness, dirty ratios, NUMA, limits, network)
        report.checks.extend(self.check_sysctl())

        # Process ulimits
        report.checks.extend(self.check_ulimits())

        # SELinux
        report.checks.append(self.check_selinux())

        return report
