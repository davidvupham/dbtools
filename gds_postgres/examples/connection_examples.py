"""
Example usage of the gds_postgres package.

This example demonstrates various ways to use the PostgreSQL connection
class including basic connections, transactions, and metadata queries.
"""

import logging
from gds_postgres import PostgreSQLConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def basic_connection_example():
    """Basic connection and query example."""
    print("=== Basic Connection Example ===")
    
    # Create connection with individual parameters
    conn = PostgreSQLConnection(
        host='localhost',
        port=5432,
        database='testdb',
        user='testuser',
        password='testpass'
    )
    
    try:
        # Connect to database
        conn.connect()
        print(f"Connected to: {conn.get_connection_info()}")
        
        # Execute a simple query
        results = conn.execute_query("SELECT version()")
        print(f"PostgreSQL version: {results[0][0]}")
        
        # Execute query with parameters
        user_results = conn.execute_query(
            "SELECT * FROM users WHERE age > %s",
            (25,)
        )
        print(f"Found {len(user_results)} users over 25")
        
    finally:
        conn.disconnect()


def connection_url_example():
    """Connection using URL example."""
    print("\n=== Connection URL Example ===")
    
    # Create connection using URL
    conn = PostgreSQLConnection(
        connection_url='postgresql://testuser:testpass@localhost:5432/testdb'
    )
    
    try:
        conn.connect()
        print("Connected using URL")
        
        # Get table names
        tables = conn.get_table_names()
        print(f"Available tables: {tables}")
        
    finally:
        conn.disconnect()


def context_manager_example():
    """Context manager usage example."""
    print("\n=== Context Manager Example ===")
    
    # Use as context manager for automatic resource management
    with PostgreSQLConnection(
        host='localhost',
        database='testdb',
        user='testuser',
        password='testpass'
    ) as conn:
        print("Connection automatically managed")
        
        # Execute query returning dictionaries
        users = conn.execute_query_dict("SELECT id, name, email FROM users LIMIT 5")
        
        for user in users:
            print(f"User: {user['name']} ({user['email']})")


def transaction_example():
    """Transaction management example."""
    print("\n=== Transaction Example ===")
    
    conn = PostgreSQLConnection(
        host='localhost',
        database='testdb',
        user='testuser',
        password='testpass',
        autocommit=False  # Enable transaction mode
    )
    
    try:
        conn.connect()
        
        # Begin transaction (implicit in psycopg2)
        conn.begin_transaction()
        
        # Execute multiple operations
        conn.execute_query(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ('John Doe', 'john@example.com')
        )
        
        conn.execute_query(
            "UPDATE users SET last_login = NOW() WHERE email = %s",
            ('john@example.com',)
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


def metadata_example():
    """Database metadata example."""
    print("\n=== Metadata Example ===")
    
    with PostgreSQLConnection(
        host='localhost',
        database='testdb',
        user='testuser',
        password='testpass'
    ) as conn:
        
        # Get all table names
        tables = conn.get_table_names()
        print(f"Tables in public schema: {tables}")
        
        # Get column information for each table
        for table in tables[:3]:  # Limit to first 3 tables
            print(f"\nColumns in {table}:")
            columns = conn.get_column_info(table)
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  {col['column_name']}: {col['data_type']} {nullable}")


def configuration_example():
    """Configuration management example."""
    print("\n=== Configuration Example ===")
    
    # Create connection with configuration dictionary
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'testdb',
        'user': 'testuser',
        'password': 'testpass',
        'connect_timeout': 30,
        'autocommit': True
    }
    
    conn = PostgreSQLConnection(config=config)
    
    # Update configuration
    conn.update_config({
        'connect_timeout': 60,
        'application_name': 'gds_postgres_example'
    })
    
    print(f"Connection timeout: {conn.get_config('connect_timeout')}")
    print(f"Application name: {conn.get_config('application_name')}")
    
    try:
        conn.connect()
        print("Connected with custom configuration")
        
        info = conn.get_connection_info()
        print(f"Connection info: {info}")
        
    finally:
        conn.disconnect()


def error_handling_example():
    """Error handling example."""
    print("\n=== Error Handling Example ===")
    
    # Example of handling connection errors
    try:
        conn = PostgreSQLConnection(
            host='nonexistent-host',
            database='testdb',
            user='testuser',
            password='testpass'
        )
        conn.connect()
        
    except Exception as e:
        print(f"Connection error handled: {e}")
    
    # Example of handling query errors
    conn = PostgreSQLConnection(
        host='localhost',
        database='testdb',
        user='testuser',
        password='testpass'
    )
    
    try:
        conn.connect()
        
        # This will cause a query error
        conn.execute_query("SELECT * FROM nonexistent_table")
        
    except Exception as e:
        print(f"Query error handled: {e}")
        
    finally:
        conn.disconnect()


if __name__ == '__main__':
    """
    Run all examples.
    
    Note: These examples assume you have a PostgreSQL database
    running with appropriate user and database created.
    
    To set up a test database:
    1. Install PostgreSQL
    2. Create database: createdb testdb
    3. Create user: createuser testuser
    4. Grant permissions: GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
    """
    
    print("GDS PostgreSQL Connection Examples")
    print("=" * 50)
    
    # Note: Comment out examples that require actual database connection
    # basic_connection_example()
    # connection_url_example()
    # context_manager_example()
    # transaction_example()
    # metadata_example()
    configuration_example()
    # error_handling_example()
    
    print("\nExamples completed!")
    print("\nTo run database examples:")
    print("1. Set up PostgreSQL database")
    print("2. Update connection parameters in examples")
    print("3. Uncomment desired example functions")