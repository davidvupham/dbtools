"""
Additional tests for gds_snowflake.monitor focusing on
latency threshold behavior and connectivity exception path.
"""

from unittest.mock import Mock, patch

from gds_snowflake.monitor import SnowflakeMonitor


@patch("gds_snowflake.connection.get_secret_from_vault")
def test_latency_threshold_triggers_alert_and_clears_on_recovery(mock_vault):
    # Ensure connection initialization is satisfied
    mock_vault.return_value = {"private_key": "k", "user": "u"}

    mon = SnowflakeMonitor(
        account="acc",
        vault_secret_path="secret/path",
        enable_email_alerts=True,
        smtp_server="smtp.example.com",
        smtp_port=587,
        from_email="from@example.com",
        to_emails=["to@example.com"],
        smtp_user="user",
        smtp_password="pass",
        latency_threshold_minutes=10.0,
    )

    # Pre-create a mocked replication handler to avoid real connection attempts
    mon.replication = Mock()

    class FG:
        def __init__(self, name: str):
            self.name = name

    mon.replication.get_failover_groups.return_value = [FG("fg1")]

    # First run: no explicit has_latency from replication,
    # but message indicates 15 minutes which exceeds the threshold,
    # so alert should be sent and notified set with suffix
    mon.replication.check_replication_latency.return_value = (
        True,
        "Replication latency: 15 minutes",
    )

    with patch("gds_snowflake.monitor.smtplib.SMTP") as smtp:
        results = mon.monitor_replication_latency()
        assert results and results[0].has_latency is True
        assert results[0].latency_minutes == 15.0
        # Email should be sent once for the latency condition
        assert smtp.call_count == 1
        assert "fg1_latency" in mon.notified_failures

    # Second run: latency recovered to 5 minutes (below threshold)
    # -> no email, clear notified
        mon.replication.check_replication_latency.return_value = (
            False,
            "Replication latency: 5 minutes",
        )
        results2 = mon.monitor_replication_latency()
        assert results2 and results2[0].has_latency is False
        # No additional email sent
        assert smtp.call_count == 1
        assert "fg1_latency" not in mon.notified_failures


@patch("gds_snowflake.connection.get_secret_from_vault")
def test_connectivity_exception_sets_flag_no_email_without_config(mock_vault):
    mock_vault.return_value = {"private_key": "k", "user": "u"}

    mon = SnowflakeMonitor(
        account="acc",
        vault_secret_path="secret/path",
        # enabled, but config incomplete so email won't send
        enable_email_alerts=True,
        smtp_server=None,
        from_email="from@example.com",
        to_emails=["to@example.com"],
        smtp_user="user",
        smtp_password="pass",
    )

    # Force connection.test_connectivity to raise
    mon.connection.test_connectivity = Mock(side_effect=RuntimeError("boom"))

    with patch("gds_snowflake.monitor.smtplib.SMTP") as smtp:
        res = mon.monitor_connectivity()
        assert res.success is False
        assert mon.notified_connectivity is True
        smtp.assert_not_called()
