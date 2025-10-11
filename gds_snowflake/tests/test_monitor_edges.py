"""
Edge tests for gds_snowflake.monitor email and formatting behavior.
"""

from datetime import datetime
from unittest.mock import Mock, patch

from gds_snowflake.monitor import ReplicationResult, SnowflakeMonitor


@patch('gds_snowflake.connection.get_secret_from_vault')
def test_email_skipped_on_incomplete_config(mock_vault):
    """Test: email skipped on incomplete config."""
    mock_vault.return_value = {'private_key': 'k', 'user': 'u'}
    mon = SnowflakeMonitor(
        account='acc',
        vault_secret_path='secret/path',
        enable_email_alerts=True,
        smtp_server=None,  # incomplete config
        from_email='from@example.com',
        to_emails=['to@example.com'],
        smtp_user='user',
        smtp_password='pass',
    )
    # Using protected method intentionally to validate guardrail
    with patch('gds_snowflake.monitor.smtplib.SMTP') as smtp:
        mon._send_email('subj', 'body', severity=Mock())
        smtp.assert_not_called()


@patch('gds_snowflake.connection.get_secret_from_vault')
def test_email_failure_path_logged(mock_vault):
    """Test: email failure path logged."""
    mock_vault.return_value = {'private_key': 'k', 'user': 'u'}
    mon = SnowflakeMonitor(
        account='acc',
        vault_secret_path='secret/path',
        enable_email_alerts=True,
        smtp_server='smtp.example.com',
        smtp_port=587,
        from_email='from@example.com',
        to_emails=['to@example.com'],
        smtp_user='user',
        smtp_password='pass',
    )
    with patch('gds_snowflake.monitor.smtplib.SMTP') as smtp:
        smtp.side_effect = RuntimeError('smtp down')
        # Should not raise, only log
        mon._send_email('subj', 'body', severity=Mock())


@patch('gds_snowflake.connection.get_secret_from_vault')
def test_format_account_info_and_notification_reset(mock_vault):
    """Test: format account info and notification reset."""
    mock_vault.return_value = {'private_key': 'k', 'user': 'u'}
    mon = SnowflakeMonitor(account='acc', vault_secret_path='secret/path')

    # Format account info
    formatted = mon._format_account_info(
        {'current_user': 'me', 'region': 'us'}
    )
    assert '- Current User: me' in formatted
    assert '- Region: us' in formatted

    # Notification reset on resolved failure/latency
    rr = ReplicationResult(
        failover_group='fg1',
        has_failure=True,
        has_latency=False,
        latency_minutes=None,
        failure_message='x',
        latency_message=None,
        last_refresh=datetime.now(),
        next_refresh=None,
    )
    # Seed notified and then simulate resolution
    mon.notified_failures.add('fg1')
    with patch.object(mon, 'replication') as repl:
        class FG:
            def __init__(self, name: str):
                self.name = name
        repl.get_failover_groups.return_value = [FG('fg1')]
        # First run: still failing
        with patch.object(
            mon, '_check_failover_group_failures', return_value=rr
        ):
            mon.monitor_replication_failures()
        # Next run: resolved
        rr2 = rr.__class__(
            **{**rr.__dict__, 'has_failure': False, 'failure_message': None}
        )
        with patch.object(
            mon, '_check_failover_group_failures', return_value=rr2
        ):
            mon.monitor_replication_failures()
            assert 'fg1' not in mon.notified_failures
