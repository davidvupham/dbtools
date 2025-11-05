"""
MongoDB Monitoring and Alerting Examples

This example demonstrates comprehensive monitoring capabilities for MongoDB
deployments, including server monitoring, database statistics, alerting,
and replica set health monitoring.
"""

import time
import logging

from gds_mongodb import (
    MongoDBConnection,
    MongoDBMonitoring,
    AlertManager,
    Alert,
    AlertSeverity,
    MongoDBReplicaSetManager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_monitoring():
    """Example: Basic MongoDB monitoring setup."""
    print("=" * 70)
    print("Example 1: Basic MongoDB Monitoring")
    print("=" * 70)

    # Create connection
    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
    )

    try:
        conn.connect()

        # Create alert manager
        alert_manager = AlertManager()

        # Create monitoring instance
        monitor = MongoDBMonitoring(conn, alert_manager)

        # Monitor server status
        print("\nServer Status:")
        server_result = monitor.monitor_server_status()
        if server_result.success:
            metrics = server_result.metrics
            print(f"  Host: {metrics.get('host', 'unknown')}")
            print(f"  MongoDB Version: {metrics.get('version', 'unknown')}")
            print(f"  Uptime: {metrics.get('uptime', 0)} seconds")

            connections = metrics.get("connections", {})
            print(f"  Current Connections: {connections.get('current', 0)}")
            print(f"  Available Connections: {connections.get('available', 0)}")

            # Check for alerts
            if server_result.alerts:
                print("  Alerts:")
                for alert in server_result.alerts:
                    print(f"    {alert.severity.value.upper()}: {alert.message}")
        else:
            print(f"  Error: {server_result.error_message}")

        # Monitor database statistics
        print("\nDatabase Statistics:")
        db_result = monitor.monitor_database_stats("test")
        if db_result.success:
            metrics = db_result.metrics
            print(f"  Database: {metrics.get('database')}")
            print(f"  Collections: {metrics.get('collections', 0)}")
            print(f"  Documents: {metrics.get('objects', 0)}")
            print(f"  Data Size: {metrics.get('data_size_gb', 0):.2f} GB")
            print(f"  Index Size: {metrics.get('index_size_gb', 0):.2f} GB")
            print(f"  Total Size: {metrics.get('total_size_gb', 0):.2f} GB")

            if db_result.alerts:
                print("  Alerts:")
                for alert in db_result.alerts:
                    print(f"    {alert.severity.value.upper()}: {alert.message}")
        else:
            print(f"  Error: {db_result.error_message}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_alert_management():
    """Example: Alert management and notification handlers."""
    print("=" * 70)
    print("Example 2: Alert Management and Notifications")
    print("=" * 70)

    # Create alert manager
    alert_manager = AlertManager()

    # Define notification handlers
    def console_alert_handler(alert: Alert):
        """Simple console notification handler."""
        print(f"[{alert.timestamp}] {alert.severity.value.upper()}: {alert.message}")
        if alert.details:
            print(f"  Details: {alert.details}")

    def email_alert_handler(alert: Alert):
        """Mock email notification handler."""
        if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
            print(f"EMAIL ALERT: Would send email for {alert.alert_type.value}")
            print(
                f"  Subject: MongoDB {alert.severity.value.upper()}: {alert.alert_type.value}"
            )
            print(f"  Body: {alert.message}")

    # Add handlers
    alert_manager.add_notification_handler(console_alert_handler)
    alert_manager.add_notification_handler(email_alert_handler)

    # Create some test alerts
    alerts = [
        Alert(
            alert_type="high_cpu_usage",
            severity=AlertSeverity.WARNING,
            message="CPU usage is at 85%",
            source="mongodb-server-01",
            timestamp=time.time(),
            threshold=80.0,
            current_value=85.0,
        ),
        Alert(
            alert_type="replica_lag_high",
            severity=AlertSeverity.ERROR,
            message="Replication lag exceeded 60 seconds on secondary-02",
            source="replica-secondary-02",
            timestamp=time.time(),
            threshold=30.0,
            current_value=65.0,
        ),
        Alert(
            alert_type="member_unhealthy",
            severity=AlertSeverity.CRITICAL,
            message="Replica set member mongodb-03 is unreachable",
            source="replica-mongodb-03",
            timestamp=time.time(),
        ),
    ]

    print("\nSimulating Alerts:")
    for alert in alerts:
        alert_manager.add_alert(alert)
        time.sleep(0.1)  # Small delay for timestamps

    # Check active alerts
    print(f"\nActive Alerts: {len(alert_manager.get_active_alerts())}")
    for alert in alert_manager.get_active_alerts():
        print(f"  {alert.alert_type}: {alert.message}")

    # Get alert history
    print(f"\nAlert History (last 24h): {len(alert_manager.get_alert_history())}")

    print()


def example_replica_set_monitoring():
    """Example: Replica set health monitoring and troubleshooting."""
    print("=" * 70)
    print("Example 3: Replica Set Monitoring and Troubleshooting")
    print("=" * 70)

    # Create connection to replica set
    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
        replica_set="myReplicaSet",
    )

    try:
        conn.connect()

        # Create replica set manager
        rs_manager = MongoDBReplicaSetManager(conn)

        # Create alert manager for replica set alerts
        alert_manager = AlertManager()

        def replica_alert_handler(alert: Alert):
            print(f"REPLICA ALERT [{alert.timestamp}]: {alert.severity.value.upper()}")
            print(f"  Type: {alert.alert_type}")
            print(f"  Message: {alert.message}")
            print(f"  Source: {alert.source}")

        alert_manager.add_notification_handler(replica_alert_handler)

        # Monitor replica set health
        print("\nReplica Set Health Check:")
        health = rs_manager.monitor_health(alert_manager)

        print(f"Overall Health: {health['overall_health'].upper()}")

        for check_name, check_result in health["checks"].items():
            status = check_result["status"]
            issues = check_result.get("issues", [])
            details = check_result.get("details", {})

            print(f"\n{check_name.replace('_', ' ').title()}: {status.upper()}")

            if details:
                for key, value in details.items():
                    print(f"  {key}: {value}")

            if issues:
                print("  Issues:")
                for issue in issues:
                    print(f"    - {issue}")

        # Get replication metrics
        print("\nReplication Metrics:")
        metrics = rs_manager.get_replication_metrics()

        print(f"Max Replication Lag: {metrics.get('max_lag_seconds', 0)} seconds")

        lag_info = metrics.get("replication_lag", {})
        if lag_info:
            print("Replication Lag by Member:")
            for member, lag in lag_info.items():
                print(f"  {member}: {lag} seconds")

        member_states = metrics.get("member_states", {})
        if member_states:
            print("Member States:")
            for member, state in member_states.items():
                print(f"  {member}: {state}")

        # Run troubleshooting
        print("\nTroubleshooting Replication Issues:")
        diagnostics = rs_manager.troubleshoot_replication_issues()

        if diagnostics["issues"]:
            print(f"Found {len(diagnostics['issues'])} issues:")
            for issue in diagnostics["issues"]:
                print(f"\nIssue: {issue['description']}")
                print(f"  Type: {issue['type']}")
                print(f"  Severity: {issue['severity']}")
                print(f"  Recommendation: {issue['recommendation']}")
        else:
            print("No replication issues detected.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_comprehensive_monitoring():
    """Example: Comprehensive monitoring with custom thresholds."""
    print("=" * 70)
    print("Example 4: Comprehensive Monitoring with Custom Thresholds")
    print("=" * 70)

    # Create connection
    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
    )

    try:
        conn.connect()

        # Create monitoring with custom thresholds
        monitor = MongoDBMonitoring(conn)

        # Update thresholds for stricter monitoring
        custom_thresholds = {
            "cpu_usage_percent": 70.0,  # More sensitive CPU monitoring
            "memory_usage_percent": 75.0,  # Lower memory threshold
            "max_connections": 500,  # Lower connection limit
            "replica_lag_seconds": 15,  # Stricter lag monitoring
            "database_size_gb": 50.0,  # Smaller database size limit
        }

        monitor.update_thresholds(custom_thresholds)
        print("Updated monitoring thresholds:")
        for key, value in custom_thresholds.items():
            print(f"  {key}: {value}")

        # Run full monitoring check
        print("\nRunning Full Monitoring Check:")
        results = monitor.run_full_monitoring_check()

        total_alerts = 0
        for check_name, result in results.items():
            status = "✓" if result.success else "✗"
            alerts = len(result.alerts)
            total_alerts += alerts
            print(f"  {status} {check_name}: {alerts} alerts")

            if result.alerts:
                for alert in result.alerts:
                    print(f"    {alert.severity.value.upper()}: {alert.message}")

        print(f"\nTotal alerts generated: {total_alerts}")

        # Show monitoring summary
        print("\nMonitoring Summary:")
        print(f"  Checks performed: {len(results)}")
        print(f"  Successful checks: {sum(1 for r in results.values() if r.success)}")
        print(f"  Failed checks: {sum(1 for r in results.values() if not r.success)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_monitoring_best_practices():
    """Example: Best practices for MongoDB monitoring."""
    print("=" * 70)
    print("Example 5: Monitoring Best Practices")
    print("=" * 70)

    print("""
MongoDB Monitoring Best Practices:

1. MONITORING FREQUENCY:
   - Server status: Every 30 seconds
   - Database stats: Every 5 minutes
   - Replica set health: Every 60 seconds
   - Performance metrics: Every 30 seconds

2. ALERT THRESHOLDS:
   - CPU Usage: Warning at 80%, Critical at 95%
   - Memory Usage: Warning at 85%, Critical at 95%
   - Disk Usage: Warning at 85%, Critical at 95%
   - Connections: Warning at 80% of max, Critical at 95%
   - Replication Lag: Warning at 30s, Critical at 60s

3. REPLICA SET MONITORING:
   - Monitor primary availability continuously
   - Check member health every minute
   - Alert on replication lag > 30 seconds
   - Monitor oplog size (recommend 24-72 hours)

4. PERFORMANCE MONITORING:
   - Track slow queries (>1000ms)
   - Monitor lock contention (>10% of time)
   - Watch cache pressure and working set size
   - Monitor connection pool utilization

5. ALERT ESCALATION:
   - INFO: Log only
   - WARNING: Review within 1 hour
   - ERROR: Investigate within 30 minutes
   - CRITICAL: Immediate response required

6. DATA RETENTION:
   - Active alerts: Keep until resolved
   - Alert history: 30 days minimum
   - Metrics data: 7-30 days based on needs

7. NOTIFICATION CHANNELS:
   - Email for non-critical alerts
   - SMS/Pager for critical alerts
   - Slack/Teams for team notifications
   - Dashboard for visual monitoring

8. AUTOMATED RESPONSES:
   - Auto-scale read replicas for high load
   - Connection pool optimization
   - Index suggestions for slow queries
   - Automated failover verification

Implementation Tips:
- Use structured logging for all monitoring events
- Implement circuit breakers for monitoring queries
- Cache monitoring results to reduce database load
- Use sampling for high-frequency metrics
- Implement graceful degradation if monitoring fails
""")

    print()


def main():
    """Run all monitoring examples."""
    print("MongoDB Monitoring and Alerting Examples")
    print("=========================================")

    try:
        # Run examples (comment out as needed for testing)
        example_basic_monitoring()
        example_alert_management()
        example_replica_set_monitoring()
        example_comprehensive_monitoring()
        example_monitoring_best_practices()

    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        logger.exception("Example execution failed")


if __name__ == "__main__":
    main()
