"""
MongoDB database connection implementation.

This module provides a concrete implementation of the DatabaseConnection
interface for MongoDB databases using pymongo.
"""

from __future__ import annotations

import logging
from typing import Any

from gds_database import (
    ConfigurableComponent,
    DatabaseConnection,
    DatabaseConnectionError,
    QueryError,
    ResourceManager,
)
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    ServerSelectionTimeoutError,
)

from .connection_config import MongoDBConnectionConfig

logger = logging.getLogger(__name__)


class MongoDBConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    MongoDB database connection implementation.

    Provides a complete implementation of the DatabaseConnection interface
    for MongoDB databases using pymongo. Supports both connection strings
    and individual parameters for connection configuration.

    Examples:
        # Using individual parameters
        conn = MongoDBConnection(
            host='localhost',
            port=27017,
            database='mydb',
            username='myuser',
            password='mypassword'
        )

        # Using connection string
        conn = MongoDBConnection(
            connection_string='mongodb://user:pass@localhost:27017/mydb'
        )

        # Using configuration dictionary
        config = {
            'host': 'localhost',
            'port': 27017,
            'database': 'mydb',
            'username': 'myuser',
            'password': 'mypassword',
            'auth_source': 'admin',
            'server_selection_timeout_ms': 5000
        }
        conn = MongoDBConnection(config=config)

        # Using as context manager
        with MongoDBConnection(host='localhost', database='mydb') as conn:
            results = conn.execute_query('users', {'age': {'$gte': 18}})
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        username: str | None = None,
        password: str | None = None,
        connection_string: str | None = None,
        auth_source: str | None = None,
        auth_mechanism: str | None = None,
        replica_set: str | None = None,
        tls: bool | None = None,
        config: MongoDBConnectionConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize MongoDB connection.

        Args:
            host: MongoDB server host (default: 'localhost')
            port: MongoDB server port (default: 27017)
            database: Database name
            username: Username for authentication
            password: Password for authentication
            connection_string: Complete MongoDB connection string
            auth_source: Authentication database (default: 'admin')
            auth_mechanism: Authentication mechanism (SCRAM-SHA-1,
                SCRAM-SHA-256, MONGODB-X509, GSSAPI, PLAIN)
            replica_set: Replica set name
            tls: Enable TLS/SSL connection
            config: MongoDBConnectionConfig instance or configuration dictionary
            **kwargs: Additional pymongo connection parameters
        """
        # Build or reuse a MongoDBConnectionConfig for validation and connection building
        if isinstance(config, MongoDBConnectionConfig):
            self._connection_config = config
        else:
            self._connection_config = MongoDBConnectionConfig(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                connection_string=connection_string,
                auth_source=auth_source,
                auth_mechanism=auth_mechanism,
                replica_set=replica_set,
                tls=tls,
                config=config if isinstance(config, dict) else None,
                **kwargs,
            )

        # Initialize parent class using the validated config dict
        ConfigurableComponent.__init__(self, self._connection_config.to_dict())

        # Connection state
        self.client: MongoClient | None = None
        self._db = None

    def validate_config(self) -> bool:
        """
        Validate MongoDB connection configuration.

        Delegates to MongoDBConnectionConfig for validation logic.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        return self._connection_config.validate_config()

    def connect(self) -> MongoClient:
        """
        Establish connection to MongoDB database.

        Returns:
            MongoClient connection object

        Raises:
            DatabaseConnectionError: If connection cannot be established
        """
        if self.is_connected():
            logger.info("Already connected to MongoDB database")
            return self.client

        try:
            connection_params = self._build_connection_params()

            logger.info(
                "Connecting to MongoDB database: %s on %s",
                self.config.get("database"),
                self.config.get("host", "connection string"),
            )

            # Establish connection
            if self.config.get("connection_string"):
                self.client = MongoClient(self.config["connection_string"], **connection_params)
            else:
                conn_string = self._build_connection_string()
                self.client = MongoClient(conn_string, **connection_params)

            # Get database reference
            self._db = self.client[self.config["database"]]

            # Test connection
            self.client.admin.command("ping")

            logger.info("Successfully connected to MongoDB database")
            return self.client

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            error_msg = f"Failed to connect to MongoDB database: {e}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to MongoDB: {e}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """
        Close MongoDB database connection.

        Properly closes the client connection, handling any errors gracefully.
        """
        try:
            if self.client:
                self.client.close()
                logger.info("Disconnected from MongoDB database")

        except Exception as e:
            logger.warning("Error during disconnect: %s", e)
        finally:
            self._db = None
            self.client = None

    def execute_query(
        self,
        collection: str,
        filter_query: dict[str, Any] | None = None,
        projection: dict[str, Any] | None = None,
        limit: int = 0,
        skip: int = 0,
        sort: list[tuple] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            collection: Collection name to query
            filter_query: MongoDB filter/query document (default: {})
            projection: Fields to include/exclude in results
            limit: Maximum number of documents to return (0 = no limit)
            skip: Number of documents to skip
            sort: List of (field, direction) tuples for sorting

        Returns:
            List of documents matching the query

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If query execution fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            filter_query = filter_query or {}
            coll = self._db[collection]

            logger.debug("Executing query on collection '%s': %s", collection, filter_query)

            # Build cursor
            cursor = coll.find(filter_query, projection)

            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            if sort:
                cursor = cursor.sort(sort)

            results = list(cursor)

            logger.debug(
                "Query on collection '%s' returned %d documents",
                collection,
                len(results),
            )
            return results

        except OperationFailure as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during query execution: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def execute_query_dict(
        self, collection: str, filter_query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute query and return results as dictionaries.

        MongoDB already returns dictionaries, so this is an alias for execute_query.

        Args:
            collection: Collection name to query
            filter_query: MongoDB filter/query document

        Returns:
            List of dictionaries representing query results
        """
        return self.execute_query(collection, filter_query)

    def insert_one(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        """
        Insert a single document into a collection.

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            Dictionary with inserted_id

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If insert fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.insert_one(document)

            logger.debug(
                "Inserted document into collection '%s' with id: %s",
                collection,
                result.inserted_id,
            )

            return {"inserted_id": result.inserted_id}

        except OperationFailure as e:
            error_msg = f"Insert failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Insert multiple documents into a collection.

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            Dictionary with inserted_ids

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If insert fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.insert_many(documents)

            logger.debug(
                "Inserted %d documents into collection '%s'",
                len(result.inserted_ids),
                collection,
            )

            return {"inserted_ids": result.inserted_ids}

        except OperationFailure as e:
            error_msg = f"Insert many failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def update_one(
        self,
        collection: str,
        filter_query: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> dict[str, Any]:
        """
        Update a single document in a collection.

        Args:
            collection: Collection name
            filter_query: Query to match document
            update: Update operations to apply
            upsert: If True, insert document if not found

        Returns:
            Dictionary with update results

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If update fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.update_one(filter_query, update, upsert=upsert)

            logger.debug(
                "Updated %d document(s) in collection '%s'",
                result.modified_count,
                collection,
            )

            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": result.upserted_id,
            }

        except OperationFailure as e:
            error_msg = f"Update failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def update_many(
        self,
        collection: str,
        filter_query: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> dict[str, Any]:
        """
        Update multiple documents in a collection.

        Args:
            collection: Collection name
            filter_query: Query to match documents
            update: Update operations to apply
            upsert: If True, insert document if not found

        Returns:
            Dictionary with update results

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If update fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.update_many(filter_query, update, upsert=upsert)

            logger.debug(
                "Updated %d document(s) in collection '%s'",
                result.modified_count,
                collection,
            )

            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": result.upserted_id,
            }

        except OperationFailure as e:
            error_msg = f"Update many failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def delete_one(self, collection: str, filter_query: dict[str, Any]) -> dict[str, Any]:
        """
        Delete a single document from a collection.

        Args:
            collection: Collection name
            filter_query: Query to match document

        Returns:
            Dictionary with delete results

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If delete fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.delete_one(filter_query)

            logger.debug(
                "Deleted %d document(s) from collection '%s'",
                result.deleted_count,
                collection,
            )

            return {"deleted_count": result.deleted_count}

        except OperationFailure as e:
            error_msg = f"Delete failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def delete_many(self, collection: str, filter_query: dict[str, Any]) -> dict[str, Any]:
        """
        Delete multiple documents from a collection.

        Args:
            collection: Collection name
            filter_query: Query to match documents

        Returns:
            Dictionary with delete results

        Raises:
            DatabaseConnectionError: If not connected to database
            QueryError: If delete fails
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            result = coll.delete_many(filter_query)

            logger.debug(
                "Deleted %d document(s) from collection '%s'",
                result.deleted_count,
                collection,
            )

            return {"deleted_count": result.deleted_count}

        except OperationFailure as e:
            error_msg = f"Delete many failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def is_connected(self) -> bool:
        """
        Check if connection is active.

        Returns:
            True if connection is active and usable, False otherwise
        """
        if not self.client:
            return False

        try:
            # Try to ping the server
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_connection_info(self) -> dict[str, Any]:
        """
        Get connection information.

        Returns:
            Dictionary containing connection metadata
        """
        info = {
            "database_type": "mongodb",
            "host": self.config.get("host"),
            "port": self.config.get("port"),
            "database": self.config.get("database"),
            "username": self.config.get("username"),
            "auth_source": self.config.get("auth_source"),
            "replica_set": self.config.get("replica_set"),
            "connected": self.is_connected(),
        }

        if self.client:
            try:
                # Get server info
                server_info = self.client.server_info()
                info["server_version"] = server_info.get("version")
            except Exception:
                pass

        return info

    def begin_transaction(self) -> None:
        """
        Begin a new transaction.

        Raises:
            NotImplementedError: MongoDB multi-document transactions require
                replica sets and ClientSession. Use pymongo's session API directly
                for transaction support.
        """
        raise NotImplementedError(
            "Multi-document transactions require a replica set and pymongo ClientSession. "
            "Use client.start_session() and session.start_transaction() directly."
        )

    def commit(self) -> None:
        """
        Commit current transaction.

        Raises:
            NotImplementedError: MongoDB multi-document transactions require
                replica sets and ClientSession. Use pymongo's session API directly
                for transaction support.
        """
        raise NotImplementedError(
            "Multi-document transactions require a replica set and pymongo ClientSession. "
            "Use client.start_session() and session.commit_transaction() directly."
        )

    def rollback(self) -> None:
        """
        Rollback current transaction.

        Raises:
            NotImplementedError: MongoDB multi-document transactions require
                replica sets and ClientSession. Use pymongo's session API directly
                for transaction support.
        """
        raise NotImplementedError(
            "Multi-document transactions require a replica set and pymongo ClientSession. "
            "Use client.start_session() and session.abort_transaction() directly."
        )

    def get_collection_names(self) -> list[str]:
        """
        Get list of collection names in the database.

        Returns:
            List of collection names

        Raises:
            DatabaseConnectionError: If not connected to database
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            return sorted(self._db.list_collection_names())
        except Exception as e:
            error_msg = f"Failed to get collection names: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_table_names(self, schema: str | None = None) -> list[str]:
        """
        Get list of collection names (MongoDB equivalent of tables).

        Args:
            schema: Not used in MongoDB (included for interface compatibility)

        Returns:
            List of collection names
        """
        return self.get_collection_names()

    def get_column_info(self, collection: str, sample_size: int = 100) -> list[dict[str, Any]]:
        """
        Get field information for a collection by sampling documents.

        Args:
            collection: Collection name
            sample_size: Number of documents to sample for field analysis

        Returns:
            List of dictionaries containing field information

        Raises:
            DatabaseConnectionError: If not connected to database
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to MongoDB database")

        try:
            coll = self._db[collection]
            sample = list(coll.find().limit(sample_size))

            if not sample:
                return []

            # Analyze fields from sample
            fields = {}
            for doc in sample:
                for field, value in doc.items():
                    if field not in fields:
                        fields[field] = {
                            "field_name": field,
                            "data_type": type(value).__name__,
                            "count": 1,
                        }
                    else:
                        fields[field]["count"] += 1

            # Convert to list and sort by field name
            field_list = list(fields.values())
            field_list.sort(key=lambda x: x["field_name"])

            return field_list

        except Exception as e:
            error_msg = f"Failed to get field information: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    # ResourceManager implementation
    def initialize(self) -> None:
        """Initialize resources (establish connection)."""
        self.connect()

    def cleanup(self) -> None:
        """Clean up resources (close connection)."""
        self.disconnect()

    def is_initialized(self) -> bool:
        """Check if resources are initialized (connected)."""
        return self.is_connected()

    def _build_connection_string(self) -> str:
        """Build MongoDB connection string from individual parameters."""
        return self._connection_config.build_connection_string()

    def _build_connection_params(self) -> dict[str, Any]:
        """Build additional connection parameters for MongoClient."""
        return self._connection_config.build_connection_params()
