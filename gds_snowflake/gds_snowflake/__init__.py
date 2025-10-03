"""
GDS Snowflake Package

A Python package for managing Snowflake database connections, replication
monitoring, and database/table metadata retrieval.

This package provides:
- SnowflakeConnection: Robust connection management with auto-reconnection
- SnowflakeReplication: Replication monitoring and failover group management
- SnowflakeDatabase: Database-level metadata retrieval (databases, schemas,
                     functions, procedures, stages, pipes, tasks, streams)
- SnowflakeTable: Table-level metadata retrieval (tables, views, columns)
- FailoverGroup: Data class for failover group representation

Example:
    >>> from gds_snowflake import SnowflakeConnection
    >>> from gds_snowflake import SnowflakeDatabase, SnowflakeTable
    >>> conn = SnowflakeConnection(account='myaccount', user='myuser')
    >>> conn.connect()
    >>> db_meta = SnowflakeDatabase(conn)
    >>> databases = db_meta.get_databases()
    >>> tbl_meta = SnowflakeTable(conn)
    >>> tables = tbl_meta.get_tables(database_name='MYDB')
"""

from gds_snowflake.connection import SnowflakeConnection
from gds_snowflake.replication import SnowflakeReplication, FailoverGroup
from gds_snowflake.database import SnowflakeDatabase
from gds_snowflake.table import SnowflakeTable

__version__ = "1.0.0"
__author__ = "GDS Team"
__all__ = [
    "SnowflakeConnection",
    "SnowflakeReplication",
    "FailoverGroup",
    "SnowflakeDatabase",
    "SnowflakeTable",
]
