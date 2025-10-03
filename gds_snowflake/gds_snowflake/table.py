"""
Snowflake Table Metadata Module

This module provides functions to retrieve metadata about Snowflake tables,
views, and columns.
"""

import logging
from typing import Optional, List, Dict, Any
from gds_snowflake.connection import SnowflakeConnection

logger = logging.getLogger(__name__)


class SnowflakeTable:
    """
    Provides methods to retrieve metadata about Snowflake tables, views, and columns.

    This class wraps Snowflake's INFORMATION_SCHEMA views to provide comprehensive
    metadata about tables, views, and their columns.
    """

    def __init__(self, connection: SnowflakeConnection):
        """
        Initialize the table metadata retriever.

        Args:
            connection: SnowflakeConnection instance
        """
        self.connection = connection

    # =========================================================================
    # Table and View Metadata
    # =========================================================================

    def get_tables(
        self,
        database_name: Optional[str] = None,
        schema_name: Optional[str] = None,
        include_views: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about tables and optionally views.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter
            include_views: Include views in results

        Returns:
            List of dictionaries containing table metadata
        """
        table_types = "('BASE TABLE', 'VIEW')" if include_views else "('BASE TABLE')"

        conditions = [f"TABLE_TYPE IN {table_types}"]
        params = []

        if database_name:
            conditions.append("TABLE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("TABLE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            TABLE_CATALOG AS DATABASE_NAME,
            TABLE_SCHEMA AS SCHEMA_NAME,
            TABLE_NAME,
            TABLE_TYPE,
            IS_TRANSIENT,
            CLUSTERING_KEY,
            ROW_COUNT,
            BYTES,
            RETENTION_TIME,
            CREATED,
            LAST_ALTERED,
            AUTO_CLUSTERING_ON,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.TABLES
        WHERE {where_clause}
        ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
        """

        try:
            logger.info("Retrieving table metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving table metadata: %s", e)
            raise

    def get_table_info(
        self,
        table_name: str,
        database_name: Optional[str] = None,
        schema_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific table.

        Args:
            table_name: Name of the table
            database_name: Optional database name
            schema_name: Optional schema name

        Returns:
            Dictionary containing table metadata or None if not found
        """
        conditions = ["TABLE_NAME = %s"]
        params = [table_name]

        if database_name:
            conditions.append("TABLE_CATALOG = %s")
            params.append(database_name)
        if schema_name:
            conditions.append("TABLE_SCHEMA = %s")
            params.append(schema_name)

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            TABLE_CATALOG AS DATABASE_NAME,
            TABLE_SCHEMA AS SCHEMA_NAME,
            TABLE_NAME,
            TABLE_TYPE,
            IS_TRANSIENT,
            CLUSTERING_KEY,
            ROW_COUNT,
            BYTES,
            RETENTION_TIME,
            CREATED,
            LAST_ALTERED,
            AUTO_CLUSTERING_ON,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.TABLES
        WHERE {where_clause}
        """

        try:
            logger.info("Retrieving metadata for table: %s", table_name)
            results = self.connection.execute_query_dict(query, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error("Error retrieving table metadata for %s: %s", table_name, e)
            raise

    def get_views(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about views.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing view metadata
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
            TABLE_NAME AS VIEW_NAME,
            VIEW_DEFINITION,
            IS_SECURE,
            IS_MATERIALIZED,
            CREATED,
            LAST_ALTERED,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.VIEWS
        WHERE {where_clause}
        ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
        """

        try:
            logger.info("Retrieving view metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving view metadata: %s", e)
            raise

    # =========================================================================
    # Column Metadata
    # =========================================================================

    def get_columns(
        self,
        table_name: Optional[str] = None,
        database_name: Optional[str] = None,
        schema_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get metadata about columns.

        Args:
            table_name: Optional table name to filter
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            List of dictionaries containing column metadata
        """
        conditions = []
        params = []

        if table_name:
            conditions.append("TABLE_NAME = %s")
            params.append(table_name)
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
            TABLE_NAME,
            COLUMN_NAME,
            ORDINAL_POSITION,
            COLUMN_DEFAULT,
            IS_NULLABLE,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            IS_IDENTITY,
            IDENTITY_START,
            IDENTITY_INCREMENT,
            COMMENT
        FROM SNOWFLAKE.INFORMATION_SCHEMA.COLUMNS
        WHERE {where_clause}
        ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
        """

        try:
            logger.info("Retrieving column metadata")
            return self.connection.execute_query_dict(
                query, tuple(params) if params else None
            )
        except Exception as e:
            logger.error("Error retrieving column metadata: %s", e)
            raise

    # =========================================================================
    # Comprehensive Table Metadata
    # =========================================================================

    def get_all_table_metadata(
        self, database_name: Optional[str] = None, schema_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive metadata about all tables, views, and columns.

        Args:
            database_name: Optional database name to filter
            schema_name: Optional schema name to filter

        Returns:
            Dictionary containing all table-related metadata organized by type
        """
        logger.info("Retrieving comprehensive table metadata")

        metadata = {
            "tables": self.get_tables(database_name, schema_name, include_views=False),
            "views": self.get_views(database_name, schema_name),
            "columns": self.get_columns(None, database_name, schema_name),
        }

        # Add summary counts
        metadata["summary"] = {
            "table_count": len(metadata["tables"]),
            "view_count": len(metadata["views"]),
            "column_count": len(metadata["columns"]),
        }

        logger.info("Successfully retrieved comprehensive table metadata")
        return metadata
