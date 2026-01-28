"""
MongoDB monitoring and alerting module.

This module provides comprehensive monitoring capabilities for MongoDB deployments,
including server status monitoring, database statistics, performance metrics,
and alerting for MongoDB operations and replica sets.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pymongo import MongoClient

from .connection import MongoDBConnection

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts that can be generated."""

    # Server alerts
    SERVER_DOWN = "server_down"
    HIGH_CPU_USAGE = "high_cpu_usage"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    LOW_DISK_SPACE = "low_disk_space"
    CONNECTIONS_EXCEEDED = "connections_exceeded"

    # Database alerts
    DATABASE_SIZE_CRITICAL = "database_size_critical"
    COLLECTION_SIZE_CRITICAL = "collection_size_critical"
    INDEX_SIZE_CRITICAL = "index_size_critical"

    # Replica set alerts
    REPLICA_SET_NO_PRIMARY = "replica_set_no_primary"
    REPLICA_LAG_HIGH = "replica_lag_high"
    MEMBER_UNHEALTHY = "member_unhealthy"
    REPLICA_SET_SPLIT_BRAIN = "replica_set_split_brain"

    # Performance alerts
    SLOW_QUERIES = "slow_queries"
    LOCK_CONTENTION = "lock_contention"
    CACHE_PRESSURE = "cache_pressure"


@dataclass
class Alert:
    """Represents a monitoring alert."""

    alert_type: AlertType
    severity: AlertSeverity
    message: str
    source: str
    timestamp: float
    details: dict[str, Any] | None = None
    threshold: int | float | None = None
    current_value: int | float | None = None


@dataclass
class MonitoringResult:
    """Result of a monitoring check."""

    timestamp: float
    metrics: dict[str, Any]
    alerts: list[Alert]
    success: bool
    error_message: str | None = None


class AlertManager:
    """
    Manages alerts and notifications for MongoDB monitoring.

    Provides functionality to:
    - Store and track active alerts
    - Send notifications via various channels
    - Manage alert thresholds and configurations
    - Generate alert summaries and reports
    """

    def __init__(self):
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.notification_handlers: list[callable] = []

    def add_alert(self, alert: Alert) -> None:
        """Add a new alert and notify handlers."""
        alert_key = f"{alert.alert_type.value}_{alert.source}"

        # Check if this alert is already active
        if alert_key in self.active_alerts:
            # Update existing alert
            self.active_alerts[alert_key] = alert
        else:
            # New alert
            self.active_alerts[alert_key] = alert
            self.alert_history.append(alert)

            # Notify handlers
            for handler in self.notification_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert notification handler: {e}")

        logger.log(
            self._get_log_level(alert.severity),
            f"Alert {alert.alert_type.value}: {alert.message} (source: {alert.source})",
        )

    def resolve_alert(self, alert_type: AlertType, source: str) -> None:
        """Resolve an active alert."""
        alert_key = f"{alert_type.value}_{source}"
        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
            logger.info(f"Resolved alert {alert_type.value} for {source}")

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get all active alerts, optionally filtered by severity."""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts

    def get_alert_history(self, hours: int = 24) -> list[Alert]:
        """Get alert history for the specified number of hours."""
        cutoff_time = time.time() - (hours * 3600)
        return [a for a in self.alert_history if a.timestamp >= cutoff_time]

    def add_notification_handler(self, handler: callable) -> None:
        """Add a notification handler function."""
        self.notification_handlers.append(handler)

    def _get_log_level(self, severity: AlertSeverity) -> int:
        """Convert alert severity to logging level."""
        mapping = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(severity, logging.INFO)


class MongoDBMonitoring:
    """
    Comprehensive monitoring for MongoDB deployments.

    Provides monitoring capabilities for:
    - Server status and health
    - Database and collection statistics
    - Performance metrics
    - Connection and resource usage
    - Custom metric collection
    """

    def __init__(
        self,
        connection: MongoDBConnection | MongoClient,
        alert_manager: AlertManager | None = None,
    ):
        """
        Initialize MongoDB monitoring.

        Args:
            connection: MongoDB connection instance
            alert_manager: Optional alert manager for notifications
        """
        if isinstance(connection, MongoDBConnection):
            self.client = connection.client
            self.connection = connection
        elif isinstance(connection, MongoClient):
            self.client = connection
            self.connection = None
        else:
            raise ValueError("connection must be MongoDBConnection or MongoClient instance")

        self.alert_manager = alert_manager or AlertManager()

        # Default thresholds
        self.thresholds = {
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0,
            "disk_usage_percent": 90.0,
            "max_connections": 1000,
            "database_size_gb": 100.0,
            "collection_size_gb": 10.0,
            "index_size_gb": 5.0,
            "replica_lag_seconds": 30,
            "slow_query_threshold_ms": 1000,
        }

    def monitor_server_status(self) -> MonitoringResult:
        """
        Monitor MongoDB server status and generate alerts.

        Returns:
            MonitoringResult with server metrics and alerts
        """
        try:
            server_status = self.client.admin.command("serverStatus")
            timestamp = time.time()

            metrics = {
                "host": server_status.get("host"),
                "version": server_status.get("version"),
                "process": server_status.get("process"),
                "pid": server_status.get("pid"),
                "uptime": server_status.get("uptime"),
                "connections": server_status.get("connections", {}),
                "memory": server_status.get("mem", {}),
                "cpu": server_status.get("cpu", {}),
                "storage_engine": server_status.get("storageEngine", {}),
                "opcounters": server_status.get("opcounters", {}),
                "opcounters_replicated": server_status.get("opcountersRepl", {}),
                "network": server_status.get("network", {}),
                "locks": server_status.get("locks", {}),
                "global_lock": server_status.get("globalLock", {}),
            }

            alerts = self._check_server_alerts(metrics)

            return MonitoringResult(timestamp=timestamp, metrics=metrics, alerts=alerts, success=True)

        except Exception as e:
            error_msg = f"Failed to monitor server status: {e}"
            logger.error(error_msg)
            return MonitoringResult(
                timestamp=time.time(),
                metrics={},
                alerts=[],
                success=False,
                error_message=error_msg,
            )

    def monitor_database_stats(self, database_name: str) -> MonitoringResult:
        """
        Monitor database statistics and generate alerts.

        Args:
            database_name: Name of database to monitor

        Returns:
            MonitoringResult with database metrics and alerts
        """
        try:
            db = self.client[database_name]
            stats = db.command("dbStats", scale=1024 * 1024 * 1024)  # Scale to GB
            timestamp = time.time()

            metrics = {
                "database": database_name,
                "collections": stats.get("collections", 0),
                "objects": stats.get("objects", 0),
                "data_size_gb": stats.get("dataSize", 0),
                "storage_size_gb": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "index_size_gb": stats.get("indexSize", 0),
                "total_size_gb": stats.get("totalSize", 0),
                "scale_factor": stats.get("scaleFactor", 1),
            }

            alerts = self._check_database_alerts(metrics)

            return MonitoringResult(timestamp=timestamp, metrics=metrics, alerts=alerts, success=True)

        except Exception as e:
            error_msg = f"Failed to monitor database {database_name}: {e}"
            logger.error(error_msg)
            return MonitoringResult(
                timestamp=time.time(),
                metrics={"database": database_name},
                alerts=[],
                success=False,
                error_message=error_msg,
            )

    def monitor_collection_stats(self, database_name: str, collection_name: str) -> MonitoringResult:
        """
        Monitor collection statistics and generate alerts.

        Args:
            database_name: Name of database
            collection_name: Name of collection to monitor

        Returns:
            MonitoringResult with collection metrics and alerts
        """
        try:
            db = self.client[database_name]
            stats = db.command("collStats", collection_name, scale=1024 * 1024 * 1024)
            timestamp = time.time()

            metrics = {
                "database": database_name,
                "collection": collection_name,
                "count": stats.get("count", 0),
                "size_gb": stats.get("size", 0),
                "storage_size_gb": stats.get("storageSize", 0),
                "total_index_size_gb": stats.get("totalIndexSize", 0),
                "avg_obj_size_bytes": stats.get("avgObjSize", 0),
                "indexes": len(stats.get("indexDetails", {})),
                "capped": stats.get("capped", False),
                "max_size_gb": stats.get("maxSize", 0),
            }

            alerts = self._check_collection_alerts(metrics)

            return MonitoringResult(timestamp=timestamp, metrics=metrics, alerts=alerts, success=True)

        except Exception as e:
            error_msg = f"Failed to monitor collection {database_name}.{collection_name}: {e}"
            logger.error(error_msg)
            return MonitoringResult(
                timestamp=time.time(),
                metrics={"database": database_name, "collection": collection_name},
                alerts=[],
                success=False,
                error_message=error_msg,
            )

    def monitor_performance(self) -> MonitoringResult:
        """
        Monitor MongoDB performance metrics.

        Returns:
            MonitoringResult with performance metrics and alerts
        """
        try:
            # Get current operations
            current_ops = list(self.client.admin.command("currentOp"))

            # Get server status for performance data
            server_status = self.client.admin.command("serverStatus")

            timestamp = time.time()

            metrics = {
                "current_operations": len(current_ops),
                "active_operations": len([op for op in current_ops if not op.get("waitingForLock", False)]),
                "waiting_operations": len([op for op in current_ops if op.get("waitingForLock", False)]),
                "opcounters": server_status.get("opcounters", {}),
                "opcounters_replicated": server_status.get("opcountersRepl", {}),
                "global_lock": server_status.get("globalLock", {}),
                "locks": server_status.get("locks", {}),
                "metrics": server_status.get("metrics", {}),
            }

            alerts = self._check_performance_alerts(metrics)

            return MonitoringResult(timestamp=timestamp, metrics=metrics, alerts=alerts, success=True)

        except Exception as e:
            error_msg = f"Failed to monitor performance: {e}"
            logger.error(error_msg)
            return MonitoringResult(
                timestamp=time.time(),
                metrics={},
                alerts=[],
                success=False,
                error_message=error_msg,
            )

    def run_full_monitoring_check(self) -> dict[str, MonitoringResult]:
        """
        Run comprehensive monitoring checks across all databases.

        Returns:
            Dictionary mapping check names to MonitoringResult objects
        """
        results = {}

        # Server status
        results["server_status"] = self.monitor_server_status()

        # Performance
        results["performance"] = self.monitor_performance()

        # Database stats for all databases
        try:
            database_names = self.client.list_database_names()
            for db_name in database_names:
                results[f"database_{db_name}"] = self.monitor_database_stats(db_name)

                # Collection stats for each database
                try:
                    db = self.client[db_name]
                    collection_names = db.list_collection_names()
                    for coll_name in collection_names[:5]:  # Limit to first 5 collections
                        results[f"collection_{db_name}_{coll_name}"] = self.monitor_collection_stats(db_name, coll_name)
                except Exception as e:
                    logger.warning(f"Could not list collections for {db_name}: {e}")

        except Exception as e:
            logger.error(f"Could not list databases: {e}")

        return results

    def _check_server_alerts(self, metrics: dict[str, Any]) -> list[Alert]:
        """Check server metrics and generate alerts."""
        alerts = []

        # CPU usage alert
        cpu_percent = metrics.get("cpu", {}).get("percent", 0)
        if cpu_percent > self.thresholds["cpu_usage_percent"]:
            alerts.append(
                Alert(
                    alert_type=AlertType.HIGH_CPU_USAGE,
                    severity=AlertSeverity.WARNING,
                    message=f"High CPU usage: {cpu_percent:.1f}%",
                    source=metrics.get("host", "unknown"),
                    timestamp=time.time(),
                    threshold=self.thresholds["cpu_usage_percent"],
                    current_value=cpu_percent,
                )
            )

        # Memory usage alert
        memory_info = metrics.get("memory", {})
        if memory_info:
            mem_resident = memory_info.get("resident", 0)
            mem_virtual = memory_info.get("virtual", 0)
            # Simple heuristic: if resident memory > 80% of virtual, alert
            if mem_virtual > 0 and (mem_resident / mem_virtual) > 0.8:
                alerts.append(
                    Alert(
                        alert_type=AlertType.HIGH_MEMORY_USAGE,
                        severity=AlertSeverity.WARNING,
                        message=f"High memory usage: {mem_resident}MB resident, {mem_virtual}MB virtual",
                        source=metrics.get("host", "unknown"),
                        timestamp=time.time(),
                    )
                )

        # Connections alert
        connections = metrics.get("connections", {})
        current_connections = connections.get("current", 0)
        if current_connections > self.thresholds["max_connections"]:
            alerts.append(
                Alert(
                    alert_type=AlertType.CONNECTIONS_EXCEEDED,
                    severity=AlertSeverity.ERROR,
                    message=f"High connection count: {current_connections}",
                    source=metrics.get("host", "unknown"),
                    timestamp=time.time(),
                    threshold=self.thresholds["max_connections"],
                    current_value=current_connections,
                )
            )

        return alerts

    def _check_database_alerts(self, metrics: dict[str, Any]) -> list[Alert]:
        """Check database metrics and generate alerts."""
        alerts = []
        db_name = metrics.get("database", "unknown")

        # Database size alert
        db_size = metrics.get("total_size_gb", 0)
        if db_size > self.thresholds["database_size_gb"]:
            alerts.append(
                Alert(
                    alert_type=AlertType.DATABASE_SIZE_CRITICAL,
                    severity=AlertSeverity.WARNING,
                    message=f"Database size critical: {db_size:.2f}GB",
                    source=db_name,
                    timestamp=time.time(),
                    threshold=self.thresholds["database_size_gb"],
                    current_value=db_size,
                )
            )

        # Index size alert
        index_size = metrics.get("index_size_gb", 0)
        if index_size > self.thresholds["index_size_gb"]:
            alerts.append(
                Alert(
                    alert_type=AlertType.INDEX_SIZE_CRITICAL,
                    severity=AlertSeverity.WARNING,
                    message=f"Index size critical: {index_size:.2f}GB",
                    source=db_name,
                    timestamp=time.time(),
                    threshold=self.thresholds["index_size_gb"],
                    current_value=index_size,
                )
            )

        return alerts

    def _check_collection_alerts(self, metrics: dict[str, Any]) -> list[Alert]:
        """Check collection metrics and generate alerts."""
        alerts = []
        source = f"{metrics.get('database', 'unknown')}.{metrics.get('collection', 'unknown')}"

        # Collection size alert
        coll_size = metrics.get("size_gb", 0)
        if coll_size > self.thresholds["collection_size_gb"]:
            alerts.append(
                Alert(
                    alert_type=AlertType.COLLECTION_SIZE_CRITICAL,
                    severity=AlertSeverity.WARNING,
                    message=f"Collection size critical: {coll_size:.2f}GB",
                    source=source,
                    timestamp=time.time(),
                    threshold=self.thresholds["collection_size_gb"],
                    current_value=coll_size,
                )
            )

        return alerts

    def _check_performance_alerts(self, metrics: dict[str, Any]) -> list[Alert]:
        """Check performance metrics and generate alerts."""
        alerts = []

        # Lock contention alert
        global_lock = metrics.get("global_lock", {})
        lock_ratio = global_lock.get("ratio", 0)
        if lock_ratio > 0.1:  # More than 10% lock time
            alerts.append(
                Alert(
                    alert_type=AlertType.LOCK_CONTENTION,
                    severity=AlertSeverity.WARNING,
                    message=f"High lock contention: {lock_ratio:.3f} ratio",
                    source=metrics.get("host", "unknown"),
                    timestamp=time.time(),
                    current_value=lock_ratio,
                )
            )

        # Cache pressure alert (simplified)
        opcounters = metrics.get("opcounters", {})
        query_count = opcounters.get("query", 0)
        if query_count > 10000:  # High query rate
            alerts.append(
                Alert(
                    alert_type=AlertType.CACHE_PRESSURE,
                    severity=AlertSeverity.INFO,
                    message=f"High query rate detected: {query_count} queries",
                    source=metrics.get("host", "unknown"),
                    timestamp=time.time(),
                    current_value=query_count,
                )
            )

        return alerts

    def update_thresholds(self, new_thresholds: dict[str, int | float]) -> None:
        """Update monitoring thresholds."""
        self.thresholds.update(new_thresholds)
        logger.info(f"Updated monitoring thresholds: {new_thresholds}")
