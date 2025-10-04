"""
Snowflake Monitor Class

A comprehensive monitoring class for Snowflake accounts, providing:
- Connectivity monitoring
- Replication failure detection
- Replication latency monitoring
- Email notifications
- Configurable alerts and thresholds
"""

import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

from gds_snowflake import SnowflakeConnection, SnowflakeReplication, FailoverGroup


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class MonitoringResult:
    """Result of a monitoring operation"""
    success: bool
    timestamp: datetime
    account: str
    message: str
    details: Dict[str, Any]
    severity: AlertSeverity = AlertSeverity.INFO


@dataclass
class ConnectivityResult:
    """Result of connectivity monitoring"""
    success: bool
    response_time_ms: float
    account_info: Dict[str, str]
    error: Optional[str]
    timestamp: datetime


@dataclass
class ReplicationResult:
    """Result of replication monitoring"""
    failover_group: str
    has_failure: bool
    has_latency: bool
    latency_minutes: Optional[float]
    failure_message: Optional[str]
    latency_message: Optional[str]
    last_refresh: Optional[datetime]
    next_refresh: Optional[datetime]


class SnowflakeMonitor:
    """
    Comprehensive Snowflake monitoring class.

    Provides monitoring capabilities for:
    - Account connectivity
    - Replication failures
    - Replication latency
    - Custom metrics
    """

    def __init__(
        self,
        account: str,
        user: Optional[str] = None,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
        database: Optional[str] = None,
        # Email configuration
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None,
        # Monitoring configuration
        connectivity_timeout: int = 30,
        latency_threshold_minutes: float = 30.0,
        enable_email_alerts: bool = True,
        # Vault configuration (optional - will use env vars if not provided)
        vault_namespace: Optional[str] = None,
        vault_secret_path: Optional[str] = None,
        vault_mount_point: Optional[str] = None,
        vault_role_id: Optional[str] = None,
        vault_secret_id: Optional[str] = None,
        vault_addr: Optional[str] = None,
    ):
        """
        Initialize Snowflake Monitor.

        Args:
            account: Snowflake account name
            user: Username (optional, can use SNOWFLAKE_USER env var)
            warehouse: Warehouse name (optional)
            role: Role name (optional)
            database: Database name (optional)
            smtp_server: SMTP server for email notifications
            smtp_port: SMTP port (default: 587)
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
            to_emails: List of recipient email addresses
            connectivity_timeout: Timeout for connectivity tests (seconds)
            latency_threshold_minutes: Threshold for latency alerts (minutes)
            enable_email_alerts: Whether to send email alerts
            vault_*: Vault configuration parameters (optional)
        """
        self.account = account
        self.connectivity_timeout = connectivity_timeout
        self.latency_threshold_minutes = latency_threshold_minutes
        self.enable_email_alerts = enable_email_alerts

        # Email configuration
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_emails = to_emails or []

        # Tracking for notifications (to avoid spam)
        self.notified_failures: Set[str] = set()
        self.notified_connectivity: bool = False

        # Create Snowflake connection
        self.connection = SnowflakeConnection(
            account=account,
            user=user,
            warehouse=warehouse,
            role=role,
            database=database,
            vault_namespace=vault_namespace,
            vault_secret_path=vault_secret_path,
            vault_mount_point=vault_mount_point,
            vault_role_id=vault_role_id,
            vault_secret_id=vault_secret_id,
            vault_addr=vault_addr,
        )

        self.replication = None
        self.logger = logging.getLogger(__name__)

    def monitor_connectivity(self) -> ConnectivityResult:
        """
        Monitor Snowflake account connectivity.

        Returns:
            ConnectivityResult with connectivity status and diagnostics
        """
        self.logger.info("Starting connectivity monitoring for account: %s", self.account)

        try:
            # Test connectivity using the connection's built-in method
            test_result = self.connection.test_connectivity(
                timeout_seconds=self.connectivity_timeout
            )

            result = ConnectivityResult(
                success=test_result['success'],
                response_time_ms=test_result['response_time_ms'],
                account_info=test_result['account_info'],
                error=test_result.get('error'),
                timestamp=datetime.fromisoformat(test_result['timestamp'])
            )

            if result.success:
                self.logger.info(
                    "✓ Connectivity OK for %s (%sms)",
                    self.account,
                    result.response_time_ms
                )
                # Reset connectivity notification flag on success
                self.notified_connectivity = False
            else:
                self.logger.error(
                    "✗ Connectivity FAILED for %s: %s",
                    self.account,
                    result.error
                )
                # Send alert if enabled and not already notified
                if self.enable_email_alerts and not self.notified_connectivity:
                    self._send_connectivity_alert(result)
                    self.notified_connectivity = True

            return result

        except Exception as e:
            self.logger.error("Error in connectivity monitoring: %s", str(e))
            result = ConnectivityResult(
                success=False,
                response_time_ms=0,
                account_info={},
                error=str(e),
                timestamp=datetime.now()
            )

            # Send alert if enabled and not already notified
            if self.enable_email_alerts and not self.notified_connectivity:
                self._send_connectivity_alert(result)
                self.notified_connectivity = True

            return result

    def monitor_replication_failures(self) -> List[ReplicationResult]:
        """
        Monitor replication failures for all failover groups.

        Returns:
            List of ReplicationResult objects for each failover group
        """
        self.logger.info("Starting replication failure monitoring")

        results = []

        try:
            # Ensure we have a connection and replication handler
            if not self.replication:
                self.connection.connect()
                self.replication = SnowflakeReplication(self.connection)

            # Get all failover groups
            failover_groups = self.replication.get_failover_groups()

            if not failover_groups:
                self.logger.warning("No failover groups found")
                return results

            self.logger.info("Found %s failover groups to monitor", len(failover_groups))

            for fg in failover_groups:
                result = self._check_failover_group_failures(fg)
                results.append(result)

                # Send alert if failure detected and not already notified
                if (result.has_failure and
                    self.enable_email_alerts and
                    fg.name not in self.notified_failures):

                    self._send_replication_failure_alert(result)
                    self.notified_failures.add(fg.name)
                elif not result.has_failure and fg.name in self.notified_failures:
                    # Remove from notified set if failure is resolved
                    self.notified_failures.discard(fg.name)

            return results

        except Exception as e:
            self.logger.error("Error in replication failure monitoring: %s", str(e))
            return results

    def monitor_replication_latency(self) -> List[ReplicationResult]:
        """
        Monitor replication latency for all failover groups.

        Returns:
            List of ReplicationResult objects with latency information
        """
        self.logger.info("Starting replication latency monitoring")

        results = []

        try:
            # Ensure we have a connection and replication handler
            if not self.replication:
                self.connection.connect()
                self.replication = SnowflakeReplication(self.connection)

            # Get all failover groups
            failover_groups = self.replication.get_failover_groups()

            if not failover_groups:
                self.logger.warning("No failover groups found")
                return results

            for fg in failover_groups:
                result = self._check_failover_group_latency(fg)
                results.append(result)

                # Send alert if latency exceeds threshold
                if (result.has_latency and
                    self.enable_email_alerts and
                    f"{fg.name}_latency" not in self.notified_failures):

                    self._send_replication_latency_alert(result)
                    self.notified_failures.add(f"{fg.name}_latency")
                elif not result.has_latency:
                    # Remove from notified set if latency is resolved
                    self.notified_failures.discard(f"{fg.name}_latency")

            return results

        except Exception as e:
            self.logger.error("Error in replication latency monitoring: %s", str(e))
            return results

    def monitor_all(self) -> Dict[str, Any]:
        """
        Run all monitoring checks and return comprehensive results.

        Returns:
            Dictionary containing all monitoring results
        """
        self.logger.info("Starting comprehensive monitoring")

        # Track start time
        start_time = datetime.now()

        results = {
            'timestamp': start_time.isoformat(),
            'account': self.account,
            'connectivity': None,
            'replication_failures': [],
            'replication_latency': [],
            'summary': {
                'connectivity_ok': False,
                'total_failover_groups': 0,
                'groups_with_failures': 0,
                'groups_with_latency': 0,
                'monitoring_duration_ms': 0
            }
        }

        try:
            # 1. Check connectivity first
            connectivity_result = self.monitor_connectivity()
            results['connectivity'] = connectivity_result
            results['summary']['connectivity_ok'] = connectivity_result.success

            # Skip replication monitoring if connectivity fails
            if not connectivity_result.success:
                self.logger.warning("Skipping replication monitoring due to connectivity failure")
                return results

            # 2. Check replication failures
            failure_results = self.monitor_replication_failures()
            results['replication_failures'] = failure_results

            # 3. Check replication latency
            latency_results = self.monitor_replication_latency()
            results['replication_latency'] = latency_results

            # Calculate summary statistics
            all_fg_names = set()
            if failure_results:
                all_fg_names.update(r.failover_group for r in failure_results)
            if latency_results:
                all_fg_names.update(r.failover_group for r in latency_results)

            results['summary'].update({
                'total_failover_groups': len(all_fg_names),
                'groups_with_failures': sum(1 for r in failure_results if r.has_failure),
                'groups_with_latency': sum(1 for r in latency_results if r.has_latency),
            })

        except Exception as e:
            self.logger.error("Error in comprehensive monitoring: %s", str(e))
            results['error'] = str(e)

        finally:
            # Calculate duration
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            results['summary']['monitoring_duration_ms'] = round(duration_ms, 2)

            conn_status = 'OK' if results['summary']['connectivity_ok'] else 'FAILED'
            self.logger.info(
                "Monitoring completed in %.2fms - Connectivity: %s, "
                "Groups: %s, Failures: %s, Latency Issues: %s",
                duration_ms,
                conn_status,
                results['summary']['total_failover_groups'],
                results['summary']['groups_with_failures'],
                results['summary']['groups_with_latency']
            )

        return results

    def _check_failover_group_failures(self, failover_group: FailoverGroup) -> ReplicationResult:
        """Check a single failover group for replication failures."""
        try:
            has_failure, failure_msg = self.replication.check_replication_failure(failover_group)

            return ReplicationResult(
                failover_group=failover_group.name,
                has_failure=has_failure,
                has_latency=False,  # Will be checked separately
                latency_minutes=None,
                failure_message=failure_msg if has_failure else None,
                latency_message=None,
                last_refresh=getattr(failover_group, 'last_refresh_time', None),
                next_refresh=getattr(failover_group, 'next_scheduled_refresh', None)
            )

        except Exception as e:
            self.logger.error("Error checking failures for %s: %s", failover_group.name, str(e))
            return ReplicationResult(
                failover_group=failover_group.name,
                has_failure=True,
                has_latency=False,
                latency_minutes=None,
                failure_message=f"Error checking failures: {str(e)}",
                latency_message=None,
                last_refresh=None,
                next_refresh=None
            )

    def _check_failover_group_latency(self, failover_group: FailoverGroup) -> ReplicationResult:
        """Check a single failover group for replication latency."""
        try:
            has_latency, latency_msg = self.replication.check_replication_latency(failover_group)

            # Extract latency value if available
            latency_minutes = None
            if has_latency and "minutes" in latency_msg:
                try:
                    # Parse latency from message like "Replication latency: 45.2 minutes"
                    parts = latency_msg.split()
                    for i, part in enumerate(parts):
                        if "minute" in part and i > 0:
                            latency_minutes = float(parts[i-1])
                            break
                except (ValueError, IndexError):
                    pass

            # Check against our threshold
            threshold_exceeded = (
                latency_minutes is not None and
                latency_minutes > self.latency_threshold_minutes
            )

            return ReplicationResult(
                failover_group=failover_group.name,
                has_failure=False,  # Will be checked separately
                has_latency=has_latency or threshold_exceeded,
                latency_minutes=latency_minutes,
                failure_message=None,
                latency_message=latency_msg if (has_latency or threshold_exceeded) else None,
                last_refresh=getattr(failover_group, 'last_refresh_time', None),
                next_refresh=getattr(failover_group, 'next_scheduled_refresh', None)
            )

        except Exception as e:
            self.logger.error("Error checking latency for %s: %s", failover_group.name, str(e))
            return ReplicationResult(
                failover_group=failover_group.name,
                has_failure=False,
                has_latency=True,
                latency_minutes=None,
                failure_message=None,
                latency_message=f"Error checking latency: {str(e)}",
                last_refresh=None,
                next_refresh=None
            )

    def _send_connectivity_alert(self, result: ConnectivityResult):
        """Send email alert for connectivity issues."""
        subject = f"🚨 Snowflake Connectivity Alert - {self.account}"

        body = f"""
Snowflake connectivity test failed for account: {self.account}

Test Results:
- Success: {result.success}
- Response Time: {result.response_time_ms} ms
- Error: {result.error or 'Unknown error'}
- Timestamp: {result.timestamp.isoformat()}

Account Information:
{self._format_account_info(result.account_info)}

This could indicate:
1. Network connectivity issues
2. Snowflake service disruption
3. Authentication problems
4. Account suspension or configuration issues

Please investigate immediately.

---
Snowflake Monitor
Account: {self.account}
        """

        self._send_email(subject.strip(), body.strip(), AlertSeverity.CRITICAL)

    def _send_replication_failure_alert(self, result: ReplicationResult):
        """Send email alert for replication failures."""
        subject = f"🚨 Snowflake Replication Failure - {result.failover_group}"

        body = f"""
Replication failure detected for failover group: {result.failover_group}
Account: {self.account}

Failure Details:
- Failover Group: {result.failover_group}
- Error Message: {result.failure_message}
- Last Refresh: {result.last_refresh or 'Unknown'}
- Next Refresh: {result.next_refresh or 'Unknown'}

Please investigate the replication status and resolve any issues.

---
Snowflake Monitor
Account: {self.account}
        """

        self._send_email(subject.strip(), body.strip(), AlertSeverity.CRITICAL)

    def _send_replication_latency_alert(self, result: ReplicationResult):
        """Send email alert for replication latency issues."""
        subject = f"⚠️ Snowflake Replication Latency - {result.failover_group}"

        body = f"""
Replication latency detected for failover group: {result.failover_group}
Account: {self.account}

Latency Details:
- Failover Group: {result.failover_group}
- Latency: {result.latency_minutes or 'Unknown'} minutes
- Threshold: {self.latency_threshold_minutes} minutes
- Message: {result.latency_message}
- Last Refresh: {result.last_refresh or 'Unknown'}
- Next Refresh: {result.next_refresh or 'Unknown'}

Please monitor the replication performance and investigate if necessary.

---
Snowflake Monitor
Account: {self.account}
        """

        self._send_email(subject.strip(), body.strip(), AlertSeverity.WARNING)

    def _send_email(self, subject: str, body: str, severity: AlertSeverity):
        """Send email notification."""
        if not self.enable_email_alerts:
            return

        if not all([self.smtp_server, self.from_email, self.to_emails,
                   self.smtp_user, self.smtp_password]):
            self.logger.warning("Email configuration incomplete. Skipping email notification.")
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            self.logger.info("Sending %s email notification: %s", severity.value, subject)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            self.logger.info("Email notification sent successfully")

        except Exception as e:
            self.logger.error("Failed to send email notification: %s", e)

    def _format_account_info(self, account_info: Dict[str, str]) -> str:
        """Format account information for display."""
        if not account_info:
            return "No account information available"

        lines = []
        for key, value in account_info.items():
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")

        return "\n".join(lines)

    def close(self):
        """Clean up resources."""
        if self.connection:
            self.connection.close()

        # Clear notification tracking
        self.notified_failures.clear()
        self.notified_connectivity = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
