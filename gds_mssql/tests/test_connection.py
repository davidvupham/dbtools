"""
Test suite for Microsoft SQL Server connection implementation.
"""

import unittest
from unittest.mock import MagicMock, patch

from gds_database import ConfigurationError, ConnectionError

# Mock pyodbc to avoid import errors in test environment
mock_pyodbc = MagicMock()
mock_pyodbc.Error = Exception

with patch.dict("sys.modules", {"pyodbc": mock_pyodbc}):
    from gds_mssql import MSSQLConnection


class TestMSSQLConnection(unittest.TestCase):
    """Test MSSQL connection implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "server": "localhost",
            "port": 1433,
            "database": "testdb",
            "user": "testuser",
            "password": "testpass",
            "driver": "ODBC Driver 18 for SQL Server",
            "connection_timeout": 30,
        }
        mock_pyodbc.reset_mock()
        mock_pyodbc.connect.side_effect = None

    def test_initialization_with_parameters(self):
        """Test initialization with individual parameters."""
        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )

        self.assertEqual(conn.config["server"], "localhost")
        self.assertEqual(conn.config["port"], 1433)
        self.assertEqual(conn.config["database"], "testdb")
        self.assertEqual(conn.config["user"], "testuser")
        self.assertEqual(conn.config["password"], "testpass")
        self.assertEqual(conn.config["authentication"], None)

    def test_initialization_with_kerberos(self):
        """Test initialization with Kerberos authentication."""
        conn = MSSQLConnection(
            server="localhost", database="testdb", authentication="kerberos"
        )

        self.assertEqual(conn.config["server"], "localhost")
        self.assertEqual(conn.config["database"], "testdb")
        self.assertEqual(conn.config["authentication"], "kerberos")
        self.assertNotIn("user", conn.config)
        self.assertNotIn("password", conn.config)

    def test_initialization_with_config_dict(self):
        """Test initialization with configuration dictionary."""
        conn = MSSQLConnection(config=self.config)

        self.assertEqual(conn.config["server"], "localhost")
        self.assertEqual(conn.config["database"], "testdb")
        self.assertEqual(conn.config["user"], "testuser")

    def test_config_validation_missing_required_fields(self):
        """Test configuration validation with missing required fields."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MSSQLConnection()
            conn.validate_config()

        self.assertIn("Missing required configuration fields", str(cm.exception))

    def test_config_validation_kerberos_with_user_password(self):
        """Test configuration validation with Kerberos and user/password."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MSSQLConnection(
                server="localhost",
                database="testdb",
                authentication="kerberos",
                user="testuser",
            )
            conn.validate_config()

        self.assertIn(
            "User/password should not be provided with Kerberos", str(cm.exception)
        )

    def test_config_validation_username_password_missing_user(self):
        """Test configuration validation with username/password missing user."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MSSQLConnection(
                server="localhost", database="testdb", password="testpass"
            )
            conn.validate_config()

        self.assertIn(
            "Username is required for username/password authentication",
            str(cm.exception),
        )

    def test_connection_string_building_username_password(self):
        """Test building connection string for username/password auth."""
        conn = MSSQLConnection(
            server="localhost",
            port=1433,
            database="testdb",
            user="testuser",
            password="testpass",
            driver="ODBC Driver 18 for SQL Server",
        )

        conn_str = conn._build_connection_string()
        self.assertIn("DRIVER={ODBC Driver 18 for SQL Server}", conn_str)
        self.assertIn("SERVER=localhost", conn_str)
        self.assertIn("DATABASE=testdb", conn_str)
        self.assertIn("UID=testuser", conn_str)
        self.assertIn("PWD=testpass", conn_str)
        self.assertNotIn("Trusted_Connection", conn_str)

    def test_connection_string_building_kerberos(self):
        """Test building connection string for Kerberos auth."""
        conn = MSSQLConnection(
            server="myserver.domain.com", database="testdb", authentication="kerberos"
        )

        conn_str = conn._build_connection_string()
        self.assertIn("SERVER=myserver.domain.com", conn_str)
        self.assertIn("DATABASE=testdb", conn_str)
        self.assertIn("Trusted_Connection=yes", conn_str)
        self.assertNotIn("UID=", conn_str)
        self.assertNotIn("PWD=", conn_str)

    @patch("gds_mssql.connection.pyodbc.connect")
    def test_connect_success(self, mock_connect):
        """Test successful connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )

        result = conn.connect()

        self.assertEqual(result, mock_connection)
        mock_connect.assert_called_once()
        self.assertEqual(conn.connection, mock_connection)

    @patch("gds_mssql.connection.pyodbc.connect")
    def test_connect_failure(self, mock_connect):
        """Test connection failure."""
        mock_connect.side_effect = mock_pyodbc.Error("Connection failed")

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )

        with self.assertRaises(ConnectionError) as cm:
            conn.connect()

        self.assertIn("Failed to connect to SQL Server database", str(cm.exception))

    def test_disconnect(self):
        """Test disconnecting from database."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        conn._cursor = mock_cursor

        conn.disconnect()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        self.assertIsNone(conn.connection)
        self.assertIsNone(conn._cursor)

    def test_is_connected_true(self):
        """Test is_connected returns True when connected."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        result = conn.is_connected()

        self.assertTrue(result)
        mock_cursor.execute.assert_called_with("SELECT 1")

    def test_is_connected_false(self):
        """Test is_connected returns False when not connected."""
        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )

        result = conn.is_connected()

        self.assertFalse(result)

    def test_get_connection_info(self):
        """Test getting connection information."""
        conn = MSSQLConnection(
            server="localhost",
            database="testdb",
            user="testuser",
            authentication="kerberos",
        )

        info = conn.get_connection_info()

        self.assertEqual(info["database_type"], "mssql")
        self.assertEqual(info["server"], "localhost")
        self.assertEqual(info["database"], "testdb")
        self.assertEqual(info["user"], "testuser")
        self.assertEqual(info["authentication"], "kerberos")
        self.assertFalse(info["connected"])

    def test_execute_query_select(self):
        """Test executing a SELECT query."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "test")]

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        result = conn.execute_query("SELECT * FROM test_table")

        self.assertEqual(result, [(1, "test")])
        mock_cursor.execute.assert_called_with("SELECT * FROM test_table", ())
        mock_cursor.close.assert_called_once()

    def test_execute_query_insert(self):
        """Test executing an INSERT query."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 1

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        result = conn.execute_query("INSERT INTO test_table VALUES (1, 'test')")

        self.assertEqual(result, [{"affected_rows": 1}])
        mock_cursor.execute.assert_called_with(
            "INSERT INTO test_table VALUES (1, 'test')", ()
        )
        mock_cursor.close.assert_called_once()

    def test_execute_query_dict(self):
        """Test executing query with dict results."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "test"), (2, "test2")]

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        result = conn.execute_query_dict("SELECT id, name FROM test_table")

        expected = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
        self.assertEqual(result, expected)

    def test_commit_transaction(self):
        """Test committing a transaction."""
        mock_connection = MagicMock()

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection

        conn.commit()

        mock_connection.commit.assert_called_once()

    def test_rollback_transaction(self):
        """Test rolling back a transaction."""
        mock_connection = MagicMock()

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection

        conn.rollback()

        mock_connection.rollback.assert_called_once()

    def test_get_table_names(self):
        """Test getting table names."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("TABLE_NAME",)]
        mock_cursor.fetchall.return_value = [("users",), ("products",)]

        conn = MSSQLConnection(
            server="localhost", database="testdb", user="testuser", password="testpass"
        )
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        result = conn.get_table_names("dbo")

        self.assertEqual(result, ["users", "products"])
        mock_cursor.execute.assert_called_with(
            "\n        SELECT TABLE_NAME\n        FROM INFORMATION_SCHEMA.TABLES\n        WHERE TABLE_SCHEMA = ? AND TABLE_TYPE = 'BASE TABLE'\n        ORDER BY TABLE_NAME\n        ",
            ("dbo",),
        )

    def test_context_manager(self):
        """Test using as context manager."""
        mock_connection = MagicMock()

        with patch("gds_mssql.connection.pyodbc.connect", return_value=mock_connection):
            with MSSQLConnection(
                server="localhost",
                database="testdb",
                user="testuser",
                password="testpass",
            ) as conn:
                self.assertEqual(conn.connection, mock_connection)

            mock_connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
