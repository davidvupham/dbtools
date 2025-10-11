"""
Edge tests for gds_snowflake.table
"""

from unittest.mock import MagicMock

import pytest

from gds_snowflake.table import SnowflakeTable


def test_get_table_info_exception_path():
    """Test: get table info exception path."""
    conn = MagicMock()
    tbl = SnowflakeTable(conn)
    conn.execute_query_dict.side_effect = RuntimeError('boom')
    with pytest.raises(RuntimeError, match='boom'):
        tbl.get_table_info('T')
