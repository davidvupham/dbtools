"""
Test suite for MongoDB connection implementation.
"""

import unittest
from unittest.mock import MagicMock, patch

from gds_database import ConfigurationError, ConnectionError

# Mock pymongo to avoid import errors in test environment
mock_pymongo = MagicMock()
mock_pymongo.MongoClient = MagicMock
mock_pymongo_errors = MagicMock()
mock_pymongo_errors.ConnectionFailure = Exception
mock_pymongo_errors.OperationFailure = Exception
mock_pymongo_errors.ServerSelectionTimeoutError = Exception

with patch.dict(
    "sys.modules",
    {"pymongo": mock_pymongo, "pymongo.errors": mock_pymongo_errors},
):
    from gds_mongodb import MongoDBConnection


class TestMongoDBConnection(unittest.TestCase):
    """Test MongoDB connection implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "host": "localhost",
            "port": 27017,
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
            "auth_source": "admin",
            "server_selection_timeout_ms": 5000,
        }
        mock_pymongo.reset_mock()
        mock_pymongo.MongoClient.side_effect = None

    def test_initialization_with_parameters(self):
        """Test initialization with individual parameters."""
        conn = MongoDBConnection(
            host="localhost",
            port=27017,
            database="testdb",
            username="testuser",
            password="testpass",
        )

        self.assertEqual(conn.config["host"], "localhost")
        self.assertEqual(conn.config["port"], 27017)
        self.assertEqual(conn.config["database"], "testdb")
        self.assertEqual(conn.config["username"], "testuser")
        self.assertEqual(conn.config["password"], "testpass")
        self.assertEqual(conn.config["auth_source"], "admin")

    def test_initialization_with_connection_string(self):
        """Test initialization with connection string."""
        conn = MongoDBConnection(
            connection_string="mongodb://user:pass@localhost:27017/",
            database="testdb",
        )

        self.assertEqual(
            conn.config["connection_string"],
            "mongodb://user:pass@localhost:27017/",
        )
        self.assertEqual(conn.config["database"], "testdb")

    def test_initialization_with_config_dict(self):
        """Test initialization with configuration dictionary."""
        conn = MongoDBConnection(config=self.config)

        self.assertEqual(conn.config["host"], "localhost")
        self.assertEqual(conn.config["database"], "testdb")
        self.assertEqual(conn.config["username"], "testuser")

    def test_config_validation_missing_required_fields(self):
        """Test configuration validation with missing required fields."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection()
            conn.validate_config()

        self.assertIn("Missing required configuration fields", str(cm.exception))

    def test_config_validation_username_without_password(self):
        """Test configuration validation with username but no password."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(host="localhost", database="testdb", username="testuser")
            conn.validate_config()

        self.assertIn("Password is required when username is provided", str(cm.exception))

    def test_config_validation_connection_string_without_database(self):
        """Test configuration validation with connection string but no database."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(connection_string="mongodb://localhost:27017/")
            conn.validate_config()

        self.assertIn(
            "Database name is required even when using connection string",
            str(cm.exception),
        )

    def test_config_validation_invalid_port(self):
        """Test configuration validation with invalid port."""
        conn = MongoDBConnection(host="localhost", database="testdb", port="invalid")

        with self.assertRaises(ConfigurationError) as cm:
            conn.validate_config()

        self.assertIn("Invalid port number", str(cm.exception))

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        conn = MongoDBConnection(host="localhost", database="testdb", username="user", password="pass")

        result = conn.validate_config()
        self.assertTrue(result)

    def test_config_validation_scram_sha256_requires_password(self):
        """Test SCRAM-SHA-256 requires username and password."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(
                host="localhost",
                database="testdb",
                username="user",
                auth_mechanism="SCRAM-SHA-256",
            )
            conn.validate_config()

        self.assertIn("SCRAM-SHA-256 requires password", str(cm.exception))

    def test_config_validation_gssapi_requires_username(self):
        """Test GSSAPI (Kerberos) requires username."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(
                host="localhost",
                database="testdb",
                auth_mechanism="GSSAPI",
            )
            conn.validate_config()

        self.assertIn("GSSAPI (Kerberos) requires username", str(cm.exception))

    def test_config_validation_x509_requires_tls(self):
        """Test MONGODB-X509 requires TLS."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(
                host="localhost",
                database="testdb",
                username="CN=user",
                auth_mechanism="MONGODB-X509",
            )
            conn.validate_config()

        self.assertIn("MONGODB-X509 requires TLS", str(cm.exception))

    def test_config_validation_invalid_auth_mechanism(self):
        """Test invalid auth mechanism raises error."""
        with self.assertRaises(ConfigurationError) as cm:
            conn = MongoDBConnection(
                host="localhost",
                database="testdb",
                username="user",
                password="pass",
                auth_mechanism="INVALID-MECHANISM",
            )
            conn.validate_config()

        self.assertIn("Unsupported auth_mechanism", str(cm.exception))

    def test_build_connection_string_basic(self):
        """Test building basic connection string."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn_str = conn._build_connection_string()

        self.assertEqual(conn_str, "mongodb://localhost:27017/")

    def test_build_connection_string_with_auth(self):
        """Test building connection string with authentication."""
        conn = MongoDBConnection(
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
        )
        conn_str = conn._build_connection_string()

        self.assertIn("user:pass@", conn_str)
        self.assertIn("localhost:27017", conn_str)

    def test_build_connection_string_with_options(self):
        """Test building connection string with options."""
        conn = MongoDBConnection(
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
            auth_source="admin",
            replica_set="rs0",
            tls=True,
        )
        conn_str = conn._build_connection_string()

        self.assertIn("authSource=admin", conn_str)
        self.assertIn("replicaSet=rs0", conn_str)
        self.assertIn("tls=true", conn_str)

    def test_build_connection_string_with_scram(self):
        """Test building connection string with SCRAM-SHA-256."""
        conn = MongoDBConnection(
            host="localhost",
            database="testdb",
            username="user",
            password="pass",
            auth_mechanism="SCRAM-SHA-256",
        )
        conn_str = conn._build_connection_string()

        self.assertIn("user:pass@", conn_str)
        self.assertIn("authMechanism=SCRAM-SHA-256", conn_str)

    def test_build_connection_string_with_gssapi(self):
        """Test building connection string with GSSAPI (Kerberos)."""
        conn = MongoDBConnection(
            host="localhost",
            database="testdb",
            username="user@REALM",
            auth_mechanism="GSSAPI",
            auth_source="$external",
        )
        conn_str = conn._build_connection_string()

        self.assertIn("authMechanism=GSSAPI", conn_str)
        self.assertIn("authSource=%24external", conn_str)

    def test_build_connection_string_with_x509(self):
        """Test building connection string with X.509."""
        conn = MongoDBConnection(
            host="localhost",
            database="testdb",
            username="CN=user",
            auth_mechanism="MONGODB-X509",
            tls=True,
        )
        conn_str = conn._build_connection_string()

        self.assertIn("authMechanism=MONGODB-X509", conn_str)
        self.assertIn("tls=true", conn_str)
        # X.509 includes username but not password
        self.assertIn("CN%3Duser@", conn_str)
        self.assertNotIn(":", conn_str.split("@")[0].split("//")[1])

    def test_build_connection_params(self):
        """Test building connection parameters."""
        config = {
            "host": "localhost",
            "database": "testdb",
            "server_selection_timeout_ms": 5000,
            "maxPoolSize": 50,
            "connectTimeoutMS": 10000,
        }
        conn = MongoDBConnection(config=config)
        params = conn._build_connection_params()

        self.assertEqual(params["serverSelectionTimeoutMS"], 5000)
        self.assertEqual(params["maxPoolSize"], 50)
        self.assertEqual(params["connectTimeoutMS"], 10000)

    def test_get_connection_info(self):
        """Test getting connection information."""
        conn = MongoDBConnection(
            host="localhost",
            port=27017,
            database="testdb",
            username="testuser",
        )

        info = conn.get_connection_info()

        self.assertEqual(info["database_type"], "mongodb")
        self.assertEqual(info["host"], "localhost")
        self.assertEqual(info["port"], 27017)
        self.assertEqual(info["database"], "testdb")
        self.assertEqual(info["username"], "testuser")
        self.assertFalse(info["connected"])

    def test_context_manager_entry_exit(self):
        """Test context manager entry and exit."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = None

        with patch.object(MongoDBConnection, "connect", return_value=mock_client):
            with patch.object(MongoDBConnection, "disconnect") as mock_disconnect:
                with MongoDBConnection(host="localhost", database="testdb") as conn:
                    self.assertIsNotNone(conn)

                mock_disconnect.assert_called_once()

    def test_is_connected_false_when_no_client(self):
        """Test is_connected returns False when no client."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        self.assertFalse(conn.is_connected())

    def test_is_connected_false_when_ping_fails(self):
        """Test is_connected returns False when ping fails."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = Exception("Connection lost")
        conn.client = mock_client

        self.assertFalse(conn.is_connected())

    def test_execute_query_not_connected(self):
        """Test execute_query raises error when not connected."""
        conn = MongoDBConnection(host="localhost", database="testdb")

        with self.assertRaises(ConnectionError) as cm:
            conn.execute_query("users", {})

        self.assertIn("Not connected", str(cm.exception))

    def test_insert_one_not_connected(self):
        """Test insert_one raises error when not connected."""
        conn = MongoDBConnection(host="localhost", database="testdb")

        with self.assertRaises(ConnectionError) as cm:
            conn.insert_one("users", {"name": "test"})

        self.assertIn("Not connected", str(cm.exception))

    def test_update_one_not_connected(self):
        """Test update_one raises error when not connected."""
        conn = MongoDBConnection(host="localhost", database="testdb")

        with self.assertRaises(ConnectionError) as cm:
            conn.update_one("users", {"_id": 1}, {"$set": {"name": "test"}})

        self.assertIn("Not connected", str(cm.exception))

    def test_delete_one_not_connected(self):
        """Test delete_one raises error when not connected."""
        conn = MongoDBConnection(host="localhost", database="testdb")

        with self.assertRaises(ConnectionError) as cm:
            conn.delete_one("users", {"_id": 1})

        self.assertIn("Not connected", str(cm.exception))

    def test_get_collection_names_not_connected(self):
        """Test get_collection_names raises error when not connected."""
        conn = MongoDBConnection(host="localhost", database="testdb")

        with self.assertRaises(ConnectionError) as cm:
            conn.get_collection_names()

        self.assertIn("Not connected", str(cm.exception))

    def test_resource_manager_interface(self):
        """Test ResourceManager interface methods."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = None

        conn = MongoDBConnection(host="localhost", database="testdb")

        with patch.object(MongoDBConnection, "connect", return_value=mock_client):
            with patch.object(MongoDBConnection, "disconnect"):
                # Test initialize
                conn.initialize()
                self.assertIsNotNone(conn.client)

                # Test cleanup
                conn.cleanup()


class TestMongoDBConnectionIntegration(unittest.TestCase):
    """Integration tests with mocked pymongo operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()

        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_client.admin.command.return_value = {"ok": 1}

    def test_execute_query_with_results(self):
        """Test execute_query with mocked results."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn.client = self.mock_client
        conn._db = self.mock_db

        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([{"name": "user1"}, {"name": "user2"}])
        self.mock_collection.find.return_value = mock_cursor

        results = conn.execute_query("users", {"age": {"$gte": 18}})

        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(results), 2)

    def test_insert_one_success(self):
        """Test successful insert_one operation."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn.client = self.mock_client
        conn._db = self.mock_db

        mock_result = MagicMock()
        mock_result.inserted_id = "12345"
        self.mock_collection.insert_one.return_value = mock_result

        result = conn.insert_one("users", {"name": "test"})

        self.assertEqual(result["inserted_id"], "12345")
        self.mock_collection.insert_one.assert_called_once_with({"name": "test"})

    def test_update_one_success(self):
        """Test successful update_one operation."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn.client = self.mock_client
        conn._db = self.mock_db

        mock_result = MagicMock()
        mock_result.matched_count = 1
        mock_result.modified_count = 1
        mock_result.upserted_id = None
        self.mock_collection.update_one.return_value = mock_result

        result = conn.update_one("users", {"_id": 1}, {"$set": {"name": "updated"}})

        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["modified_count"], 1)

    def test_delete_one_success(self):
        """Test successful delete_one operation."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn.client = self.mock_client
        conn._db = self.mock_db

        mock_result = MagicMock()
        mock_result.deleted_count = 1
        self.mock_collection.delete_one.return_value = mock_result

        result = conn.delete_one("users", {"_id": 1})

        self.assertEqual(result["deleted_count"], 1)

    def test_get_collection_names(self):
        """Test getting collection names."""
        conn = MongoDBConnection(host="localhost", database="testdb")
        conn.client = self.mock_client
        conn._db = self.mock_db

        self.mock_db.list_collection_names.return_value = [
            "users",
            "posts",
            "comments",
        ]

        collections = conn.get_collection_names()

        self.assertEqual(len(collections), 3)
        self.assertIn("users", collections)


if __name__ == "__main__":
    unittest.main()
