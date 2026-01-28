"""Tests for MongoDB connection configuration module."""

from __future__ import annotations

import pytest
from gds_database import ConfigurationError
from gds_mongodb.connection_config import MongoDBConnectionConfig


class TestMongoDBConnectionConfig:
    """Tests for MongoDBConnectionConfig class."""

    def test_init_with_required_params(self):
        """Initialize with host and database."""
        config = MongoDBConnectionConfig(host="localhost", database="testdb")
        assert config.get_host() == "localhost"
        assert config.get_port() == 27017
        assert config.get_database() == "testdb"
        assert config.get_auth_source() == "admin"

    def test_init_with_all_params(self):
        """Initialize with all connection parameters."""
        config = MongoDBConnectionConfig(
            host="mongo.example.com",
            port=27018,
            database="mydb",
            username="user",
            password="pass",
            auth_source="authdb",
            auth_mechanism="SCRAM-SHA-256",
            replica_set="rs0",
            tls=True,
        )
        assert config.get_host() == "mongo.example.com"
        assert config.get_port() == 27018
        assert config.get_database() == "mydb"
        assert config.get_username() == "user"
        assert config.get_auth_mechanism() == "SCRAM-SHA-256"
        assert config.get_auth_source() == "authdb"
        assert config.is_tls_enabled() is True

    def test_init_with_config_dict(self):
        """Initialize from config dictionary."""
        config = MongoDBConnectionConfig(config={
            "host": "dbhost",
            "database": "testdb",
            "username": "admin",
            "password": "secret",
        })
        assert config.get_host() == "dbhost"
        assert config.get_database() == "testdb"

    def test_init_defaults(self):
        """Default values are applied."""
        config = MongoDBConnectionConfig(database="testdb")
        assert config.get_host() == "localhost"
        assert config.get_port() == 27017
        assert config.get_auth_source() == "admin"
        assert config.is_tls_enabled() is False

    def test_init_instance_metadata(self):
        """Instance metadata fields are stored."""
        config = MongoDBConnectionConfig(
            database="testdb",
            instance_name="prod-mongo-1",
            environment="production",
            description="Primary production instance",
            tags=["prod", "primary"],
            metadata={"region": "us-east-1"},
        )
        assert config.get_instance_name() == "prod-mongo-1"
        assert config.get_environment() == "production"
        assert config.get_description() == "Primary production instance"
        assert config.get_tags() == ["prod", "primary"]
        assert config.get_metadata() == {"region": "us-east-1"}

    def test_init_metadata_defaults(self):
        """Metadata fields default to None or empty."""
        config = MongoDBConnectionConfig(database="testdb")
        assert config.get_instance_name() is None
        assert config.get_environment() is None
        assert config.get_description() is None
        assert config.get_tags() == []
        assert config.get_metadata() == {}

    def test_validate_missing_database(self):
        """Missing database raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Missing required"):
            MongoDBConnectionConfig(host="localhost")

    def test_validate_scram_requires_password(self):
        """SCRAM-SHA-256 requires password."""
        with pytest.raises(ConfigurationError, match="requires password"):
            MongoDBConnectionConfig(
                database="testdb",
                username="user",
                auth_mechanism="SCRAM-SHA-256",
            )

    def test_validate_gssapi_requires_username(self):
        """GSSAPI requires username."""
        with pytest.raises(ConfigurationError, match="requires username"):
            MongoDBConnectionConfig(
                database="testdb",
                auth_mechanism="GSSAPI",
            )

    def test_validate_x509_requires_tls(self):
        """X.509 requires TLS."""
        with pytest.raises(ConfigurationError, match="requires TLS"):
            MongoDBConnectionConfig(
                database="testdb",
                auth_mechanism="MONGODB-X509",
            )

    def test_validate_unsupported_auth_mechanism(self):
        """Unsupported auth mechanism raises error."""
        with pytest.raises(ConfigurationError, match="Unsupported auth_mechanism"):
            MongoDBConnectionConfig(
                database="testdb",
                auth_mechanism="INVALID",
            )

    def test_validate_username_without_password(self):
        """Username without password raises error."""
        with pytest.raises(ConfigurationError, match="Password is required"):
            MongoDBConnectionConfig(
                database="testdb",
                username="user",
            )

    def test_validate_connection_string_requires_database(self):
        """Connection string still requires database."""
        with pytest.raises(ConfigurationError, match="Database name is required"):
            MongoDBConnectionConfig(
                connection_string="mongodb://localhost:27017/",
            )

    def test_validate_invalid_port(self):
        """Invalid port raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Invalid port number"):
            MongoDBConnectionConfig(
                host="localhost",
                database="testdb",
                port="not_a_number",
            )

    def test_from_dict(self):
        """Create config from dictionary."""
        config = MongoDBConnectionConfig.from_dict({
            "host": "dbhost",
            "database": "testdb",
            "username": "admin",
            "password": "secret",
        })
        assert config.get_host() == "dbhost"
        assert config.get_database() == "testdb"

    def test_from_connection_string(self):
        """Create config from connection string."""
        config = MongoDBConnectionConfig.from_connection_string(
            "mongodb://user:pass@host1:27017/", "mydb"
        )
        assert config.get_database() == "mydb"

    def test_build_connection_string_basic(self):
        """Build basic connection string."""
        config = MongoDBConnectionConfig(host="localhost", database="testdb")
        conn_str = config.build_connection_string()

        assert conn_str.startswith("mongodb://")
        assert "localhost:27017" in conn_str
        assert "authSource=admin" in conn_str

    def test_build_connection_string_with_auth(self):
        """Build connection string with authentication."""
        config = MongoDBConnectionConfig(
            host="dbhost",
            database="testdb",
            username="user",
            password="p@ss",
            auth_mechanism="SCRAM-SHA-256",
        )
        conn_str = config.build_connection_string()

        assert "user:p%40ss@" in conn_str
        assert "authMechanism=SCRAM-SHA-256" in conn_str

    def test_build_connection_string_x509(self):
        """X.509 connection string has username but no password."""
        config = MongoDBConnectionConfig(
            host="dbhost",
            database="testdb",
            username="CN=client",
            auth_mechanism="MONGODB-X509",
            tls=True,
        )
        conn_str = config.build_connection_string()

        assert "CN%3Dclient@" in conn_str
        assert "authMechanism=MONGODB-X509" in conn_str
        assert "tls=true" in conn_str

    def test_build_connection_string_replica_set(self):
        """Build connection string with replica set."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            replica_set="rs0",
        )
        conn_str = config.build_connection_string()

        assert "replicaSet=rs0" in conn_str

    def test_build_connection_params(self):
        """Build connection parameters dict."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            server_selection_timeout_ms=3000,
            maxPoolSize=50,
        )
        params = config.build_connection_params()

        assert params["serverSelectionTimeoutMS"] == 3000
        assert params["maxPoolSize"] == 50

    def test_to_dict(self):
        """Convert config to dictionary."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            username="user",
            password="secret",
        )
        d = config.to_dict()

        assert d["host"] == "localhost"
        assert d["database"] == "testdb"
        assert d["password"] == "secret"

    def test_to_safe_dict(self):
        """Safe dict excludes sensitive fields."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            username="user",
            password="secret",
            connection_string="mongodb://user:secret@localhost:27017/",
        )
        safe = config.to_safe_dict()

        assert "password" not in safe
        assert "connection_string" not in safe
        assert safe["host"] == "localhost"

    def test_clone(self):
        """Clone creates new config with overrides."""
        original = MongoDBConnectionConfig(
            host="host1",
            database="db1",
            username="user",
            password="pass",
        )
        cloned = original.clone(database="db2")

        assert cloned.get_database() == "db2"
        assert cloned.get_host() == "host1"
        assert original.get_database() == "db1"  # Original unchanged

    def test_repr(self):
        """String representation excludes password."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            password="secret",
        )
        r = repr(config)

        assert "MongoDBConnectionConfig" in r
        assert "secret" not in r

    def test_str_basic(self):
        """String representation without instance name."""
        config = MongoDBConnectionConfig(host="localhost", database="testdb")
        s = str(config)

        assert "localhost" in s
        assert "testdb" in s

    def test_str_with_instance_name(self):
        """String representation with instance name."""
        config = MongoDBConnectionConfig(
            host="localhost",
            database="testdb",
            instance_name="prod-1",
            environment="production",
        )
        s = str(config)

        assert "prod-1" in s
        assert "production" in s

    def test_supported_auth_mechanisms(self):
        """All supported mechanisms are listed."""
        assert "SCRAM-SHA-1" in MongoDBConnectionConfig.SUPPORTED_AUTH_MECHANISMS
        assert "SCRAM-SHA-256" in MongoDBConnectionConfig.SUPPORTED_AUTH_MECHANISMS
        assert "MONGODB-X509" in MongoDBConnectionConfig.SUPPORTED_AUTH_MECHANISMS
        assert "GSSAPI" in MongoDBConnectionConfig.SUPPORTED_AUTH_MECHANISMS
        assert "PLAIN" in MongoDBConnectionConfig.SUPPORTED_AUTH_MECHANISMS
