"""
Unit tests for the SnowflakeTable class.
"""

import unittest
from unittest.mock import Mock
from gds_snowflake.table import SnowflakeTable


class TestSnowflakeTable(unittest.TestCase):
    """Test cases for SnowflakeTable class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.table_metadata = SnowflakeTable(self.mock_connection)

    def test_init(self):
        """Test SnowflakeTable initialization."""
        self.assertEqual(self.table_metadata.connection, self.mock_connection)

    # =========================================================================
    # Table Metadata Tests
    # =========================================================================

    def test_get_tables(self):
        """Test get_tables method."""
        mock_tables = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMERS",
                "TABLE_TYPE": "BASE TABLE",
                "IS_TRANSIENT": "NO",
                "CLUSTERING_KEY": None,
                "ROW_COUNT": 1000,
                "BYTES": 50000,
                "RETENTION_TIME": 1,
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "AUTO_CLUSTERING_ON": "NO",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_tables

        result = self.table_metadata.get_tables()

        self.assertEqual(result, mock_tables)
        self.mock_connection.execute_query_dict.assert_called_once()

    def test_get_tables_with_views(self):
        """Test get_tables with include_views=True."""
        mock_tables = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMERS",
                "TABLE_TYPE": "BASE TABLE",
            },
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMER_VIEW",
                "TABLE_TYPE": "VIEW",
            },
        ]
        self.mock_connection.execute_query_dict.return_value = mock_tables

        result = self.table_metadata.get_tables(include_views=True)

        self.assertEqual(result, mock_tables)
        call_args = self.mock_connection.execute_query_dict.call_args
        query = call_args[0][0]
        self.assertIn("'VIEW'", query)

    def test_get_tables_filtered(self):
        """Test get_tables with filters."""
        mock_tables = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMERS",
                "TABLE_TYPE": "BASE TABLE",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_tables

        result = self.table_metadata.get_tables(
            database_name="TEST_DB", schema_name="PUBLIC"
        )

        self.assertEqual(result, mock_tables)

    def test_get_table_info(self):
        """Test get_table_info method."""
        mock_table = {
            "DATABASE_NAME": "TEST_DB",
            "SCHEMA_NAME": "PUBLIC",
            "TABLE_NAME": "CUSTOMERS",
            "TABLE_TYPE": "BASE TABLE",
            "IS_TRANSIENT": "NO",
            "CLUSTERING_KEY": None,
            "ROW_COUNT": 1000,
            "BYTES": 50000,
            "RETENTION_TIME": 1,
            "CREATED": "2023-01-01",
            "LAST_ALTERED": "2023-01-02",
            "AUTO_CLUSTERING_ON": "NO",
            "COMMENT": "",
        }
        self.mock_connection.execute_query_dict.return_value = [mock_table]

        result = self.table_metadata.get_table_info("CUSTOMERS")

        self.assertEqual(result, mock_table)

    def test_get_table_info_not_found(self):
        """Test get_table_info when table doesn't exist."""
        self.mock_connection.execute_query_dict.return_value = []

        result = self.table_metadata.get_table_info("NONEXISTENT_TABLE")

        self.assertIsNone(result)

    # =========================================================================
    # View Metadata Tests
    # =========================================================================

    def test_get_views(self):
        """Test get_views method."""
        mock_views = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "VIEW_NAME": "CUSTOMER_VIEW",
                "VIEW_DEFINITION": "SELECT * FROM CUSTOMERS",
                "IS_SECURE": "NO",
                "IS_MATERIALIZED": "NO",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_views

        result = self.table_metadata.get_views()

        self.assertEqual(result, mock_views)
        self.mock_connection.execute_query_dict.assert_called_once()

    def test_get_views_filtered(self):
        """Test get_views with filters."""
        mock_views = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "VIEW_NAME": "CUSTOMER_VIEW",
                "VIEW_DEFINITION": "SELECT * FROM CUSTOMERS",
                "IS_SECURE": "NO",
                "IS_MATERIALIZED": "NO",
                "CREATED": "2023-01-01",
                "LAST_ALTERED": "2023-01-02",
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_views

        result = self.table_metadata.get_views(
            database_name="TEST_DB", schema_name="PUBLIC"
        )

        self.assertEqual(result, mock_views)

    # =========================================================================
    # Column Metadata Tests
    # =========================================================================

    def test_get_columns(self):
        """Test get_columns method."""
        mock_columns = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMERS",
                "COLUMN_NAME": "ID",
                "ORDINAL_POSITION": 1,
                "COLUMN_DEFAULT": None,
                "IS_NULLABLE": "NO",
                "DATA_TYPE": "NUMBER",
                "CHARACTER_MAXIMUM_LENGTH": None,
                "NUMERIC_PRECISION": 38,
                "NUMERIC_SCALE": 0,
                "IS_IDENTITY": "YES",
                "IDENTITY_START": 1,
                "IDENTITY_INCREMENT": 1,
                "COMMENT": "",
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_columns

        result = self.table_metadata.get_columns()

        self.assertEqual(result, mock_columns)
        self.mock_connection.execute_query_dict.assert_called_once()

    def test_get_columns_for_table(self):
        """Test get_columns for specific table."""
        mock_columns = [
            {
                "DATABASE_NAME": "TEST_DB",
                "SCHEMA_NAME": "PUBLIC",
                "TABLE_NAME": "CUSTOMERS",
                "COLUMN_NAME": "ID",
                "ORDINAL_POSITION": 1,
            }
        ]
        self.mock_connection.execute_query_dict.return_value = mock_columns

        result = self.table_metadata.get_columns(table_name="CUSTOMERS")

        self.assertEqual(result, mock_columns)

    # =========================================================================
    # Comprehensive Metadata Tests
    # =========================================================================

    def test_get_all_table_metadata(self):
        """Test get_all_table_metadata method."""
        # Mock all the individual methods
        self.table_metadata.get_tables = Mock(
            return_value=[{"TABLE_NAME": "CUSTOMERS"}]
        )
        self.table_metadata.get_views = Mock(
            return_value=[{"VIEW_NAME": "CUSTOMER_VIEW"}]
        )
        self.table_metadata.get_columns = Mock(return_value=[{"COLUMN_NAME": "ID"}])

        result = self.table_metadata.get_all_table_metadata()

        # Check that all methods were called
        self.table_metadata.get_tables.assert_called_once()
        self.table_metadata.get_views.assert_called_once()
        self.table_metadata.get_columns.assert_called_once()

        # Check result structure
        self.assertIn("tables", result)
        self.assertIn("views", result)
        self.assertIn("columns", result)
        self.assertIn("summary", result)

        # Check summary counts
        self.assertEqual(result["summary"]["table_count"], 1)
        self.assertEqual(result["summary"]["view_count"], 1)
        self.assertEqual(result["summary"]["column_count"], 1)

    def test_get_all_table_metadata_with_filters(self):
        """Test get_all_table_metadata with filters."""
        # Mock all the individual methods
        self.table_metadata.get_tables = Mock(
            return_value=[{"TABLE_NAME": "CUSTOMERS"}]
        )
        self.table_metadata.get_views = Mock(return_value=[])
        self.table_metadata.get_columns = Mock(return_value=[])

        result = self.table_metadata.get_all_table_metadata(
            database_name="TEST_DB", schema_name="PUBLIC"
        )

        # Check that filters were passed
        self.table_metadata.get_tables.assert_called_once_with(
            "TEST_DB", "PUBLIC", include_views=False
        )
        self.table_metadata.get_views.assert_called_once_with("TEST_DB", "PUBLIC")
        self.table_metadata.get_columns.assert_called_once_with(
            None, "TEST_DB", "PUBLIC"
        )

    # =========================================================================
    # Error Handling Tests
    # =========================================================================

    def test_get_tables_error(self):
        """Test error handling in get_tables."""
        self.mock_connection.execute_query_dict.side_effect = Exception("Query error")

        with self.assertRaises(Exception) as context:
            self.table_metadata.get_tables()

        self.assertIn("Query error", str(context.exception))

    def test_get_views_error(self):
        """Test error handling in get_views."""
        self.mock_connection.execute_query_dict.side_effect = Exception("Query error")

        with self.assertRaises(Exception) as context:
            self.table_metadata.get_views()

        self.assertIn("Query error", str(context.exception))

    def test_get_columns_error(self):
        """Test error handling in get_columns."""
        self.mock_connection.execute_query_dict.side_effect = Exception("Query error")

        with self.assertRaises(Exception) as context:
            self.table_metadata.get_columns()

        self.assertIn("Query error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
