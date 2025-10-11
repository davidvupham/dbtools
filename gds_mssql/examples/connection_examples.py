"""
Example usage of the gds_mssql package.

This example demonstrates various ways to use the Microsoft SQL Server connection
class including basic connections with username/password and Kerberos authentication,
transactions, and metadata queries.
"""

import logging

from gds_mssql import MSSQLConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def basic_connection_example():
    """Basic connection and query example with username/password."""
    print("=== Basic Connection Example (Username/Password) ===")

    # Create connection with individual parameters
    conn = MSSQLConnection(
        server="localhost",
        port=1433,
        database="testdb",
        user="testuser",
        password="testpass",
    )

    try:
        # Connect to database
        conn.connect()
        print(f"Connected to: {conn.get_connection_info()}")

        # Execute a simple query
        results = conn.execute_query("SELECT @@VERSION")
        print(f"SQL Server version: {results[0][0]}")

        # Execute query with parameters
        user_results = conn.execute_query("SELECT * FROM users WHERE age > ?", (25,))
        print(f"Found {len(user_results)} users over 25")

    finally:
        conn.disconnect()


def kerberos_connection_example():
    """Connection example using Kerberos authentication."""
    print("=== Kerberos Connection Example ===")

    # Create connection with Kerberos authentication
    conn = MSSQLConnection(
        server="sqlserver.domain.com",
        database="production_db",
        authentication="kerberos",
    )

    try:
        # Connect to database
        conn.connect()
        print(f"Connected to: {conn.get_connection_info()}")

        # Execute a simple query
        results = conn.execute_query("SELECT @@VERSION")
        print(f"SQL Server version: {results[0][0]}")

    finally:
        conn.disconnect()


def config_dict_example():
    """Connection example using configuration dictionary."""
    print("=== Configuration Dictionary Example ===")

    # Configuration dictionary
    config = {
        "server": "localhost",
        "database": "testdb",
        "user": "testuser",
        "password": "testpass",
        "driver": "ODBC Driver 18 for SQL Server",
        "connection_timeout": 30,
    }

    conn = MSSQLConnection(config=config)

    try:
        conn.connect()
        print(f"Connected to: {conn.get_connection_info()}")

        # Get database metadata
        tables = conn.get_table_names()
        print(f"Tables in database: {tables}")

        if tables:
            # Get column info for first table
            columns = conn.get_column_info(tables[0])
            print(f"Columns in {tables[0]}: {[col['COLUMN_NAME'] for col in columns]}")

    finally:
        conn.disconnect()


def transaction_example():
    """Transaction management example."""
    print("=== Transaction Example ===")

    conn = MSSQLConnection(
        server="localhost", database="testdb", user="testuser", password="testpass"
    )

    try:
        conn.connect()

        # Start transaction
        conn.begin_transaction()

        try:
            # Execute multiple operations
            conn.execute_query(
                "INSERT INTO users (name, age) VALUES (?, ?)", ("John Doe", 30)
            )
            conn.execute_query(
                "INSERT INTO users (name, age) VALUES (?, ?)", ("Jane Smith", 25)
            )

            # Commit transaction
            conn.commit()
            print("Transaction committed successfully")

        except Exception as e:
            # Rollback on error
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")

    finally:
        conn.disconnect()


def context_manager_example():
    """Context manager usage example."""
    print("=== Context Manager Example ===")

    with MSSQLConnection(
        server="localhost", database="testdb", user="testuser", password="testpass"
    ) as conn:
        print("Connected using context manager")

        # Execute query
        results = conn.execute_query("SELECT COUNT(*) FROM users")
        print(f"Total users: {results[0][0]}")

    print("Connection automatically closed")


def dict_results_example():
    """Example of getting results as dictionaries."""
    print("=== Dictionary Results Example ===")

    conn = MSSQLConnection(
        server="localhost", database="testdb", user="testuser", password="testpass"
    )

    try:
        conn.connect()

        # Get results as dictionaries
        users = conn.execute_query_dict("SELECT TOP 5 * FROM users")
        print("Users as dictionaries:")
        for user in users:
            print(f"  {user}")

    finally:
        conn.disconnect()


if __name__ == "__main__":
    print("GDS MSSQL Examples")
    print("==================")
    print()

    # Run examples (comment out ones that require actual database)
    # basic_connection_example()
    # kerberos_connection_example()
    # config_dict_example()
    # transaction_example()
    # context_manager_example()
    # dict_results_example()

    print(
        "Examples completed. Uncomment the functions above to run them with an actual SQL Server instance."
    )
