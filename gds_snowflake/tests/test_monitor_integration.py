"""
Integration tests for monitor_snowflake_replication_v2
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
from io import StringIO
from datetime import datetime, timedelta

# Add snowflake_monitoring directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'snowflake_monitoring'))

# Import the module
import monitor_snowflake_replication_v2 as monitor


class TestEmailNotification(unittest.TestCase):
    """Test cases for email notification functionality"""
    
    @patch('monitor_snowflake_replication_v2.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_USER': 'user@test.com',
        'SMTP_PASSWORD': 'password',
        'FROM_EMAIL': 'monitor@test.com',
        'TO_EMAILS': 'admin1@test.com,admin2@test.com'
    })
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        monitor.send_email_notification(
            subject='Test Subject',
            body='Test Body'
        )
        
        mock_smtp.assert_called_once_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('user@test.com', 'password')
        mock_server.send_message.assert_called_once()
        
    @patch('monitor_snowflake_replication_v2.smtplib.SMTP')
    def test_send_email_missing_config(self, mock_smtp):
        """Test email sending with missing configuration"""
        # Should not raise exception, just log error
        monitor.send_email_notification(
            subject='Test',
            body='Test'
        )
        
        # Should not attempt to send
        mock_smtp.assert_not_called()
        
    @patch('monitor_snowflake_replication_v2.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_USER': 'user@test.com',
        'SMTP_PASSWORD': 'password',
        'FROM_EMAIL': 'monitor@test.com',
        'TO_EMAILS': ''  # Empty recipients
    })
    def test_send_email_no_recipients(self, mock_smtp):
        """Test email sending with no recipients"""
        monitor.send_email_notification(
            subject='Test',
            body='Test'
        )
        
        # Should not attempt to send
        mock_smtp.assert_not_called()
        
    @patch('monitor_snowflake_replication_v2.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_USER': 'user@test.com',
        'SMTP_PASSWORD': 'password',
        'FROM_EMAIL': 'monitor@test.com',
        'TO_EMAILS': 'admin@test.com'
    })
    def test_send_email_failure(self, mock_smtp):
        """Test email sending failure"""
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP error")
        
        # Should not raise exception, just log error
        monitor.send_email_notification(
            subject='Test',
            body='Test'
        )


class TestProcessFailoverGroup(unittest.TestCase):
    """Test cases for process_failover_group function"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear notification tracking
        monitor.notified_failures = set()
        
    @patch('monitor_snowflake_replication_v2.send_email_notification')
    def test_process_failover_group_with_failure(self, mock_email):
        """Test processing failover group with failure"""
        from gds_snowflake.replication import FailoverGroup
        
        fg = FailoverGroup('FG1', {
            'type': 'SECONDARY',
            'primary': 'ACCOUNT1',
            'replication_schedule': 'USING CRON */10 * * * * UTC',
            'next_scheduled_refresh': '2025-10-02 11:00:00'
        })
        
        mock_replication = Mock()
        mock_replication.check_replication_failure.return_value = (True, "Connection timeout")
        mock_replication.check_replication_latency.return_value = (False, None)
        
        mock_connection = Mock()
        mock_connection.account = 'ACCOUNT2'
        
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT2'
        )
        
        # Should send failure email
        mock_email.assert_called()
        call_args = mock_email.call_args
        self.assertIn('Failure', call_args[1]['subject'])
        
        # Should track notification
        self.assertIn('FG1_failure', monitor.notified_failures)
        
    @patch('monitor_snowflake_replication_v2.send_email_notification')
    def test_process_failover_group_with_latency(self, mock_email):
        """Test processing failover group with latency"""
        from gds_snowflake.replication import FailoverGroup
        
        fg = FailoverGroup('FG1', {
            'type': 'SECONDARY',
            'primary': 'ACCOUNT1',
            'replication_schedule': 'USING CRON */10 * * * * UTC',
            'next_scheduled_refresh': '2025-10-02 11:00:00'
        })
        
        mock_replication = Mock()
        mock_replication.check_replication_failure.return_value = (False, None)
        mock_replication.check_replication_latency.return_value = (True, "Latency detected")
        
        mock_connection = Mock()
        mock_connection.account = 'ACCOUNT2'
        
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT2'
        )
        
        # Should send latency email
        mock_email.assert_called()
        call_args = mock_email.call_args
        self.assertIn('Latency', call_args[1]['subject'])
        
        # Should track notification
        self.assertIn('FG1_latency', monitor.notified_failures)
        
    @patch('monitor_snowflake_replication_v2.send_email_notification')
    def test_process_failover_group_no_duplicate_notifications(self, mock_email):
        """Test that notifications are only sent once"""
        from gds_snowflake.replication import FailoverGroup
        
        fg = FailoverGroup('FG1', {
            'type': 'SECONDARY',
            'primary': 'ACCOUNT1',
            'replication_schedule': 'USING CRON */10 * * * * UTC'
        })
        
        mock_replication = Mock()
        mock_replication.check_replication_failure.return_value = (True, "Error")
        mock_replication.check_replication_latency.return_value = (False, None)
        
        mock_connection = Mock()
        mock_connection.account = 'ACCOUNT2'
        
        # First call - should send email
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT2'
        )
        self.assertEqual(mock_email.call_count, 1)
        
        # Second call - should NOT send email
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT2'
        )
        self.assertEqual(mock_email.call_count, 1)  # Still 1
        
    @patch('monitor_snowflake_replication_v2.send_email_notification')
    def test_process_failover_group_clears_notification_on_success(self, mock_email):
        """Test that notification flag is cleared when issue resolves"""
        from gds_snowflake.replication import FailoverGroup
        
        fg = FailoverGroup('FG1', {
            'type': 'SECONDARY',
            'primary': 'ACCOUNT1',
            'replication_schedule': 'USING CRON */10 * * * * UTC'
        })
        
        mock_replication = Mock()
        mock_connection = Mock()
        mock_connection.account = 'ACCOUNT2'
        
        # First: failure
        monitor.notified_failures.add('FG1_failure')
        mock_replication.check_replication_failure.return_value = (False, None)
        mock_replication.check_replication_latency.return_value = (False, None)
        
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT2'
        )
        
        # Should clear the flag
        self.assertNotIn('FG1_failure', monitor.notified_failures)
        
    @patch('monitor_snowflake_replication_v2.send_email_notification')
    def test_process_failover_group_from_primary(self, mock_email):
        """Test processing from primary account (should switch)"""
        from gds_snowflake.replication import FailoverGroup
        
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'primary': 'ACCOUNT1',
            'secondary_state': 'ACCOUNT2:READY',
            'replication_schedule': 'USING CRON */10 * * * * UTC'
        })
        
        mock_replication = Mock()
        mock_replication.check_replication_failure.return_value = (False, None)
        mock_replication.check_replication_latency.return_value = (False, None)
        mock_replication.switch_to_secondary_account.return_value = True
        
        mock_connection = Mock()
        mock_connection.account = 'ACCOUNT1'
        
        monitor.process_failover_group(
            fg, mock_replication, mock_connection, 'ACCOUNT1'
        )
        
        # Should attempt to switch to secondary
        mock_replication.switch_to_secondary_account.assert_called_once_with(fg, 'ACCOUNT1')


class TestMonitorFailoverGroups(unittest.TestCase):
    """Test cases for monitor_failover_groups function"""
    
    @patch('monitor_snowflake_replication_v2.SnowflakeReplication')
    @patch('monitor_snowflake_replication_v2.SnowflakeConnection')
    @patch.dict(os.environ, {
        'SNOWFLAKE_USER': 'testuser',
        'SNOWFLAKE_PASSWORD': 'testpass'
    })
    def test_monitor_failover_groups_success(self, mock_conn_class, mock_repl_class):
        """Test successful monitoring cycle"""
        from gds_snowflake.replication import FailoverGroup
        
        # Setup mocks
        mock_connection = Mock()
        mock_conn_class.return_value = mock_connection
        
        mock_replication = Mock()
        mock_repl_class.return_value = mock_replication
        
        fg1 = FailoverGroup('FG1', {'type': 'PRIMARY', 'replication_schedule': 'USING CRON */10 * * * * UTC'})
        fg2 = FailoverGroup('FG2', {'type': 'SECONDARY', 'replication_schedule': 'USING CRON */30 * * * * UTC'})
        mock_replication.get_failover_groups.return_value = [fg1, fg2]
        
        mock_replication.check_replication_failure.return_value = (False, None)
        mock_replication.check_replication_latency.return_value = (False, None)
        
        # Call function
        monitor.monitor_failover_groups('testaccount')
        
        # Verify
        mock_conn_class.assert_called_once()
        mock_connection.connect.assert_called_once()
        mock_replication.get_failover_groups.assert_called_once()
        mock_connection.close.assert_called_once()
        
    @patch('monitor_snowflake_replication_v2.SnowflakeConnection')
    def test_monitor_failover_groups_missing_credentials(self, mock_conn_class):
        """Test monitoring with missing credentials"""
        with self.assertRaises(ValueError) as context:
            monitor.monitor_failover_groups('testaccount')
        
        self.assertIn('credentials', str(context.exception).lower())
        
    @patch('monitor_snowflake_replication_v2.SnowflakeReplication')
    @patch('monitor_snowflake_replication_v2.SnowflakeConnection')
    @patch.dict(os.environ, {
        'SNOWFLAKE_USER': 'testuser',
        'SNOWFLAKE_PASSWORD': 'testpass'
    })
    def test_monitor_failover_groups_no_failover_groups(self, mock_conn_class, mock_repl_class):
        """Test monitoring when no failover groups found"""
        mock_connection = Mock()
        mock_conn_class.return_value = mock_connection
        
        mock_replication = Mock()
        mock_repl_class.return_value = mock_replication
        mock_replication.get_failover_groups.return_value = []
        
        # Should not raise exception
        monitor.monitor_failover_groups('testaccount')
        
        mock_connection.close.assert_called_once()
        
    @patch('monitor_snowflake_replication_v2.SnowflakeReplication')
    @patch('monitor_snowflake_replication_v2.SnowflakeConnection')
    @patch.dict(os.environ, {
        'SNOWFLAKE_USER': 'testuser',
        'SNOWFLAKE_PASSWORD': 'testpass'
    })
    def test_monitor_failover_groups_connection_error(self, mock_conn_class, mock_repl_class):
        """Test monitoring with connection error"""
        mock_connection = Mock()
        mock_connection.connect.side_effect = Exception("Connection failed")
        mock_conn_class.return_value = mock_connection
        
        with self.assertRaises(Exception) as context:
            monitor.monitor_failover_groups('testaccount')
        
        self.assertIn("Connection failed", str(context.exception))
        mock_connection.close.assert_called_once()


class TestMainFunction(unittest.TestCase):
    """Test cases for main function"""
    
    @patch('monitor_snowflake_replication_v2.monitor_failover_groups')
    @patch('sys.argv', ['script.py', 'testaccount', '--once'])
    def test_main_once_mode(self, mock_monitor):
        """Test main function in one-time mode"""
        try:
            monitor.main()
        except SystemExit:
            pass  # main() may call sys.exit
        
        # Should call monitor once
        mock_monitor.assert_called_once()
        
    @patch('monitor_snowflake_replication_v2.monitor_failover_groups')
    @patch('monitor_snowflake_replication_v2.time.sleep')
    @patch('sys.argv', ['script.py', 'testaccount', '--interval', '30'])
    def test_main_continuous_mode(self, mock_sleep, mock_monitor):
        """Test main function in continuous mode"""
        # Simulate KeyboardInterrupt after one iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        try:
            monitor.main()
        except (SystemExit, KeyboardInterrupt):
            pass
        
        # Should call monitor at least once
        self.assertGreaterEqual(mock_monitor.call_count, 1)


if __name__ == '__main__':
    unittest.main()
