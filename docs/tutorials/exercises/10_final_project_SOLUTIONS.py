"""
Final Project: Database Monitoring System - SOLUTIONS
======================================================

This file contains the complete solution for the final project.
DO NOT share this with students - let them learn by solving!

Run this file to verify the solution passes all tests:
    python 10_final_project_SOLUTIONS.py
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

# ============================================================================
# Enums
# ============================================================================


class MonitorStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class DatabaseType(Enum):
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# Dataclasses
# ============================================================================


@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    unit: str


@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: datetime


@dataclass
class DatabaseConfig:
    name: str
    db_type: DatabaseType
    host: str
    port: int


# ============================================================================
# Abstract Base Class
# ============================================================================


class Monitor(ABC):
    def __init__(self, config: DatabaseConfig):
        self.config = config

    @abstractmethod
    def check_health(self) -> MonitorStatus:
        """Check the health of this monitor"""
        pass

    @abstractmethod
    def get_metrics(self) -> list[Metric]:
        """Get current metrics"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this monitor"""
        pass


# ============================================================================
# Concrete Monitor Classes
# ============================================================================


class ConnectionMonitor(Monitor):
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.is_connected = random.choice([True, True, True, False])  # 75% success rate

    def check_health(self) -> MonitorStatus:
        if self.is_connected:
            return MonitorStatus.HEALTHY
        return MonitorStatus.CRITICAL

    def get_metrics(self) -> list[Metric]:
        now = datetime.now()
        return [
            Metric("connection_status", 1.0 if self.is_connected else 0.0, now, "boolean"),
            Metric("response_time", random.uniform(5, 50), now, "ms"),
        ]

    def get_name(self) -> str:
        return f"Connection Monitor - {self.config.name}"


class PerformanceMonitor(Monitor):
    def __init__(self, config: DatabaseConfig, threshold_ms: float = 100.0):
        super().__init__(config)
        self.threshold_ms = threshold_ms
        self.query_time = random.uniform(10, 200)

    def check_health(self) -> MonitorStatus:
        if self.query_time < self.threshold_ms:
            return MonitorStatus.HEALTHY
        if self.query_time < self.threshold_ms * 1.5:
            return MonitorStatus.WARNING
        return MonitorStatus.CRITICAL

    def get_metrics(self) -> list[Metric]:
        now = datetime.now()
        return [
            Metric("query_latency", self.query_time, now, "ms"),
            Metric("throughput", random.uniform(100, 1000), now, "queries/sec"),
            Metric("cpu_usage", random.uniform(20, 90), now, "%"),
        ]

    def get_name(self) -> str:
        return f"Performance Monitor - {self.config.name}"


class StorageMonitor(Monitor):
    def __init__(self, config: DatabaseConfig, max_usage_percent: float = 80.0):
        super().__init__(config)
        self.max_usage_percent = max_usage_percent
        self.current_usage = random.uniform(30, 95)

    def check_health(self) -> MonitorStatus:
        if self.current_usage < self.max_usage_percent:
            return MonitorStatus.HEALTHY
        if self.current_usage < self.max_usage_percent * 1.1:
            return MonitorStatus.WARNING
        return MonitorStatus.CRITICAL

    def get_metrics(self) -> list[Metric]:
        now = datetime.now()
        total_gb = 1000
        used_gb = total_gb * (self.current_usage / 100)
        return [
            Metric("disk_usage", self.current_usage, now, "%"),
            Metric("disk_used", used_gb, now, "GB"),
            Metric("disk_total", total_gb, now, "GB"),
        ]

    def get_name(self) -> str:
        return f"Storage Monitor - {self.config.name}"


# ============================================================================
# Main Monitoring System
# ============================================================================


class MonitoringSystem:
    def __init__(self):
        self.monitors: list[Monitor] = []
        self.alerts: list[Alert] = []
        self.last_check_results: dict[str, MonitorStatus] = {}

    def add_monitor(self, monitor: Monitor):
        """Add a monitor to the system"""
        self.monitors.append(monitor)

    def run_checks(self) -> dict[str, MonitorStatus]:
        """Run health checks on all monitors"""
        self.last_check_results.clear()
        self.alerts.clear()

        for monitor in self.monitors:
            status = monitor.check_health()
            name = monitor.get_name()
            self.last_check_results[name] = status

            # Generate alerts based on status
            now = datetime.now()
            if status == MonitorStatus.CRITICAL:
                self.alerts.append(Alert(AlertLevel.CRITICAL, f"{name} is in CRITICAL state!", now))
            elif status == MonitorStatus.WARNING:
                self.alerts.append(Alert(AlertLevel.WARNING, f"{name} needs attention", now))

        return self.last_check_results

    def get_all_metrics(self) -> list[Metric]:
        """Get all metrics from all monitors"""
        all_metrics = []
        for monitor in self.monitors:
            all_metrics.extend(monitor.get_metrics())
        return all_metrics

    def get_alerts(self, level: Optional[AlertLevel] = None) -> list[Alert]:
        """Get all alerts, optionally filtered by level"""
        if level is None:
            return self.alerts
        return [alert for alert in self.alerts if alert.level == level]

    def generate_report(self) -> str:
        """Generate a formatted monitoring report"""
        separator = "=" * 70
        report_lines = [
            separator,
            "DATABASE MONITORING REPORT".center(70),
            separator,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Monitors: {len(self.monitors)}",
            "",
            "Monitor Status:".upper(),
            "-" * 70,
        ]

        # Add monitor statuses
        for name, status in self.last_check_results.items():
            status_symbol = {
                MonitorStatus.HEALTHY: "✓",
                MonitorStatus.WARNING: "⚠",
                MonitorStatus.CRITICAL: "✗",
                MonitorStatus.UNKNOWN: "?",
            }.get(status, "?")

            report_lines.append(f"{status_symbol} {name:<50} {status.value.upper():>15}")

        # Add metrics summary
        report_lines.extend(
            [
                "",
                "Metrics Summary:".upper(),
                "-" * 70,
            ]
        )

        metrics_by_type = {}
        for metric in self.get_all_metrics():
            if metric.name not in metrics_by_type:
                metrics_by_type[metric.name] = []
            metrics_by_type[metric.name].append(metric.value)

        for metric_name, values in sorted(metrics_by_type.items()):
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            report_lines.append(
                f"{metric_name:<30} Avg: {avg_value:>8.2f}  Min: {min_value:>8.2f}  Max: {max_value:>8.2f}"
            )

        # Add alerts
        if self.alerts:
            report_lines.extend(
                [
                    "",
                    "Active Alerts:".upper(),
                    "-" * 70,
                ]
            )
            for alert in self.alerts:
                alert_symbol = {
                    AlertLevel.CRITICAL: "🔴",
                    AlertLevel.ERROR: "🟠",
                    AlertLevel.WARNING: "🟡",
                    AlertLevel.INFO: "ℹ️",
                }.get(alert.level, "•")
                report_lines.append(f"{alert_symbol} [{alert.level.value.upper()}] {alert.message}")
        else:
            report_lines.extend(
                [
                    "",
                    "✓ No active alerts".center(70),
                ]
            )

        report_lines.append(separator)
        return "\n".join(report_lines)


# ============================================================================
# Test Suite
# ============================================================================


def test_basic_functionality():
    """Test basic functionality of all components"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Functionality")
    print("=" * 60)

    try:
        # Test enums
        status = MonitorStatus.HEALTHY
        assert status == MonitorStatus.HEALTHY
        print("✓ Enums work")

        # Test dataclasses
        config = DatabaseConfig("prod_db", DatabaseType.SNOWFLAKE, "db.example.com", 5432)
        assert config.name == "prod_db"
        print("✓ DatabaseConfig dataclass works")

        metric = Metric("cpu_usage", 45.2, datetime.now(), "%")
        assert metric.value == 45.2
        print("✓ Metric dataclass works")

        alert = Alert(AlertLevel.WARNING, "CPU high", datetime.now())
        assert alert.level == AlertLevel.WARNING
        print("✓ Alert dataclass works")

        print("\n✅ TEST 1 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_monitor_inheritance():
    """Test monitor inheritance and abstract methods"""
    print("\n" + "=" * 60)
    print("TEST 2: Monitor Inheritance")
    print("=" * 60)

    try:
        config = DatabaseConfig("test_db", DatabaseType.POSTGRES, "localhost", 5432)

        # Test ConnectionMonitor
        conn_monitor = ConnectionMonitor(config)
        status = conn_monitor.check_health()
        assert status in [MonitorStatus.HEALTHY, MonitorStatus.CRITICAL]
        metrics = conn_monitor.get_metrics()
        assert isinstance(metrics, list)
        name = conn_monitor.get_name()
        assert "Connection" in name
        print("✓ ConnectionMonitor works")

        # Test PerformanceMonitor
        perf_monitor = PerformanceMonitor(config, threshold_ms=100.0)
        status = perf_monitor.check_health()
        metrics = perf_monitor.get_metrics()
        assert len(metrics) > 0
        print("✓ PerformanceMonitor works")

        # Test StorageMonitor
        storage_monitor = StorageMonitor(config, max_usage_percent=80.0)
        status = storage_monitor.check_health()
        metrics = storage_monitor.get_metrics()
        assert len(metrics) > 0
        print("✓ StorageMonitor works")

        # Test that Monitor is abstract
        try:
            monitor = Monitor(config)
            print("❌ Should not be able to instantiate abstract Monitor")
            return False
        except TypeError:
            print("✓ Cannot instantiate abstract Monitor")

        print("\n✅ TEST 2 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_monitoring_system():
    """Test the complete monitoring system"""
    print("\n" + "=" * 60)
    print("TEST 3: Monitoring System")
    print("=" * 60)

    try:
        # Create system
        system = MonitoringSystem()
        print("✓ Created MonitoringSystem")

        # Add monitors
        config = DatabaseConfig("prod_db", DatabaseType.SNOWFLAKE, "db.prod.com", 5432)
        system.add_monitor(ConnectionMonitor(config))
        system.add_monitor(PerformanceMonitor(config, threshold_ms=100.0))
        system.add_monitor(StorageMonitor(config, max_usage_percent=80.0))
        print("✓ Added 3 monitors")

        # Run checks
        results = system.run_checks()
        assert len(results) == 3
        assert all(isinstance(v, MonitorStatus) for v in results.values())
        print(f"✓ Ran checks, got {len(results)} results")

        # Get metrics
        all_metrics = system.get_all_metrics()
        assert len(all_metrics) > 0
        assert all(isinstance(m, Metric) for m in all_metrics)
        print(f"✓ Collected {len(all_metrics)} metrics")

        # Get alerts
        all_alerts = system.get_alerts()
        assert isinstance(all_alerts, list)
        print(f"✓ Retrieved {len(all_alerts)} alerts")

        # Filter alerts by level
        critical_alerts = system.get_alerts(AlertLevel.CRITICAL)
        assert all(a.level == AlertLevel.CRITICAL for a in critical_alerts)
        print(f"✓ Filtered to {len(critical_alerts)} critical alerts")

        print("\n✅ TEST 3 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_report_generation():
    """Test report generation with formatting"""
    print("\n" + "=" * 60)
    print("TEST 4: Report Generation")
    print("=" * 60)

    try:
        # Create system with monitors
        system = MonitoringSystem()
        config = DatabaseConfig("prod_db", DatabaseType.SNOWFLAKE, "db.prod.com", 5432)
        system.add_monitor(ConnectionMonitor(config))
        system.add_monitor(PerformanceMonitor(config, threshold_ms=100.0))
        system.add_monitor(StorageMonitor(config, max_usage_percent=80.0))

        # Run checks to generate data
        system.run_checks()

        # Generate report
        report = system.generate_report()
        assert isinstance(report, str)
        assert len(report) > 0
        print("✓ Generated report")

        # Verify report contains key information
        assert "Database Monitoring Report" in report or "MONITORING REPORT" in report.upper()
        assert "prod_db" in report
        assert "Monitor" in report
        print("✓ Report contains required information")

        # Print sample report
        print("\n" + "-" * 60)
        print("SAMPLE REPORT:")
        print("-" * 60)
        print(report)
        print("-" * 60)

        print("\n✅ TEST 4 PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_real_world_scenario():
    """Test a complete real-world scenario"""
    print("\n" + "=" * 60)
    print("TEST 5: Real-World Scenario")
    print("=" * 60)

    try:
        # Setup: Multiple databases being monitored
        system = MonitoringSystem()

        databases = [
            DatabaseConfig("analytics_db", DatabaseType.SNOWFLAKE, "analytics.example.com", 5432),
            DatabaseConfig("api_db", DatabaseType.POSTGRES, "api.example.com", 5433),
            DatabaseConfig("cache_db", DatabaseType.MONGODB, "cache.example.com", 27017),
        ]

        for db_config in databases:
            system.add_monitor(ConnectionMonitor(db_config))
            system.add_monitor(PerformanceMonitor(db_config, threshold_ms=150.0))
            system.add_monitor(StorageMonitor(db_config, max_usage_percent=85.0))

        print(f"✓ Monitoring {len(databases)} databases with 3 monitors each")

        # Scenario: Run health checks
        results = system.run_checks()
        assert len(results) == 9  # 3 databases × 3 monitors
        print(f"✓ Completed {len(results)} health checks")

        # Scenario: Check for unhealthy systems
        unhealthy = [
            name for name, status in results.items() if status in [MonitorStatus.WARNING, MonitorStatus.CRITICAL]
        ]
        print(f"✓ Found {len(unhealthy)} monitors needing attention")

        # Scenario: Collect all metrics for analysis
        all_metrics = system.get_all_metrics()
        assert len(all_metrics) > 0
        print(f"✓ Collected {len(all_metrics)} metrics for analysis")

        # Scenario: Get critical alerts for immediate action
        critical_alerts = system.get_alerts(AlertLevel.CRITICAL)
        if critical_alerts:
            print(f"⚠ {len(critical_alerts)} critical alerts require immediate attention!")
        else:
            print("✓ No critical alerts")

        # Scenario: Generate executive report
        report = system.generate_report()
        assert "analytics_db" in report
        assert "api_db" in report
        assert "cache_db" in report
        print("✓ Generated comprehensive report for all databases")

        # Scenario: Find performance bottlenecks
        perf_metrics = [m for m in all_metrics if "query" in m.name.lower() or "latency" in m.name.lower()]
        slow_queries = [m for m in perf_metrics if m.value > 150]
        print(f"✓ Identified {len(slow_queries)} slow queries")

        print("\n✅ TEST 5 PASSED!")
        print("\n🎉 Congratulations! You've built a complete monitoring system!")
        return True
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


# ============================================================================
# Run All Tests
# ============================================================================


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 70)
    print("FINAL PROJECT: DATABASE MONITORING SYSTEM - TEST SUITE")
    print("=" * 70)

    results = [
        test_basic_functionality(),
        test_monitor_inheritance(),
        test_monitoring_system(),
        test_report_generation(),
        test_real_world_scenario(),
    ]

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n" + "🎉" * 35)
        print("\n✅ ALL TESTS PASSED! ✅")
        print("\n🎉" * 35)
        print("\n🏆 CONGRATULATIONS! 🏆")
        print("\nYou have successfully completed the Python OOP exercises!")
        print("\nYou've demonstrated mastery of:")
        print("  ✓ Object-Oriented Programming")
        print("  ✓ Dataclasses and Enums")
        print("  ✓ Abstract Base Classes")
        print("  ✓ Inheritance and Composition")
        print("  ✓ Type Hints")
        print("  ✓ Design Patterns")
        print("  ✓ Real-World System Design")
        print("\n🚀 You're ready to contribute to production codebases!")
        print("\nNext steps:")
        print("  1. Review the gds_snowflake codebase")
        print("  2. Try implementing your own monitoring system")
        print("  3. Explore advanced OOP patterns")
        print("  4. Build more complex applications")
        print("\nHappy coding! 🐍")
    else:
        print(f"\n📚 Keep working! {total - passed} test(s) need attention.")
        print("\nTips:")
        print("  • Review the test that failed")
        print("  • Check the error messages carefully")
        print("  • Look at similar examples in previous exercises")
        print("  • Test each component individually")
        print("  • Don't hesitate to start over if needed!")


if __name__ == "__main__":
    run_all_tests()
