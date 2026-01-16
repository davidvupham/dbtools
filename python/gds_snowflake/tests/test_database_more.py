"""
Additional focused tests for gds_snowflake.database:
- get_all_database_metadata summary counts and handling of None database info
"""

from unittest.mock import MagicMock

from gds_snowflake.database import SnowflakeDatabase


def test_get_all_database_metadata_summary_and_none_entry():
    """Test: get all database metadata summary and none entry."""
    conn = MagicMock()
    db = SnowflakeDatabase(conn)

    # Simulate filtering by database_name which calls get_database_info
    # We return None (e.g., database not found), and verify summary counts
    # compute correctly
    db.get_database_info = MagicMock(return_value=None)
    db.get_schemas = MagicMock(return_value=[{"SCHEMA_NAME": "SCH"}])
    db.get_functions = MagicMock(return_value=[{"FUNCTION_NAME": "F"}])
    db.get_procedures = MagicMock(return_value=[])
    db.get_sequences = MagicMock(return_value=[])
    db.get_stages = MagicMock(return_value=[{"STAGE_NAME": "ST"}])
    db.get_file_formats = MagicMock(return_value=[])
    db.get_pipes = MagicMock(return_value=[])
    db.get_tasks = MagicMock(return_value=[{"TASK_NAME": "T1"}, {"TASK_NAME": "T2"}])
    db.get_streams = MagicMock(return_value=[])

    result = db.get_all_database_metadata(database_name="DBX", schema_name="SCH")

    # Databases list contains [None] and should not be counted in summary
    assert result["databases"] == [None]
    assert result["summary"]["database_count"] == 0
    assert result["summary"]["schema_count"] == 1
    assert result["summary"]["function_count"] == 1
    assert result["summary"]["procedure_count"] == 0
    assert result["summary"]["sequence_count"] == 0
    assert result["summary"]["stage_count"] == 1
    assert result["summary"]["file_format_count"] == 0
    assert result["summary"]["pipe_count"] == 0
    assert result["summary"]["task_count"] == 2
    assert result["summary"]["stream_count"] == 0
