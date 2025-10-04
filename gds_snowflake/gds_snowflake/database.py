"""
Snowflake Database Metadata Module

This module provides functions to retrieve metadata about Snowflake database objects
(databases, schemas, functions, procedures, stages, pipes, tasks, streams, etc.).
For table-related metadata, use the table module.
"""

import logging
from typing import Optional, List, Dict, Any
from gds_snowflake.connection import SnowflakeConnection

logger = logging.getLogger(__name__)


class SnowflakeDatabase:
    """
    Provides methods to retrieve metadata about Snowflake database-level objects.

    This class wraps Snowflake's INFORMATION_SCHEMA and ACCOUNT_USAGE views
    to provide comprehensive metadata about databases, schemas, functions,
    procedures, sequences, stages, file formats, pipes, tasks, and streams.

    For table, view, and column metadata, use the SnowflakeTable class.
    """

    def __init__(self, connection: SnowflakeConnection):
        """
        Initialize the database metadata retriever.

        Args:
            connection: SnowflakeConnection instance
        """
        self.connection = connection

    # =========================================================================
    # Database and Schema Metadata
    # =========================================================================

    def get_databases(self) -> List[Dict[str, Any]]:
        """
        Get metadata about all databases in the account.

        Returns:
            List of dictionaries containing database metadata
        """
        query = """
        SELECT
            DATABASE_NAME,
            DATABASE_OWNER,
            IS_TRANSIENT,
            COMMENT,
            CREATED,
            LAST_ALTERED,
            RETENTION_TIME
        FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
        ORDER BY DATABASE_NAME
        """
        try:
            logger.info("Retrieving database metadata")
            return self.connection.execute_query_dict(query)
        except Exception as e:
            logger.error("Error retrieving database metadata: %s", e)
            raise

    def get_database_info(self, database_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific database.

        Args:
            database_name: Name of the database

        Returns:
            Dictionary containing database metadata or None if not found
        """
        query = """
        SELECT
            DATABASE_NAME,
            DATABASE_OWNER,
            IS_TRANSIENT,
            COMMENT,
            CREATED,
            LAST_ALTERED,
            RETENTION_TIME
        FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
        WHERE DATABASE_NAME = %s
        """
        try:
            logger.info("Retrieving metadata for database: %s", database_name)
            results = self.connection.execute_query_dict(query, (database_name,))
            return results[0] if results else None
        except Exception as e:
            logger.error(
                "Error retrieving database metadata for %s: %s", database_name, e
            )
            raise

    def get_schemas(self, database_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get metadata about schemas.

        Args:
            database_name: Optional database name to filter schemas

        Returns:
            List of dictionaries containing schema metadata
        """
        if database_name:
            query = """
            SELECT
                CATALOG_NAME AS DATABASE_NAME,
                SCHEMA_NAME,
                SCHEMA_OWNER,
                IS_TRANSIENT,
                IS_MANAGED_ACCESS,
                COMMENT,
                CREATED,
                LAST_ALTERED,
                RETENTION_TIME
            FROM SNOWFLAKE.INFORMATION_SCHEMA.SCHEMATA
            WHERE CATALOG_NAME = %s
            ORDER BY SCHEMA_NAME
            """
            params = (database_name,)
        else:
            query = """
            SELECT
                CATALOG_NAME AS DATABASE_NAME,
                SCHEMA_NAME,
                SCHEMA_OWNER,
                IS_TRANSIENT,
                IS_MANAGED_ACCESS,
                COMMENT,
                CREATED,
                LAST_ALTERED,
                RETENTION_TIME
            FROM SNOWFLAKE.INFORMATION_SCHEMA.SCHEMATA
            ORDER BY CATALOG_NAME, SCHEMA_NAME
            """
            params = None

        try:
            logger.info("Retrieving schema metadata")
            return self.connection.execute_query_dict(query, params)
        except Exception as e:
            logger.error("Error retrieving schema metadata: %s", e)
            raise

    # =========================================================================
    # NOTE: Table, View, and Column metadata methods have been moved to
    #       the SnowflakeTable class in the table module.
    #       Use: from gds_snowflake import SnowflakeTable
    # =========================================================================

    # =========================================================================
    # Function and Procedure Metadata
    # =========================================================================

    def get_functions(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about user-defined functions (UDFs).

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing function metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("FUNCTION_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("FUNCTION_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            FUNCTION_CATALOG AS DATABASE_NAME,
            FUNCTION_SCHEMA AS SCHEMA_NAME,
            FUNCTION_NAME,
            FUNCTION_LANGUAGE,
            FUNCTION_DEFINITION,
            DATA_TYPE AS RETURN_TYPE,
            ARGUMENT_SIGNATURE,
            IS_SECURE,
            IS_EXTERNAL,
            CREATED,
            LAST_ALTERED,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.FUNCTIONS
        WHERE {where_clause}
        ORDER BY FUNCTION_CATALOG, FUNCTION_SCHEMA, FUNCTION_NAME
        """

        try:
            logger.info("Retrieving function metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving function metadata: %s", e)
            raise

    def get_procedures(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about stored procedures.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing procedure metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("PROCEDURE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("PROCEDURE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            PROCEDURE_CATALOG AS DATABASE_NAME,
            PROCEDURE_SCHEMA AS SCHEMA_NAME,
            PROCEDURE_NAME,
            PROCEDURE_LANGUAGE,
            PROCEDURE_DEFINITION,
            ARGUMENT_SIGNATURE,
            IS_SECURE,
            CREATED,
            LAST_ALTERED,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.PROCEDURES
        WHERE {where_clause}
        ORDER BY PROCEDURE_CATALOG, PROCEDURE_SCHEMA, PROCEDURE_NAME
        """

        try:
            logger.info("Retrieving procedure metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving procedure metadata: %s", e)
            raise

    # =========================================================================
    # Sequence Metadata
    # =========================================================================

    def get_sequences(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about sequences.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing sequence metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("SEQUENCE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("SEQUENCE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            SEQUENCE_CATALOG AS DATABASE_NAME,
            SEQUENCE_SCHEMA AS SCHEMA_NAME,
            SEQUENCE_NAME,
            DATA_TYPE,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            START_VALUE,
            MINIMUM_VALUE,
            MAXIMUM_VALUE,
            INCREMENT,
            CYCLE_OPTION,
            CREATED,
            LAST_ALTERED,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.SEQUENCES
        WHERE {where_clause}
        ORDER BY SEQUENCE_CATALOG, SEQUENCE_SCHEMA, SEQUENCE_NAME
        """

        try:
            logger.info("Retrieving sequence metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving sequence metadata: %s", e)
            raise

    # =========================================================================
    # Stage Metadata
    # =========================================================================

    def get_stages(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about stages.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing stage metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("STAGE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("STAGE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            STAGE_CATALOG AS DATABASE_NAME,
            STAGE_SCHEMA AS SCHEMA_NAME,
            STAGE_NAME,
            STAGE_URL,
            STAGE_REGION,
            STAGE_TYPE,
            STAGE_OWNER,
            COMMENT,
            CREATED,
            LAST_ALTERED
        FROM SNOWFLAKE.INFORMATION_SCHEMA.STAGES
        WHERE {where_clause}
        ORDER BY STAGE_CATALOG, STAGE_SCHEMA, STAGE_NAME
        """

        try:
            logger.info("Retrieving stage metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving stage metadata: %s", e)
            raise

    # =========================================================================
    # File Format Metadata
    # =========================================================================

    def get_file_formats(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about file formats.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing file format metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("FILE_FORMAT_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("FILE_FORMAT_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            FILE_FORMAT_CATALOG AS DATABASE_NAME,
            FILE_FORMAT_SCHEMA AS SCHEMA_NAME,
            FILE_FORMAT_NAME,
            FILE_FORMAT_TYPE,
            FILE_FORMAT_OWNER,
            COMMENT,
            CREATED,
            LAST_ALTERED
        FROM SNOWFLAKE.INFORMATION_SCHEMA.FILE_FORMATS
        WHERE {where_clause}
        ORDER BY FILE_FORMAT_CATALOG, FILE_FORMAT_SCHEMA, FILE_FORMAT_NAME
        """

        try:
            logger.info("Retrieving file format metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving file format metadata: %s", e)
            raise

    # =========================================================================
    # Pipe Metadata
    # =========================================================================

    def get_pipes(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about pipes (for Snowpipe).

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing pipe metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("PIPE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("PIPE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            PIPE_CATALOG AS DATABASE_NAME,
            PIPE_SCHEMA AS SCHEMA_NAME,
            PIPE_NAME,
            PIPE_OWNER,
            DEFINITION,
            NOTIFICATION_CHANNEL_NAME,
            COMMENT,
            CREATED,
            LAST_ALTERED
        FROM SNOWFLAKE.INFORMATION_SCHEMA.PIPES
        WHERE {where_clause}
        ORDER BY PIPE_CATALOG, PIPE_SCHEMA, PIPE_NAME
        """

        try:
            logger.info("Retrieving pipe metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving pipe metadata: %s", e)
            raise

    # =========================================================================
    # Task and Stream Metadata
    # =========================================================================

    def get_tasks(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about tasks.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing task metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("database_name = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("schema_name = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            database_name,
            schema_name,
            name AS task_name,
            schedule,
            state,
            definition,
            warehouse,
            condition_text,
            allow_overlapping_execution,
            created_on,
            last_committed_on,
            comment
        FROM SNOWFLAKE.ACCOUNT_USAGE.TASKS
        WHERE {where_clause}
        ORDER BY database_name, schema_name, name
        """

        try:
            logger.info("Retrieving task metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving task metadata: %s", e)
            raise

    def get_streams(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about streams.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing stream metadata
        """
        conditions = []
        params = []

        if database_name:
            conditions.append("TABLE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("TABLE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            TABLE_CATALOG AS DATABASE_NAME,
            TABLE_SCHEMA AS SCHEMA_NAME,
            TABLE_NAME AS STREAM_NAME,
            SOURCE_TYPE,
            BASE_TABLE_NAME,
            OWNER,
            COMMENT,
            CREATED,
            LAST_ALTERED
        FROM SNOWFLAKE.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'STREAM' AND {where_clause}
        ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
        """

        try:
            logger.info("Retrieving stream metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving stream metadata: %s", e)
            raise

    # =========================================================================
    # Comprehensive Metadata Retrieval
    # =========================================================================

    def get_all_database_metadata(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive metadata about database-level Snowflake objects.

        Note: This does NOT include table, view, or column metadata.
        For table-related metadata, use SnowflakeTable.get_all_table_metadata()

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            Dictionary containing all database-level metadata organized by object type
        """
        logger.info("Retrieving comprehensive database metadata for Snowflake objects")

        metadata = {
            "databases": (
                self.get_databases()
                if not database_name
                else [self.get_database_info(database_name)]
            ),
            "schemas": self.get_schemas(database_name),
            "functions": self.get_functions(database_name, schema_name),
            "procedures": self.get_procedures(database_name, schema_name),
            "sequences": self.get_sequences(database_name, schema_name),
            "stages": self.get_stages(database_name, schema_name),
            "file_formats": self.get_file_formats(database_name, schema_name),
            "pipes": self.get_pipes(database_name, schema_name),
            "tasks": self.get_tasks(database_name, schema_name),
            "streams": self.get_streams(database_name, schema_name),
        }

        # Add summary counts
        metadata["summary"] = {
            "database_count": len([d for d in metadata["databases"] if d]),
            "schema_count": len(metadata["schemas"]),
            "function_count": len(metadata["functions"]),
            "procedure_count": len(metadata["procedures"]),
            "sequence_count": len(metadata["sequences"]),
            "stage_count": len(metadata["stages"]),
            "file_format_count": len(metadata["file_formats"]),
            "pipe_count": len(metadata["pipes"]),
            "task_count": len(metadata["tasks"]),
            "stream_count": len(metadata["streams"]),
        }

        logger.info("Successfully retrieved comprehensive database metadata")
        return metadata
