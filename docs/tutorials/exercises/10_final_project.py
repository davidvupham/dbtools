"""
Final Project: Database Monitoring System
==========================================

Build a complete database monitoring system that brings together all the concepts
you've learned:
- Dataclasses
- Enums
- Abstract Base Classes
- Inheritance
- Composition
- @classmethod
- super()
- Type hints
- List comprehensions
- f-strings

This project simulates a real-world scenario similar to the gds_snowflake codebase!

Run this file to test your solution:
    python 10_final_project.py
"""

from datetime import datetime

# ============================================================================
# PROJECT: Build a Database Monitoring System
# ============================================================================
# TODO: Implement the complete monitoring system with the following components:
#
# 1. Enums:
#    - MonitorStatus (HEALTHY, WARNING, CRITICAL, UNKNOWN)
#    - DatabaseType (SNOWFLAKE, POSTGRES, MYSQL, MONGODB)
#    - AlertLevel (INFO, WARNING, ERROR, CRITICAL)
#
# 2. Dataclasses:
#    - Metric (name: str, value: float, timestamp: datetime, unit: str)
#    - Alert (level: AlertLevel, message: str, timestamp: datetime)
#    - DatabaseConfig (name: str, db_type: DatabaseType, host: str, port: int)
#
# 3. Abstract Base Class:
#    - Monitor (ABC) with:
#      - @abstractmethod check_health() -> MonitorStatus
#      - @abstractmethod get_metrics() -> List[Metric]
#      - @abstractmethod get_name() -> str
#
# 4. Concrete Classes (inherit from Monitor):
#    - ConnectionMonitor (checks database connectivity)
#    - PerformanceMonitor (checks query performance)
#    - StorageMonitor (checks disk usage)
#
# 5. Main System Class:
#    - MonitoringSystem with:
#      - add_monitor(monitor: Monitor)
#      - run_checks() -> Dict[str, MonitorStatus]
#      - get_all_metrics() -> List[Metric]
#      - get_alerts(level: Optional[AlertLevel] = None) -> List[Alert]
#      - generate_report() -> str (formatted with f-strings)
#
# Your code here:

# class MonitorStatus(Enum):
#     pass

# class DatabaseType(Enum):
#     pass

# class AlertLevel(Enum):
#     pass

# @dataclass
# class Metric:
#     pass

# @dataclass
# class Alert:
#     pass

# @dataclass
# class DatabaseConfig:
#     pass

# class Monitor(ABC):
#     pass

# class ConnectionMonitor(Monitor):
#     pass

# class PerformanceMonitor(Monitor):
#     pass

# class StorageMonitor(Monitor):
#     pass

# class MonitoringSystem:
#     pass


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
        config = DatabaseConfig(
            "prod_db", DatabaseType.SNOWFLAKE, "db.example.com", 5432
        )
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
        assert (
            "Database Monitoring Report" in report
            or "MONITORING REPORT" in report.upper()
        )
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
            DatabaseConfig(
                "analytics_db", DatabaseType.SNOWFLAKE, "analytics.example.com", 5432
            ),
            DatabaseConfig("api_db", DatabaseType.POSTGRES, "api.example.com", 5433),
            DatabaseConfig(
                "cache_db", DatabaseType.MONGODB, "cache.example.com", 27017
            ),
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
            name
            for name, status in results.items()
            if status in [MonitorStatus.WARNING, MonitorStatus.CRITICAL]
        ]
        print(f"✓ Found {len(unhealthy)} monitors needing attention")

        # Scenario: Collect all metrics for analysis
        all_metrics = system.get_all_metrics()
        assert len(all_metrics) > 0
        print(f"✓ Collected {len(all_metrics)} metrics for analysis")

        # Scenario: Get critical alerts for immediate action
        critical_alerts = system.get_alerts(AlertLevel.CRITICAL)
        if critical_alerts:
            print(
                f"⚠ {len(critical_alerts)} critical alerts require immediate attention!"
            )
        else:
            print("✓ No critical alerts")

        # Scenario: Generate executive report
        report = system.generate_report()
        assert "analytics_db" in report
        assert "api_db" in report
        assert "cache_db" in report
        print("✓ Generated comprehensive report for all databases")

        # Scenario: Find performance bottlenecks
        perf_metrics = [
            m
            for m in all_metrics
            if "query" in m.name.lower() or "latency" in m.name.lower()
        ]
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
