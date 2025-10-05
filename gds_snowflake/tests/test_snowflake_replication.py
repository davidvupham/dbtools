"""
Unit tests for gds_snowflake.replication module
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from gds_snowflake.replication import FailoverGroup, SnowflakeReplication


class TestFailoverGroup(unittest.TestCase):
    """Test cases for FailoverGroup class"""

    def setUp(self):
        """Set up test fixtures"""
        self.fg_name = 'TEST_FG'
        self.properties = {
            'type': 'PRIMARY',
            'primary': 'ACCOUNT1.US-WEST-2',
            'secondary_state': 'ACCOUNT2.US-EAST-1:READY, ACCOUNT3.EU-WEST-1:READY',
            'replication_schedule': 'USING CRON */15 * * * * UTC',
            'next_scheduled_refresh': '2025-10-02 11:00:00',
            'allowed_databases': 'DB1, DB2',
            'allowed_shares': 'SHARE1',
            'allowed_integration_types': 'API_INTEGRATION'
        }

    def test_init(self):
        """Test FailoverGroup initialization"""
        fg = FailoverGroup(self.fg_name, self.properties)

        self.assertEqual(fg.name, self.fg_name)
        self.assertEqual(fg.type, 'PRIMARY')
        self.assertEqual(fg.primary_account, 'ACCOUNT1.US-WEST-2')
        self.assertEqual(fg.replication_schedule, 'USING CRON */15 * * * * UTC')
        self.assertEqual(fg.next_scheduled_refresh, '2025-10-02 11:00:00')
        self.assertEqual(len(fg.secondary_accounts), 2)

    def test_parse_secondary_accounts(self):
        """Test parsing secondary accounts from state string"""
        fg = FailoverGroup(self.fg_name, self.properties)

        self.assertIn('ACCOUNT2.US-EAST-1', fg.secondary_accounts)
        self.assertIn('ACCOUNT3.EU-WEST-1', fg.secondary_accounts)

    def test_parse_secondary_accounts_empty(self):
        """Test parsing empty secondary state"""
        props = self.properties.copy()
        props['secondary_state'] = ''

        fg = FailoverGroup(self.fg_name, props)

        self.assertEqual(len(fg.secondary_accounts), 0)

    def test_parse_secondary_accounts_no_colon(self):
        """Test parsing secondary state without status"""
        props = self.properties.copy()
        props['secondary_state'] = 'ACCOUNT2, ACCOUNT3'

        fg = FailoverGroup(self.fg_name, props)

        # Should handle gracefully
        self.assertIsInstance(fg.secondary_accounts, list)

    def test_is_primary_exact_match(self):
        """Test is_primary with exact account match"""
        fg = FailoverGroup(self.fg_name, self.properties)

        self.assertTrue(fg.is_primary('ACCOUNT1.US-WEST-2'))
        self.assertTrue(fg.is_primary('account1.us-west-2'))  # Case insensitive

    def test_is_primary_partial_match(self):
        """Test is_primary with partial account match"""
        fg = FailoverGroup(self.fg_name, self.properties)

        self.assertTrue(fg.is_primary('ACCOUNT1'))
        self.assertTrue(fg.is_primary('account1'))

    def test_is_primary_not_primary(self):
        """Test is_primary returns False for secondary"""
        fg = FailoverGroup(self.fg_name, self.properties)

        self.assertFalse(fg.is_primary('ACCOUNT2'))
        self.assertFalse(fg.is_primary('ACCOUNT3'))
        self.assertFalse(fg.is_primary('ACCOUNT4'))

    def test_get_secondary_account(self):
        """Test getting a secondary account"""
        fg = FailoverGroup(self.fg_name, self.properties)

        secondary = fg.get_secondary_account('ACCOUNT1')

        self.assertIsNotNone(secondary)
        self.assertIn(secondary, ['ACCOUNT2.US-EAST-1', 'ACCOUNT3.EU-WEST-1'])

    def test_get_secondary_account_from_secondary(self):
        """Test getting secondary when connected to a secondary"""
        fg = FailoverGroup(self.fg_name, self.properties)

        # When connected to ACCOUNT2, should get ACCOUNT3 or None
        secondary = fg.get_secondary_account('ACCOUNT2')

        if secondary:
            self.assertNotIn('ACCOUNT2', secondary.upper())

    def test_get_secondary_account_none_available(self):
        """Test getting secondary when none available"""
        props = self.properties.copy()
        props['secondary_state'] = ''

        fg = FailoverGroup(self.fg_name, props)

        secondary = fg.get_secondary_account('ACCOUNT1')

        self.assertIsNone(secondary)

    def test_repr(self):
        """Test string representation"""
        fg = FailoverGroup(self.fg_name, self.properties)

        repr_str = repr(fg)

        self.assertIn('TEST_FG', repr_str)
        self.assertIn('PRIMARY', repr_str)
        self.assertIn('ACCOUNT1', repr_str)


class TestSnowflakeReplication(unittest.TestCase):
    """Test cases for SnowflakeReplication class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()
        self.replication = SnowflakeReplication(self.mock_connection)

    def test_init(self):
        """Test SnowflakeReplication initialization"""
        self.assertEqual(self.replication.connection, self.mock_connection)

    def test_get_failover_groups(self):
        """Test retrieving failover groups"""
        mock_results = [
            ('created_on', 'FG1', 'PRIMARY', 'region1', 'account1', 'locator1',
             None, None, 'ACCOUNT2:READY', 'USING CRON */10 * * * * UTC',
             '2025-10-02 11:00:00', 'DB1', 'SHARE1', 'API_INTEGRATION'),
            ('created_on', 'FG2', 'SECONDARY', 'region2', 'account2', 'locator2',
             None, None, '', 'USING CRON */30 * * * * UTC',
             '2025-10-02 11:30:00', 'DB2', 'SHARE2', '')
        ]

        self.mock_connection.execute_query.return_value = mock_results

        failover_groups = self.replication.get_failover_groups()

        self.mock_connection.execute_query.assert_called_once_with("SHOW FAILOVER GROUPS")
        self.assertEqual(len(failover_groups), 2)
        self.assertEqual(failover_groups[0].name, 'FG1')
        self.assertEqual(failover_groups[1].name, 'FG2')

    def test_get_failover_groups_empty(self):
        """Test retrieving failover groups when none exist"""
        self.mock_connection.execute_query.return_value = []

        failover_groups = self.replication.get_failover_groups()

        self.assertEqual(len(failover_groups), 0)

    def test_get_failover_groups_error(self):
        """Test error handling when retrieving failover groups"""
        self.mock_connection.execute_query.side_effect = Exception("Query failed")

        with self.assertRaises(Exception):
            self.replication.get_failover_groups()

    def test_get_replication_history(self):
        """Test getting replication history"""
        mock_history = [
            {
                'START_TIME': datetime(2025, 10, 2, 10, 0),
                'END_TIME': datetime(2025, 10, 2, 10, 5),
                'STATUS': 'SUCCESS',
                'MESSAGE': None
            },
            {
                'START_TIME': datetime(2025, 10, 2, 9, 50),
                'END_TIME': datetime(2025, 10, 2, 9, 54),
                'STATUS': 'SUCCESS',
                'MESSAGE': None
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        history = self.replication.get_replication_history('FG1', limit=2)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['STATUS'], 'SUCCESS')

    def test_get_replication_history_with_failures(self):
        """Test getting replication history with failures"""
        mock_history = [
            {
                'START_TIME': datetime(2025, 10, 2, 10, 0),
                'END_TIME': datetime(2025, 10, 2, 10, 5),
                'STATUS': 'FAILED',
                'MESSAGE': 'Network timeout'
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        history = self.replication.get_replication_history('FG1')

        self.assertEqual(history[0]['STATUS'], 'FAILED')
        self.assertEqual(history[0]['MESSAGE'], 'Network timeout')

    def test_parse_cron_schedule_10_minutes(self):
        """Test parsing cron schedule for 10 minute interval"""
        cron_expr = "USING CRON */10 * * * * UTC"

        interval = self.replication.parse_cron_schedule(cron_expr)

        self.assertEqual(interval, 10)

    def test_parse_cron_schedule_30_minutes(self):
        """Test parsing cron schedule for 30 minute interval"""
        cron_expr = "USING CRON */30 * * * * UTC"

        interval = self.replication.parse_cron_schedule(cron_expr)

        self.assertEqual(interval, 30)

    def test_parse_cron_schedule_hourly(self):
        """Test parsing cron schedule for hourly"""
        cron_expr = "USING CRON 0 * * * * UTC"

        interval = self.replication.parse_cron_schedule(cron_expr)

        self.assertEqual(interval, 60)

    def test_parse_cron_schedule_invalid(self):
        """Test parsing invalid cron schedule"""
        cron_expr = "INVALID CRON EXPRESSION"

        interval = self.replication.parse_cron_schedule(cron_expr)

        self.assertIsNone(interval)

    def test_parse_cron_schedule_empty(self):
        """Test parsing empty cron schedule"""
        interval = self.replication.parse_cron_schedule("")

        self.assertIsNone(interval)

    def test_check_replication_failure_success(self):
        """Test checking for failure when replication succeeded"""
        fg = FailoverGroup('FG1', {'type': 'PRIMARY'})

        mock_history = [
            {
                'STATUS': 'SUCCESS',
                'MESSAGE': None
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        is_failed, message = self.replication.check_replication_failure(fg)

        self.assertFalse(is_failed)
        self.assertIsNone(message)

    def test_check_replication_failure_failed(self):
        """Test checking for failure when replication failed"""
        fg = FailoverGroup('FG1', {'type': 'PRIMARY'})

        mock_history = [
            {
                'STATUS': 'FAILED',
                'MESSAGE': 'Connection timeout'
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        is_failed, message = self.replication.check_replication_failure(fg)

        self.assertTrue(is_failed)
        self.assertEqual(message, 'Connection timeout')

    def test_check_replication_failure_partially_failed(self):
        """Test checking for partial failure"""
        fg = FailoverGroup('FG1', {'type': 'PRIMARY'})

        mock_history = [
            {
                'STATUS': 'PARTIALLY_FAILED',
                'MESSAGE': 'Some objects failed'
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        is_failed, message = self.replication.check_replication_failure(fg)

        self.assertTrue(is_failed)
        self.assertIsNotNone(message)

    def test_check_replication_failure_no_history(self):
        """Test checking for failure with no history"""
        fg = FailoverGroup('FG1', {'type': 'PRIMARY'})

        self.mock_connection.execute_query_dict.return_value = []

        is_failed, message = self.replication.check_replication_failure(fg)

        self.assertFalse(is_failed)
        self.assertIsNone(message)

    def test_check_replication_latency_no_latency(self):
        """Test checking for latency when replication is on time"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'replication_schedule': 'USING CRON */10 * * * * UTC'
        })

        # Last run completed 5 minutes ago, took 2 minutes
        now = datetime.now()
        end_time = now - timedelta(minutes=5)
        start_time = end_time - timedelta(minutes=2)

        mock_history = [
            {
                'START_TIME': start_time,
                'END_TIME': end_time,
                'STATUS': 'SUCCESS'
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        has_latency, message = self.replication.check_replication_latency(fg)

        self.assertFalse(has_latency)
        self.assertIsNone(message)

    def test_check_replication_latency_with_latency(self):
        """Test checking for latency when replication is delayed"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'replication_schedule': 'USING CRON */10 * * * * UTC'
        })

        # Last run completed 20 minutes ago, took 2 minutes
        # Expected next: 10 (interval) + 2 (duration) + 0.2 (10% buffer) = 12.2 minutes
        # Current delay: 20 - 12.2 = 7.8 minutes late
        now = datetime.now()
        end_time = now - timedelta(minutes=20)
        start_time = end_time - timedelta(minutes=2)

        mock_history = [
            {
                'START_TIME': start_time,
                'END_TIME': end_time,
                'STATUS': 'SUCCESS'
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_history

        has_latency, message = self.replication.check_replication_latency(fg)

        self.assertTrue(has_latency)
        self.assertIsNotNone(message)
        self.assertIn('latency', message.lower())

    def test_check_replication_latency_no_schedule(self):
        """Test checking for latency with no schedule"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'replication_schedule': ''
        })

        has_latency, message = self.replication.check_replication_latency(fg)

        self.assertFalse(has_latency)
        self.assertIsNone(message)

    def test_check_replication_latency_invalid_schedule(self):
        """Test checking for latency with invalid schedule"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'replication_schedule': 'INVALID'
        })

        has_latency, message = self.replication.check_replication_latency(fg)

        self.assertFalse(has_latency)
        self.assertIsNone(message)

    def test_switch_to_secondary_account_from_primary(self):
        """Test switching from primary to secondary"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'primary': 'ACCOUNT1',
            'secondary_state': 'ACCOUNT2:READY'
        })

        result = self.replication.switch_to_secondary_account(fg, 'ACCOUNT1')

        self.assertTrue(result)
        self.mock_connection.switch_account.assert_called_once_with('ACCOUNT2')

    def test_switch_to_secondary_account_already_secondary(self):
        """Test switching when already on secondary"""
        fg = FailoverGroup('FG1', {
            'type': 'SECONDARY',
            'primary': 'ACCOUNT1',
            'secondary_state': 'ACCOUNT2:READY'
        })

        result = self.replication.switch_to_secondary_account(fg, 'ACCOUNT2')

        self.assertTrue(result)
        self.mock_connection.switch_account.assert_not_called()

    def test_switch_to_secondary_account_no_secondary(self):
        """Test switching when no secondary available"""
        fg = FailoverGroup('FG1', {
            'type': 'PRIMARY',
            'primary': 'ACCOUNT1',
            'secondary_state': ''
        })

        result = self.replication.switch_to_secondary_account(fg, 'ACCOUNT1')

        self.assertFalse(result)
        self.mock_connection.switch_account.assert_not_called()


if __name__ == '__main__':
    unittest.main()
