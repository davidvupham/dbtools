"""
GDS PostgreSQL - PostgreSQL Database Connection Library

This package provides a PostgreSQL implementation of the gds-database
interface, offering a comprehensive connection library for PostgreSQL
databases with connection pooling, transaction management, and more.

Classes:
    PostgreSQLConnection: Main PostgreSQL connection implementation

Usage:
    from gds_postgres import PostgreSQLConnection
    
    # Basic connection
    conn = PostgreSQLConnection(
        host='localhost',
        database='mydb',
        user='myuser',
        password='mypass'
    )
    
    # Using connection URL
    conn = PostgreSQLConnection(
        connection_url='postgresql://user:pass@localhost:5432/mydb'
    )
    
    # Context manager usage
    with PostgreSQLConnection(host='localhost', database='mydb') as conn:
        results = conn.execute_query("SELECT * FROM users")
"""

from .connection import PostgreSQLConnection

__version__ = "1.0.0"
__all__ = [
    "PostgreSQLConnection",
]
