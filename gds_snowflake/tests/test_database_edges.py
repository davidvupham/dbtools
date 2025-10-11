"""
Edge tests for gds_snowflake.database
"""

from unittest.mock import MagicMock

import pytest

from gds_snowflake.database import SnowflakeDatabase


def test_functions_with_filters_and_empty():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.return_value = []
    res = db.get_functions(database_name='DB', schema_name='SCH')
    assert res == []
    q, params = conn.execute_query_dict.call_args[0]
    assert 'FUNCTION_CATALOG' in q and 'FUNCTION_SCHEMA' in q
    assert params == ('DB', 'SCH')


def test_procedures_error_path():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.side_effect = RuntimeError('fail')
    with pytest.raises(RuntimeError, match='fail'):
        db.get_procedures()


def test_sequences_with_filters():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.return_value = []
    db.get_sequences(database_name='DB', schema_name='SCH')
    _, params = conn.execute_query_dict.call_args[0]
    assert params == ('DB', 'SCH')


def test_stages_empty_no_filters():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.return_value = []
    assert db.get_stages() == []


def test_file_formats_error_path():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.side_effect = ValueError('bad')
    with pytest.raises(ValueError, match='bad'):
        db.get_file_formats()


def test_pipes_with_filters():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.return_value = []
    db.get_pipes(database_name='DB', schema_name='SCH')
    _, params = conn.execute_query_dict.call_args[0]
    assert params == ('DB', 'SCH')


def test_tasks_error_path():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.side_effect = RuntimeError('down')
    with pytest.raises(RuntimeError, match='down'):
        db.get_tasks()


def test_streams_with_filters_and_empty():
    conn = MagicMock()
    db = SnowflakeDatabase(conn)
    conn.execute_query_dict.return_value = []
    assert db.get_streams(database_name='DB', schema_name='SCH') == []
    _, params = conn.execute_query_dict.call_args[0]
    assert params == ('DB', 'SCH')
