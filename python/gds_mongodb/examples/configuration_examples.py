"""
Configuration example for MongoDB connection.

This example demonstrates various ways to configure
the MongoDB connection.
"""

from gds_mongodb import MongoDBConnection


def example_individual_parameters():
    """Connect using individual parameters."""
    print("1. Connection with individual parameters:")

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        auth_source="admin",
    )

    with conn:
        info = conn.get_connection_info()
        print(f"   Connected to: {info['host']}:{info['port']}")
        print(f"   Database: {info['database']}\n")


def example_connection_string():
    """Connect using connection string."""
    print("2. Connection with connection string:")

    conn = MongoDBConnection(
        connection_string="mongodb://myuser:mypassword@localhost:27017/",
        database="mydb",
    )

    with conn:
        info = conn.get_connection_info()
        print(f"   Connected: {info['connected']}")
        print(f"   Database: {info['database']}\n")


def example_config_dictionary():
    """Connect using configuration dictionary."""
    print("3. Connection with configuration dictionary:")

    config = {
        "host": "localhost",
        "port": 27017,
        "database": "mydb",
        "username": "myuser",
        "password": "mypassword",
        "auth_source": "admin",
        "server_selection_timeout_ms": 5000,
    }

    conn = MongoDBConnection(config=config)

    with conn:
        info = conn.get_connection_info()
        print(f"   Database: {info['database']}")
        print(f"   Auth Source: {info['auth_source']}\n")


def example_replica_set():
    """Connect to replica set."""
    print("4. Connection to replica set:")

    conn = MongoDBConnection(
        host="replica1.example.com",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        replica_set="myReplicaSet",
        auth_source="admin",
    )

    print(f"   Configured for replica set: {conn.config['replica_set']}\n")


def example_tls_connection():
    """Connect with TLS/SSL."""
    print("5. Connection with TLS/SSL:")

    conn = MongoDBConnection(
        host="secure.example.com",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        tls=True,
        auth_source="admin",
    )

    print(f"   TLS enabled: {conn.config.get('tls', False)}\n")


def example_connection_pooling():
    """Connect with custom connection pool settings."""
    print("6. Connection with custom pool settings:")

    config = {
        "host": "localhost",
        "port": 27017,
        "database": "mydb",
        "username": "myuser",
        "password": "mypassword",
        "maxPoolSize": 50,
        "minPoolSize": 10,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 10000,
        "serverSelectionTimeoutMS": 5000,
    }

    conn = MongoDBConnection(config=config)

    print(f"   Max pool size: {conn.config.get('maxPoolSize')}")
    print(f"   Min pool size: {conn.config.get('minPoolSize')}\n")


def example_no_authentication():
    """Connect without authentication (for local development)."""
    print("7. Connection without authentication:")

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="mydb",
    )

    with conn:
        info = conn.get_connection_info()
        print(f"   Connected to: {info['host']}:{info['port']}")
        print(f"   Database: {info['database']}")
        print(f"   Username: {info.get('username', 'None')}\n")


def main():
    """Run all configuration examples."""
    print("=== MongoDB Configuration Examples ===\n")

    # Note: These examples show configuration patterns
    # Actual connections will fail without a running MongoDB server

    try:
        example_individual_parameters()
    except Exception as e:
        print(f"   Error: {e}\n")

    try:
        example_connection_string()
    except Exception as e:
        print(f"   Error: {e}\n")

    try:
        example_config_dictionary()
    except Exception as e:
        print(f"   Error: {e}\n")

    example_replica_set()
    example_tls_connection()
    example_connection_pooling()

    try:
        example_no_authentication()
    except Exception as e:
        print(f"   Error: {e}\n")

    print("=== Examples Complete ===")


if __name__ == "__main__":
    main()
