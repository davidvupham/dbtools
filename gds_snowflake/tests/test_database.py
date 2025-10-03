"""
Unit tests for the SnowflakeDatabase class.
"""

import unittest
from unittest.mock import Mock
from gds_snowflake.database import SnowflakeDatabase


class TestSnowflakeDatabase(unittest.TestCase):
    """Test cases for SnowflakeDatabase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.metadata = SnowflakeDatabase(self.mock_connection)

    def test_init(self):
        """Test SnowflakeDatabase initialization."""
        self.assertEqual(self.metadata.connection, self.mock_connection)

    # =========================================================================
    # Database Metadata Tests
    # =========================================================================

    def test_get_databases(self):
        """Test get_databases method."""
        mock_databases = [
            {
                "DATABASE_NAME": "TEST_DB",
                "DATABASE_OWNER": "SYSADMIN",
                "IS_TRANSIENT": "NO",
                "COMMENT": "Test database",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "RETENTION_TIME": 1,
            },
            {
                "DATABASE_NAME": "PROD_DB",
                "DATABASE_OWNER": "SYSADMIN",
                "IS_TRANSIENT": "NO",
                "COMMENT": "Production database",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "RETENTION_TIME": 7,
            },
        ]
        self.mock_connection.execute_query_dict.return_value = mock_databases

        result = self.metadata.get_databases()

        self.assertEqual(result, mock_databases)
        self.mock_connection.execute_query_dict.assert_called_once()

    def test_get_database_info(self):
        """Test get_database_info method."""
        mock_database = {
            "DATABASE_NAME": "TEST_DB",
            "DATABASE_OWNER": "SYSADMIN",
            "IS_TRANSIENT": "NO",
            "COMMENT": "Test database",
            "CREATED": "2023-01-01",
            "LAST_ALTERED": "2023-01-02",
            "RETENTION_TIME": 1,
        }
        self.mock_connection.execute_query_dict.return_value = [mock_database]

        result = self.metadata.get_database_info("TEST_DB")

        self.assertEqual(result, mock_database)
        self.mock_connection.execute_query_dict.assert_called_once()
        call_args = self.mock_connection.execute_query_dict.call_args
        self.assertIn("TEST_DB", call_args[0][1])

    def test_get_database_info_not_found(self):
        """Test get_database_info when database doesn't exist."""
        self.mock_connection.execute_query_dict.return_value = []

        result = self.metadata.get_database_info("NONEXISTENT_DB")

        self.assertIsNone(result)

    # =========================================================================
    # Schema Metadata Tests
    # =========================================================================

    def test_get_schemas_all(self):
        """Test get_schemas without filters."""
        mock_schemas = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "SCHEMA_OWNER": "SYSADMIN",
                "IS_TRANSIENT": "NO",
                "IS_MANAGED_ACCESS": "NO",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "RETENTION_TIME": 1,
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_schemas

        result = self.metadata.get_schemas()

        self.assertEqual(result, mock_schemas)
        call_args = self.mock_connection.execute_query_dict.call_args
        self.assertIsNone(call_args[0][1])  # No parameters

    def test_get_schemas_filtered(self):
        """Test get_schemas with database filter."""
        mock_schemas = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "SCHEMA_OWNER": "SYSADMIN",
                "IS_TRANSIENT": "NO",
                "IS_MANAGED_ACCESS": "NO",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "RETENTION_TIME": 1,
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_schemas

        result = self.metadata.get_schemas(database_name="TEST_DB")

        self.assertEqual(result, mock_schemas)
        call_args = self.mock_connection.execute_query_dict.call_args
        self.assertEqual(call_args[0][1], ("TEST_DB",))

    # =========================================================================
    # Table Metadata Tests
    # =========================================================================
    # NOTE: Table, view, and column tests have been moved to test_table.py
    # Use SnowflakeTable class for table-level metadata tests
    # =========================================================================

    # =========================================================================
    # Function and Procedure Tests
    # =========================================================================

    def test_get_functions(self):
        """Test get_functions method."""
        mock_functions = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "FUNCTION_NAME": "ADD_NUMBERS",
                "FUNCTION_LANGUAGE": "SQL",
                "FUNCTION_DEFINITION": "RETURN A + B",
                "RETURN_TYPE": "NUMBER",
                "ARGUMENT_SIGNATURE": "(A NUMBER, B NUMBER)",
                "IS_SECURE": "NO",
                "IS_EXTERNAL": "NO",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_functions

        result = self.metadata.get_functions()

        self.assertEqual(result, mock_functions)

    def test_get_procedures(self):
        """Test get_procedures method."""
        mock_procedures = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "PROCEDURE_NAME": "UPDATE_CUSTOMER",
                "PROCEDURE_LANGUAGE": "SQL",
                "PROCEDURE_DEFINITION": "UPDATE CUSTOMERS SET...",
                "ARGUMENT_SIGNATURE": "(CUSTOMER_ID NUMBER)",
                "IS_SECURE": "NO",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_procedures

        result = self.metadata.get_procedures()

        self.assertEqual(result, mock_procedures)

    # =========================================================================
    # Sequence Tests
    # =========================================================================

    def test_get_sequences(self):
        """Test get_sequences method."""
        mock_sequences = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "SEQUENCE_NAME": "CUSTOMER_ID_SEQ",
                "DATA_TYPE": "NUMBER",
                "NUMERIC_PRECISION": 38,
                "NUMERIC_SCALE": 0,
                "START_VALUE": 1,
                "MINIMUM_VALUE": 1,
                "MAXIMUM_VALUE": 9999999999,
                "INCREMENT": 1,
                "CYCLE_OPTION": "NO",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_sequences

        result = self.metadata.get_sequences()

        self.assertEqual(result, mock_sequences)

    # =========================================================================
    # Stage Tests
    # =========================================================================

    def test_get_stages(self):
        """Test get_stages method."""
        mock_stages = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "STAGE_NAME": "MY_STAGE",
                "STAGE_URL": "s3://mybucket/path/",
                "STAGE_REGION": "us-east-1",
                "STAGE_TYPE": "EXTERNAL",
                "STAGE_OWNER": "SYSADMIN",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_stages

        result = self.metadata.get_stages()

        self.assertEqual(result, mock_stages)

    # =========================================================================
    # File Format Tests
    # =========================================================================

    def test_get_file_formats(self):
        """Test get_file_formats method."""
        mock_file_formats = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "FILE_FORMAT_NAME": "MY_CSV_FORMAT",
                "FILE_FORMAT_TYPE": "CSV",
                "FILE_FORMAT_OWNER": "SYSADMIN",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_file_formats

        result = self.metadata.get_file_formats()

        self.assertEqual(result, mock_file_formats)

    # =========================================================================
    # Pipe Tests
    # =========================================================================

    def test_get_pipes(self):
        """Test get_pipes method."""
        mock_pipes = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "PIPE_NAME": "MY_PIPE",
                "PIPE_OWNER": "SYSADMIN",
                "DEFINITION": "COPY INTO CUSTOMERS FROM @MY_STAGE",
                "NOTIFICATION_CHANNEL_NAME": "arn:aws:sns:...",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_pipes

        result = self.metadata.get_pipes()

        self.assertEqual(result, mock_pipes)

    # =========================================================================
    # Task and Stream Tests
    # =========================================================================

    def test_get_tasks(self):
        """Test get_tasks method."""
        mock_tasks = [
            {
                "database_name": "TEST_DB",
                "schema_name": "PUBLIC",
                "task_name": "MY_TASK",
                "schedule": "USING CRON 0 0 * * * UTC",
                "state": "STARTED",
                "definition": "INSERT INTO TABLE...",
                "warehouse": "COMPUTE_WH",
                "condition_text": None,
                "allow_overlapping_execution": "NO",
                "created_on": "2023-01-01",
                "last_committed_on": "2023-01-02",
                "comment": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_tasks

        result = self.metadata.get_tasks()

        self.assertEqual(result, mock_tasks)

    def test_get_streams(self):
        """Test get_streams method."""
        mock_streams = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "STREAM_NAME": "MY_STREAM",
                "SOURCE_TYPE": "Table",
                "BASE_TABLE_NAME": "CUSTOMERS",
                "OWNER": "SYSADMIN",
                "COMMENT": "",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_streams

        result = self.metadata.get_streams()

        self.assertEqual(result, mock_streams)

    # =========================================================================
    # Comprehensive Metadata Tests
    # =========================================================================

    def test_get_all_database_metadata(self):
        """Test get_all_database_metadata method."""
        # Mock all the individual methods
        self.metadata.get_databases = Mock(return_value=[{"DATABASE_NAME": "TEST_DB"}])
        self.metadata.get_database_info = Mock(
            return_value={"DATABASE_NAME": "TEST_DB"}
        )
        self.metadata.get_schemas = Mock(return_value=[{"SCHEMA_NAME": "PUBLIC"}])
        self.metadata.get_functions = Mock(return_value=[{"FUNCTION_NAME": "ADD"}])
        self.metadata.get_procedures = Mock(return_value=[{"PROCEDURE_NAME": "UPDATE"}])
        self.metadata.get_sequences = Mock(return_value=[{"SEQUENCE_NAME": "SEQ1"}])
        self.metadata.get_stages = Mock(return_value=[{"STAGE_NAME": "STAGE1"}])
        self.metadata.get_file_formats = Mock(
            return_value=[{"FILE_FORMAT_NAME": "CSV1"}]
        )
        self.metadata.get_pipes = Mock(return_value=[{"PIPE_NAME": "PIPE1"}])
        self.metadata.get_tasks = Mock(return_value=[{"task_name": "TASK1"}])
        self.metadata.get_streams = Mock(return_value=[{"STREAM_NAME": "STREAM1"}])

        result = self.metadata.get_all_database_metadata()

        # Check that all methods were called
        self.metadata.get_databases.assert_called_once()
        self.metadata.get_schemas.assert_called_once()
        self.metadata.get_functions.assert_called_once()
        self.metadata.get_procedures.assert_called_once()
        self.metadata.get_sequences.assert_called_once()
        self.metadata.get_stages.assert_called_once()
        self.metadata.get_file_formats.assert_called_once()
        self.metadata.get_pipes.assert_called_once()
        self.metadata.get_tasks.assert_called_once()
        self.metadata.get_streams.assert_called_once()

        # Check result structure
        self.assertIn("databases", result)
        self.assertIn("schemas", result)
        self.assertIn("functions", result)
        self.assertIn("procedures", result)
        self.assertIn("sequences", result)
        self.assertIn("stages", result)
        self.assertIn("file_formats", result)
        self.assertIn("pipes", result)
        self.assertIn("tasks", result)
        self.assertIn("streams", result)
        self.assertIn("summary", result)

        # Check summary counts
        self.assertEqual(result["summary"]["database_count"], 1)
        self.assertEqual(result["summary"]["schema_count"], 1)

    def test_get_all_database_metadata_with_database_filter(self):
        """Test get_all_database_metadata with database filter."""
        # Mock all the individual methods
        self.metadata.get_databases = Mock(return_value=[{"DATABASE_NAME": "TEST_DB"}])
        self.metadata.get_database_info = Mock(
            return_value={"DATABASE_NAME": "TEST_DB"}
        )
        self.metadata.get_schemas = Mock(return_value=[{"SCHEMA_NAME": "PUBLIC"}])
        self.metadata.get_functions = Mock(return_value=[])
        self.metadata.get_procedures = Mock(return_value=[])
        self.metadata.get_sequences = Mock(return_value=[])
        self.metadata.get_stages = Mock(return_value=[])
        self.metadata.get_file_formats = Mock(return_value=[])
        self.metadata.get_pipes = Mock(return_value=[])
        self.metadata.get_tasks = Mock(return_value=[])
        self.metadata.get_streams = Mock(return_value=[])

        self.metadata.get_all_database_metadata(database_name="TEST_DB")

        # Check that database_info was called instead of get_databases
        self.metadata.get_database_info.assert_called_once_with("TEST_DB")
        # Check that filters were passed to other methods
        self.metadata.get_schemas.assert_called_once_with("TEST_DB")

    # =========================================================================
    # Error Handling Tests
    # =========================================================================

    def test_get_databases_error(self):
        """Test error handling in get_databases."""
        self.mock_connection.execute_query_dict.side_effect = Exception(
            "Database error"
        )

        with self.assertRaises(Exception) as context:
            self.metadata.get_databases()

        self.assertIn("Database error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
