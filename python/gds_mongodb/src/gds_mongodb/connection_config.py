"""
MongoDB connection configuration management module.

This module provides configuration classes for MongoDB connections,
allowing for reusable connection configuration across multiple instances.

Note: This module handles CONNECTION configuration (host, port, auth),
not server PARAMETER configuration (which is managed by server_config.py).
"""

import logging
from typing import Any, Optional
from urllib.parse import quote_plus

from gds_database import ConfigurableComponent, ConfigurationError

logger = logging.getLogger(__name__)


class MongoDBConnectionConfig(ConfigurableComponent):
    """
    MongoDB connection configuration class.

    Encapsulates all MongoDB connection parameters with validation.
    Supports multiple authentication mechanisms and configuration reuse.

    This class follows the OOP design pattern where configuration is
    separate from connection management, allowing:
    - Configuration reuse across multiple connections
    - Validation of configuration before connection attempts
    - Easy configuration serialization and storage
    - Configuration inheritance and composition

    Examples:
        # Create a reusable configuration
        config = MongoDBConnectionConfig(
            host='localhost',
            port=27017,
            database='mydb',
            username='myuser',
            password='mypass',
            auth_mechanism='SCRAM-SHA-256'
        )

        # Use the same config for multiple connections
        conn1 = MongoDBConnection(config=config)
        conn2 = MongoDBConnection(config=config)

        # Create from dictionary
        config_dict = {
            'host': 'localhost',
            'database': 'mydb',
            'auth_mechanism': 'GSSAPI',
            'username': 'user@REALM'
        }
        config = MongoDBConnectionConfig.from_dict(config_dict)

        # Modify configuration
        config.set_config('maxPoolSize', 100)
        config.set_config('tls', True)
    """

    # Supported authentication mechanisms
    SUPPORTED_AUTH_MECHANISMS = [
        "SCRAM-SHA-1",
        "SCRAM-SHA-256",
        "MONGODB-X509",
        "GSSAPI",
        "PLAIN",
    ]

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
        auth_source: Optional[str] = None,
        auth_mechanism: Optional[str] = None,
        replica_set: Optional[str] = None,
        tls: Optional[bool] = None,
        instance_name: Optional[str] = None,
        environment: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        config: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize MongoDB configuration.

        Args:
            host: MongoDB server host
            port: MongoDB server port
            database: Database name
            username: Username for authentication
            password: Password for authentication
            connection_string: Complete MongoDB connection string
            auth_source: Authentication database
            auth_mechanism: Authentication mechanism
            replica_set: Replica set name
            tls: Enable TLS/SSL
            instance_name: Name/identifier for this configuration (optional)
            environment: Environment name (e.g., dev, staging, prod) (optional)
            description: Human-readable description (optional)
            tags: List of tags for categorization (optional)
            metadata: Additional metadata dictionary (optional)
            config: Configuration dictionary
            **kwargs: Additional MongoDB connection parameters
        """
        # Build configuration dictionary
        config_dict: dict[str, Any] = dict(config) if config else {}

        # Add individual parameters to config
        if host is not None:
            config_dict["host"] = host
        if port is not None:
            config_dict["port"] = port
        if database is not None:
            config_dict["database"] = database
        if username is not None:
            config_dict["username"] = username
        if password is not None:
            config_dict["password"] = password
        if connection_string is not None:
            config_dict["connection_string"] = connection_string
        if auth_source is not None:
            config_dict["auth_source"] = auth_source
        if auth_mechanism is not None:
            config_dict["auth_mechanism"] = auth_mechanism
        if replica_set is not None:
            config_dict["replica_set"] = replica_set
        if tls is not None:
            config_dict["tls"] = tls

        # Add instance metadata fields
        if instance_name is not None:
            config_dict["instance_name"] = instance_name
        if environment is not None:
            config_dict["environment"] = environment
        if description is not None:
            config_dict["description"] = description
        if tags is not None:
            config_dict["tags"] = tags
        if metadata is not None:
            config_dict["metadata"] = metadata

        # Add additional parameters
        if kwargs:
            config_dict.update(kwargs)

        # Set defaults
        config_dict.setdefault("host", "localhost")
        config_dict.setdefault("port", 27017)
        config_dict.setdefault("auth_source", "admin")
        config_dict.setdefault("server_selection_timeout_ms", 5000)

        # Initialize parent class (which calls validate_config)
        super().__init__(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "MongoDBConnectionConfig":
        """
        Create MongoDBConnectionConfig from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            MongoDBConnectionConfig instance

        Example:
            config_dict = {
                'host': 'localhost',
                'port': 27017,
                'database': 'mydb',
                'username': 'user',
                'password': 'pass'
            }
            config = MongoDBConnectionConfig.from_dict(config_dict)
        """
        return cls(config=config_dict)

    @classmethod
    def from_connection_string(cls, connection_string: str, database: str) -> "MongoDBConnectionConfig":
        """
        Create MongoDBConnectionConfig from connection string.

        Args:
            connection_string: MongoDB connection string
            database: Database name

        Returns:
            MongoDBConnectionConfig instance

        Example:
            config = MongoDBConnectionConfig.from_connection_string(
                'mongodb://user:pass@localhost:27017/',
                'mydb'
            )
        """
        return cls(connection_string=connection_string, database=database)

    def validate_config(self) -> bool:
        """
        Validate MongoDB configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # If connection_string is provided, database is still required
        if not self.config.get("connection_string"):
            # Validate individual parameters
            required_fields = ["host", "database"]
            missing_fields = [field for field in required_fields if not self.config.get(field)]

            if missing_fields:
                raise ConfigurationError(f"Missing required configuration fields: {missing_fields}")

            # Validate authentication requirements
            auth_mechanism = self.config.get("auth_mechanism")

            if auth_mechanism in ["SCRAM-SHA-1", "SCRAM-SHA-256", "PLAIN"]:
                # These mechanisms require username and password
                if not self.config.get("username"):
                    raise ConfigurationError(f"{auth_mechanism} requires username")
                if not self.config.get("password"):
                    raise ConfigurationError(f"{auth_mechanism} requires password")
            elif auth_mechanism == "GSSAPI":
                # Kerberos authentication requires username
                if not self.config.get("username"):
                    raise ConfigurationError("GSSAPI (Kerberos) requires username")
            elif auth_mechanism == "MONGODB-X509":
                # X.509 doesn't require password, but needs TLS
                if not self.config.get("tls"):
                    raise ConfigurationError("MONGODB-X509 requires TLS to be enabled")
            elif auth_mechanism and auth_mechanism not in self.SUPPORTED_AUTH_MECHANISMS:
                raise ConfigurationError(
                    f"Unsupported auth_mechanism: {auth_mechanism}. "
                    f"Supported: {', '.join(self.SUPPORTED_AUTH_MECHANISMS)}"
                )
            else:
                # No auth_mechanism specified, basic validation
                username = self.config.get("username")
                password = self.config.get("password")
                if username and not password:
                    raise ConfigurationError("Password is required when username is provided")
        # Connection string provided
        elif not self.config.get("database"):
            raise ConfigurationError("Database name is required even when using connection string")

        # Validate port is a number
        port = self.config.get("port")
        if port and not isinstance(port, int):
            try:
                self.config["port"] = int(port)
            except ValueError as err:
                raise ConfigurationError(f"Invalid port number: {port}") from err

        return True

    def build_connection_string(self) -> str:
        """
        Build MongoDB connection string from configuration.

        Returns:
            MongoDB connection string

        Example:
            config = MongoDBConnectionConfig(host='localhost', database='mydb')
            conn_str = config.build_connection_string()
            # Returns: "mongodb://localhost:27017/"
        """
        # Build authentication part
        auth_part = ""
        auth_mechanism = self.config.get("auth_mechanism")

        # For most mechanisms, include username:password in URI
        # MONGODB-X509 doesn't use password in connection string
        if self.config.get("username"):
            if auth_mechanism == "MONGODB-X509":
                # X.509 uses username but not password
                username = quote_plus(self.config["username"])
                auth_part = f"{username}@"
            elif self.config.get("password"):
                username = quote_plus(self.config["username"])
                password = quote_plus(self.config["password"])
                auth_part = f"{username}:{password}@"

        # Build host part
        host = self.config["host"]
        port = self.config.get("port", 27017)
        host_part = f"{host}:{port}"

        # Build options part
        options = []
        if self.config.get("auth_source"):
            options.append(f"authSource={self.config['auth_source']}")
        if auth_mechanism:
            options.append(f"authMechanism={auth_mechanism}")
        if self.config.get("replica_set"):
            options.append(f"replicaSet={self.config['replica_set']}")
        if self.config.get("tls"):
            options.append("tls=true")

        options_part = "?" + "&".join(options) if options else ""

        return f"mongodb://{auth_part}{host_part}/{options_part}"

    def build_connection_params(self) -> dict[str, Any]:
        """
        Build additional connection parameters for MongoClient.

        Returns:
            Dictionary of connection parameters

        Example:
            config = MongoDBConnectionConfig(
                host='localhost',
                database='mydb',
                maxPoolSize=50
            )
            params = config.build_connection_params()
            # Returns: {'serverSelectionTimeoutMS': 5000, 'maxPoolSize': 50}
        """
        params = {}

        if self.config.get("server_selection_timeout_ms"):
            params["serverSelectionTimeoutMS"] = self.config["server_selection_timeout_ms"]

        # Add any other pymongo-specific parameters from config
        pymongo_params = [
            "maxPoolSize",
            "minPoolSize",
            "maxIdleTimeMS",
            "waitQueueTimeoutMS",
            "connectTimeoutMS",
            "socketTimeoutMS",
        ]

        for param in pymongo_params:
            if param in self.config:
                params[param] = self.config[param]

        return params

    def get_host(self) -> str:
        """Get host from configuration."""
        return self.config.get("host", "localhost")

    def get_port(self) -> int:
        """Get port from configuration."""
        return self.config.get("port", 27017)

    def get_database(self) -> str:
        """Get database name from configuration."""
        return self.config["database"]

    def get_username(self) -> Optional[str]:
        """Get username from configuration."""
        return self.config.get("username")

    def get_auth_mechanism(self) -> Optional[str]:
        """Get authentication mechanism from configuration."""
        return self.config.get("auth_mechanism")

    def get_auth_source(self) -> str:
        """Get authentication source from configuration."""
        return self.config.get("auth_source", "admin")

    def is_tls_enabled(self) -> bool:
        """Check if TLS is enabled."""
        return bool(self.config.get("tls", False))

    def get_instance_name(self) -> Optional[str]:
        """Get instance name/identifier."""
        return self.config.get("instance_name")

    def get_environment(self) -> Optional[str]:
        """Get environment name."""
        return self.config.get("environment")

    def get_description(self) -> Optional[str]:
        """Get instance description."""
        return self.config.get("description")

    def get_tags(self) -> list[str]:
        """Get instance tags."""
        return self.config.get("tags", [])

    def get_metadata(self) -> dict[str, Any]:
        """Get instance metadata."""
        return self.config.get("metadata", {})

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary (excludes sensitive data by default)

        Example:
            config = MongoDBConnectionConfig(host='localhost', database='mydb')
            config_dict = config.to_dict()
        """
        # Return a copy to prevent external modification
        return dict(self.config)

    def to_safe_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary without sensitive data.

        Returns:
            Configuration dictionary with passwords removed

        Example:
            config = MongoDBConnectionConfig(
                host='localhost',
                database='mydb',
                password='secret'
            )
            safe_dict = config.to_safe_dict()
            # 'password' field is excluded
        """
        safe_config = dict(self.config)
        # Remove sensitive fields
        sensitive_fields = ["password", "connection_string"]
        for field in sensitive_fields:
            safe_config.pop(field, None)
        return safe_config

    def clone(self, **overrides) -> "MongoDBConnectionConfig":
        """
        Create a copy of this configuration with optional overrides.

        Args:
            **overrides: Configuration values to override

        Returns:
            New MongoDBConnectionConfig instance

        Example:
            original = MongoDBConnectionConfig(
                host='localhost', database='db1'
            )
            clone = original.clone(database='db2')
            # clone has same config as original but different database
        """
        new_config = dict(self.config)
        new_config.update(overrides)
        return MongoDBConnectionConfig(config=new_config)

    def __repr__(self) -> str:
        """String representation of configuration."""
        safe_config = self.to_safe_dict()
        return f"MongoDBConnectionConfig({safe_config})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        instance_name = self.get_instance_name()
        environment = self.get_environment()

        if instance_name:
            env_str = f" ({environment})" if environment else ""
            return (
                f"MongoDB Instance '{instance_name}'{env_str}: "
                f"{self.get_host()}:{self.get_port()}/{self.get_database()}"
            )
        return f"MongoDB Configuration: {self.get_host()}:{self.get_port()}/{self.get_database()}"
