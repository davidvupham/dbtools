"""
GDS MSSQL - Microsoft SQL Server Database Connection Library

This package provides a Microsoft SQL Server implementation of the gds-database
interface, offering a comprehensive connection library for SQL Server
databases with username/password and Kerberos authentication support.

Classes:
    MSSQLConnection: Main SQL Server connection implementation

Usage:
    from gds_mssql import MSSQLConnection

    # Basic connection with username/password
    conn = MSSQLConnection(
        server='localhost',
        database='mydb',
        user='myuser',
        password='mypass'
    )

    # Kerberos authentication
    conn = MSSQLConnection(
        server='localhost',
        database='mydb',
        authentication='kerberos'
    )

    # Context manager usage
    with MSSQLConnection(server='localhost', database='mydb') as conn:
        results = conn.execute_query("SELECT * FROM users")
"""

from .connection import MSSQLConnection

__version__ = "1.0.0"
__all__ = [
    "MSSQLConnection",
]
