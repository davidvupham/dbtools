"""Tests for MongoDB monitoring and alerting module."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest
from gds_mongodb.connection import MongoDBConnection
from gds_mongodb.monitoring import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertType,
    MongoDBMonitoring,
    MonitoringResult,
)
from pymongo import MongoClient


class TestAlertSeverity:
    """Tests for AlertSeverity enum."""

    def test_severity_values(self):
        """All severity levels are defined."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestAlertType:
    """Tests for AlertType enum."""

    def test_server_alert_types(self):
        """Server alert types are defined."""
        assert AlertType.SERVER_DOWN.value == "server_down"
        assert AlertType.HIGH_CPU_USAGE.value == "high_cpu_usage"
        assert AlertType.HIGH_MEMORY_USAGE.value == "high_memory_usage"
        assert AlertType.CONNECTIONS_EXCEEDED.value == "connections_exceeded"

    def test_replica_set_alert_types(self):
        """Replica set alert types are defined."""
        assert AlertType.REPLICA_SET_NO_PRIMARY.value == "replica_set_no_primary"
        assert AlertType.REPLICA_LAG_HIGH.value == "replica_lag_high"
        assert AlertType.MEMBER_UNHEALTHY.value == "member_unhealthy"

    def test_performance_alert_types(self):
        """Performance alert types are defined."""
        assert AlertType.SLOW_QUERIES.value == "slow_queries"
        assert AlertType.LOCK_CONTENTION.value == "lock_contention"
        assert AlertType.CACHE_PRESSURE.value == "cache_pressure"


class TestAlert:
    """Tests for Alert dataclass."""

    def test_alert_creation(self):
        """Alert can be created with required fields."""
        alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="High CPU",
            source="host1",
            timestamp=time.time(),
        )
        assert alert.alert_type == AlertType.HIGH_CPU_USAGE
        assert alert.severity == AlertSeverity.WARNING
        assert alert.details is None
        assert alert.threshold is None
        assert alert.current_value is None

    def test_alert_with_optional_fields(self):
        """Alert can include optional threshold and value."""
        alert = Alert(
            alert_type=AlertType.CONNECTIONS_EXCEEDED,
            severity=AlertSeverity.ERROR,
            message="Too many connections",
            source="host1",
            timestamp=time.time(),
            details={"current": 1500},
            threshold=1000,
            current_value=1500,
        )
        assert alert.threshold == 1000
        assert alert.current_value == 1500
        assert alert.details == {"current": 1500}


class TestMonitoringResult:
    """Tests for MonitoringResult dataclass."""

    def test_success_result(self):
        """Successful monitoring result."""
        result = MonitoringResult(
            timestamp=time.time(),
            metrics={"uptime": 3600},
            alerts=[],
            success=True,
        )
        assert result.success is True
        assert result.error_message is None
        assert result.metrics["uptime"] == 3600

    def test_failure_result(self):
        """Failed monitoring result."""
        result = MonitoringResult(
            timestamp=time.time(),
            metrics={},
            alerts=[],
            success=False,
            error_message="Connection refused",
        )
        assert result.success is False
        assert result.error_message == "Connection refused"


class TestAlertManager:
    """Tests for AlertManager class."""

    def test_init(self):
        """AlertManager initializes with empty state."""
        mgr = AlertManager()
        assert mgr.active_alerts == {}
        assert mgr.alert_history == []
        assert mgr.notification_handlers == []

    def test_add_alert(self):
        """Adding an alert stores it and records history."""
        mgr = AlertManager()
        alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU high",
            source="host1",
            timestamp=time.time(),
        )
        mgr.add_alert(alert)

        assert len(mgr.active_alerts) == 1
        assert len(mgr.alert_history) == 1
        assert "high_cpu_usage_host1" in mgr.active_alerts

    def test_add_duplicate_alert_updates(self):
        """Adding same alert type+source updates existing, doesn't duplicate history."""
        mgr = AlertManager()
        alert1 = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU at 85%",
            source="host1",
            timestamp=time.time(),
        )
        alert2 = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.ERROR,
            message="CPU at 95%",
            source="host1",
            timestamp=time.time(),
        )
        mgr.add_alert(alert1)
        mgr.add_alert(alert2)

        assert len(mgr.active_alerts) == 1
        assert mgr.active_alerts["high_cpu_usage_host1"].message == "CPU at 95%"
        # History only records first occurrence
        assert len(mgr.alert_history) == 1

    def test_resolve_alert(self):
        """Resolving an alert removes it from active alerts."""
        mgr = AlertManager()
        alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU high",
            source="host1",
            timestamp=time.time(),
        )
        mgr.add_alert(alert)
        mgr.resolve_alert(AlertType.HIGH_CPU_USAGE, "host1")

        assert len(mgr.active_alerts) == 0
        assert len(mgr.alert_history) == 1  # History preserved

    def test_resolve_nonexistent_alert(self):
        """Resolving a nonexistent alert does nothing."""
        mgr = AlertManager()
        mgr.resolve_alert(AlertType.HIGH_CPU_USAGE, "host1")
        assert len(mgr.active_alerts) == 0

    def test_get_active_alerts(self):
        """Get active alerts with optional severity filter."""
        mgr = AlertManager()
        mgr.add_alert(Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU", source="h1", timestamp=time.time(),
        ))
        mgr.add_alert(Alert(
            alert_type=AlertType.CONNECTIONS_EXCEEDED,
            severity=AlertSeverity.ERROR,
            message="Conn", source="h1", timestamp=time.time(),
        ))

        all_alerts = mgr.get_active_alerts()
        assert len(all_alerts) == 2

        warnings = mgr.get_active_alerts(severity=AlertSeverity.WARNING)
        assert len(warnings) == 1
        assert warnings[0].alert_type == AlertType.HIGH_CPU_USAGE

    def test_get_alert_history(self):
        """Get alert history filters by time window."""
        mgr = AlertManager()
        old_alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="old",
            source="h1",
            timestamp=time.time() - 100000,  # ~28 hours ago
        )
        new_alert = Alert(
            alert_type=AlertType.CONNECTIONS_EXCEEDED,
            severity=AlertSeverity.ERROR,
            message="new",
            source="h1",
            timestamp=time.time(),
        )
        mgr.alert_history = [old_alert, new_alert]

        recent = mgr.get_alert_history(hours=24)
        assert len(recent) == 1
        assert recent[0].message == "new"

    def test_notification_handler(self):
        """Notification handlers are called on new alerts."""
        mgr = AlertManager()
        received = []
        mgr.add_notification_handler(lambda alert: received.append(alert))

        alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU",
            source="h1",
            timestamp=time.time(),
        )
        mgr.add_alert(alert)

        assert len(received) == 1
        assert received[0].message == "CPU"

    def test_notification_handler_error_does_not_propagate(self):
        """Handler errors are caught and logged, not propagated."""
        mgr = AlertManager()
        mgr.add_notification_handler(lambda alert: 1 / 0)

        alert = Alert(
            alert_type=AlertType.HIGH_CPU_USAGE,
            severity=AlertSeverity.WARNING,
            message="CPU",
            source="h1",
            timestamp=time.time(),
        )
        # Should not raise
        mgr.add_alert(alert)
        assert len(mgr.active_alerts) == 1


class TestMongoDBMonitoring:
    """Tests for MongoDBMonitoring class."""

    def _make_monitoring(self):
        """Create a MongoDBMonitoring with a mocked client."""
        mock_client = MagicMock(spec=MongoClient)
        mock_client.admin = MagicMock()
        monitoring = MongoDBMonitoring(connection=mock_client)
        return monitoring, mock_client

    def test_init_with_mongo_client(self):
        """Initialize with MongoClient."""
        mock_client = MagicMock(spec=MongoClient)
        mock_client.admin = MagicMock()
        monitoring = MongoDBMonitoring(connection=mock_client)
        assert monitoring.client is mock_client
        assert monitoring.connection is None

    def test_init_with_connection(self):
        """Initialize with MongoDBConnection."""
        mock_conn = MagicMock(spec=MongoDBConnection)
        mock_conn.client = MagicMock()
        monitoring = MongoDBMonitoring(connection=mock_conn)
        assert monitoring.client is mock_conn.client
        assert monitoring.connection is mock_conn

    def test_init_invalid_connection(self):
        """Invalid connection type raises ValueError."""
        with pytest.raises(ValueError, match="must be MongoDBConnection or MongoClient"):
            MongoDBMonitoring(connection="invalid")

    def test_init_with_custom_alert_manager(self):
        """Custom AlertManager is used."""
        mock_client = MagicMock(spec=MongoClient)
        custom_mgr = AlertManager()
        monitoring = MongoDBMonitoring(connection=mock_client, alert_manager=custom_mgr)
        assert monitoring.alert_manager is custom_mgr

    def test_default_thresholds(self):
        """Default thresholds are set."""
        monitoring, _ = self._make_monitoring()
        assert monitoring.thresholds["cpu_usage_percent"] == 80.0
        assert monitoring.thresholds["max_connections"] == 1000
        assert monitoring.thresholds["database_size_gb"] == 100.0

    def test_update_thresholds(self):
        """Thresholds can be updated."""
        monitoring, _ = self._make_monitoring()
        monitoring.update_thresholds({"cpu_usage_percent": 90.0})
        assert monitoring.thresholds["cpu_usage_percent"] == 90.0

    def test_monitor_server_status_success(self):
        """Successful server status monitoring."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.return_value = {
            "host": "localhost:27017",
            "version": "7.0.0",
            "process": "mongod",
            "pid": 1234,
            "uptime": 3600,
            "connections": {"current": 10, "available": 990},
            "mem": {"resident": 512, "virtual": 1024},
            "cpu": {"percent": 25.0},
            "storageEngine": {"name": "wiredTiger"},
            "opcounters": {"query": 100},
            "opcountersRepl": {},
            "network": {},
            "locks": {},
            "globalLock": {},
        }

        result = monitoring.monitor_server_status()

        assert result.success is True
        assert result.metrics["host"] == "localhost:27017"
        assert result.metrics["version"] == "7.0.0"
        assert result.metrics["uptime"] == 3600
        assert result.error_message is None

    def test_monitor_server_status_failure(self):
        """Server status monitoring handles errors."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.side_effect = Exception("Connection refused")

        result = monitoring.monitor_server_status()

        assert result.success is False
        assert "Connection refused" in result.error_message

    def test_monitor_server_status_cpu_alert(self):
        """High CPU generates alert."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.return_value = {
            "host": "host1",
            "cpu": {"percent": 95.0},
            "connections": {"current": 5},
            "mem": {},
        }

        result = monitoring.monitor_server_status()

        assert result.success is True
        cpu_alerts = [a for a in result.alerts if a.alert_type == AlertType.HIGH_CPU_USAGE]
        assert len(cpu_alerts) == 1
        assert cpu_alerts[0].current_value == 95.0

    def test_monitor_server_status_connection_alert(self):
        """High connection count generates alert."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.return_value = {
            "host": "host1",
            "cpu": {},
            "connections": {"current": 1500},
            "mem": {},
        }

        result = monitoring.monitor_server_status()

        conn_alerts = [a for a in result.alerts if a.alert_type == AlertType.CONNECTIONS_EXCEEDED]
        assert len(conn_alerts) == 1
        assert conn_alerts[0].severity == AlertSeverity.ERROR

    def test_monitor_database_stats_success(self):
        """Successful database stats monitoring."""
        monitoring, mock_client = self._make_monitoring()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {
            "collections": 10,
            "objects": 50000,
            "dataSize": 2.5,
            "storageSize": 3.0,
            "indexes": 15,
            "indexSize": 0.5,
            "totalSize": 3.5,
            "scaleFactor": 1073741824,
        }

        result = monitoring.monitor_database_stats("testdb")

        assert result.success is True
        assert result.metrics["database"] == "testdb"
        assert result.metrics["collections"] == 10
        assert result.metrics["total_size_gb"] == 3.5

    def test_monitor_database_stats_failure(self):
        """Database stats monitoring handles errors."""
        monitoring, mock_client = self._make_monitoring()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.command.side_effect = Exception("db error")

        result = monitoring.monitor_database_stats("testdb")

        assert result.success is False
        assert result.metrics["database"] == "testdb"

    def test_monitor_database_stats_size_alert(self):
        """Large database generates alert."""
        monitoring, mock_client = self._make_monitoring()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {
            "totalSize": 150.0,
            "indexSize": 0.5,
        }

        result = monitoring.monitor_database_stats("bigdb")

        db_alerts = [a for a in result.alerts if a.alert_type == AlertType.DATABASE_SIZE_CRITICAL]
        assert len(db_alerts) == 1

    def test_monitor_collection_stats_success(self):
        """Successful collection stats monitoring."""
        monitoring, mock_client = self._make_monitoring()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {
            "count": 10000,
            "size": 0.5,
            "storageSize": 0.6,
            "totalIndexSize": 0.1,
            "avgObjSize": 512,
            "indexDetails": {"_id_": {}},
            "capped": False,
        }

        result = monitoring.monitor_collection_stats("testdb", "users")

        assert result.success is True
        assert result.metrics["collection"] == "users"
        assert result.metrics["count"] == 10000

    def test_monitor_collection_stats_failure(self):
        """Collection stats monitoring handles errors."""
        monitoring, mock_client = self._make_monitoring()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.command.side_effect = Exception("collection not found")

        result = monitoring.monitor_collection_stats("testdb", "missing")

        assert result.success is False

    def test_monitor_performance_success(self):
        """Successful performance monitoring."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.side_effect = [
            [{"op": "query", "waitingForLock": False}, {"op": "update", "waitingForLock": True}],
            {
                "opcounters": {"query": 500},
                "opcountersRepl": {},
                "globalLock": {"ratio": 0.01},
                "locks": {},
                "metrics": {},
            },
        ]

        result = monitoring.monitor_performance()

        assert result.success is True
        assert result.metrics["current_operations"] == 2
        assert result.metrics["active_operations"] == 1
        assert result.metrics["waiting_operations"] == 1

    def test_monitor_performance_failure(self):
        """Performance monitoring handles errors."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.side_effect = Exception("timeout")

        result = monitoring.monitor_performance()

        assert result.success is False

    def test_check_performance_lock_alert(self):
        """High lock contention generates alert."""
        monitoring, mock_client = self._make_monitoring()
        mock_client.admin.command.side_effect = [
            [],  # currentOp
            {
                "opcounters": {"query": 100},
                "opcountersRepl": {},
                "globalLock": {"ratio": 0.5},
                "locks": {},
                "metrics": {},
            },
        ]

        result = monitoring.monitor_performance()

        lock_alerts = [a for a in result.alerts if a.alert_type == AlertType.LOCK_CONTENTION]
        assert len(lock_alerts) == 1

    def test_run_full_monitoring_check(self):
        """Full monitoring check runs server status and performance."""
        monitoring, mock_client = self._make_monitoring()
        # serverStatus for monitor_server_status
        mock_client.admin.command.return_value = {
            "host": "host1",
            "cpu": {},
            "connections": {"current": 5},
            "mem": {},
            "opcounters": {},
            "opcountersRepl": {},
            "globalLock": {},
            "locks": {},
            "metrics": {},
        }
        mock_client.list_database_names.side_effect = Exception("not authorized")

        results = monitoring.run_full_monitoring_check()

        assert "server_status" in results
        assert "performance" in results
