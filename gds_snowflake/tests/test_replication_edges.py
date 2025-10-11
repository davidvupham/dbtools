"""
Edge tests for gds_snowflake.replication
"""

from unittest.mock import MagicMock, patch

from gds_snowflake.replication import FailoverGroup, SnowflakeReplication


def test_switch_to_secondary_already_secondary():
    """Test: switch to secondary already secondary."""
    conn = MagicMock()
    repl = SnowflakeReplication(conn)
    fg = FailoverGroup(
        'FG', {'primary': 'ACC1', 'secondary_state': 'ACC2:READY'}
    )
    # If current is ACC2 (secondary), returns True without switching
    assert repl.switch_to_secondary_account(fg, 'ACC2') is True


def test_switch_to_secondary_none_available():
    """Test: switch to secondary none available."""
    conn = MagicMock()
    repl = SnowflakeReplication(conn)
    fg = FailoverGroup('FG', {'primary': 'ACC1', 'secondary_state': ''})
    assert repl.switch_to_secondary_account(fg, 'ACC1') is False


def test_parse_cron_schedule_exception_path():
    """Test: parse cron schedule exception path."""
    conn = MagicMock()
    repl = SnowflakeReplication(conn)
    # Force croniter import path to raise by patching croniter.croniter
    with patch('gds_snowflake.replication.croniter') as cron:
        cron.side_effect = RuntimeError('bad cron')
        assert repl.parse_cron_schedule('USING CRON */10 * * * * UTC') is None
