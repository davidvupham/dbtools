"""
MongoDB configuration management example.

This example demonstrates how to use MongoDBConnectionConfig for
configuration management following OOP design principles, including
support for instance metadata (name, environment, tags, etc.).
"""

from gds_mongodb import (
    MongoDBConnection,
    MongoDBConnectionConfig,
)


def example_basic_config():
    """Basic configuration class usage."""
    print("1. Basic MongoDBConnectionConfig Usage:")
    print("-" * 50)

    # Create configuration
    config = MongoDBConnectionConfig(
        host="localhost",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        auth_mechanism="SCRAM-SHA-256",
    )

    print(f"   Config: {config}")
    print(f"   Host: {config.get_host()}")
    print(f"   Port: {config.get_port()}")
    print(f"   Database: {config.get_database()}")
    print(f"   Auth Mechanism: {config.get_auth_mechanism()}")
    print()


def example_config_from_dict():
    """Create configuration from dictionary."""
    print("2. Create Config from Dictionary:")
    print("-" * 50)

    config_dict = {
        "host": "mongo.example.com",
        "port": 27017,
        "database": "production_db",
        "username": "prod_user",
        "password": "prod_pass",
        "replica_set": "prod-rs",
        "tls": True,
        "maxPoolSize": 100,
    }

    config = MongoDBConnectionConfig.from_dict(config_dict)
    print(f"   Config: {config}")
    print(f"   TLS Enabled: {config.is_tls_enabled()}")
    print()


def example_config_reuse():
    """Demonstrate configuration reuse across connections."""
    print("3. Configuration Reuse:")
    print("-" * 50)

    # Create a single configuration
    config = MongoDBConnectionConfig(
        host="localhost",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypass",
    )

    print(f"   Created config: {config}")

    # Use the same config for multiple connections
    conn1 = MongoDBConnection(config=config)
    conn2 = MongoDBConnection(config=config)

    print(f"   Connection 1: {conn1.get_connection_info()['database']}")
    print(f"   Connection 2: {conn2.get_connection_info()['database']}")
    print("   Both connections share the same configuration")
    print()


def example_config_modification():
    """Demonstrate configuration modification."""
    print("4. Configuration Modification:")
    print("-" * 50)

    config = MongoDBConnectionConfig(
        host="localhost",
        database="mydb",
    )

    print(f"   Initial: {config.to_safe_dict()}")

    # Modify configuration
    config.set_config("maxPoolSize", 50)
    config.set_config("tls", True)

    print(f"   Modified: {config.to_safe_dict()}")
    print()


def example_config_cloning():
    """Demonstrate configuration cloning."""
    print("5. Configuration Cloning:")
    print("-" * 50)

    # Original config for database 1
    original = MongoDBConnectionConfig(
        host="localhost",
        port=27017,
        database="db1",
        username="user1",
        password="pass1",
    )

    # Clone for database 2 with different credentials
    clone = original.clone(
        database="db2",
        username="user2",
        password="pass2",
    )

    print(f"   Original: {original}")
    print(f"   Clone: {clone}")
    print("   Same host/port, different database/credentials")
    print()


def example_instance_config():
    """Demonstrate instance-specific configuration with metadata."""
    print("6. MongoDB Configuration with Instance Metadata:")
    print("-" * 50)

    # Production instance with metadata
    prod_config = MongoDBConnectionConfig(
        instance_name="production",
        environment="prod",
        description="Production MongoDB cluster",
        host="prod-mongo.example.com",
        port=27017,
        database="prod_db",
        username="prod_user",
        password="prod_pass",
        replica_set="prod-rs",
        tls=True,
        tags=["production", "critical", "replicated"],
        metadata={
            "cluster_size": 3,
            "region": "us-east-1",
            "backup_enabled": True,
        },
    )

    # Development instance with metadata
    dev_config = MongoDBConnectionConfig(
        instance_name="development",
        environment="dev",
        description="Local development MongoDB",
        host="localhost",
        port=27017,
        database="dev_db",
        tags=["development", "local"],
        metadata={
            "cluster_size": 1,
            "region": "local",
        },
    )

    print(f"   Production: {prod_config}")
    print(f"     Environment: {prod_config.get_environment()}")
    print(f"     Tags: {prod_config.get_tags()}")
    print(f"     Metadata: {prod_config.get_metadata()}")
    print()
    print(f"   Development: {dev_config}")
    print(f"     Environment: {dev_config.get_environment()}")
    print(f"     Tags: {dev_config.get_tags()}")
    print()


def example_multiple_instances():
    """Manage multiple MongoDB instances with metadata."""
    print("7. Managing Multiple Instances:")
    print("-" * 50)

    # Define multiple instances with metadata
    instances = {
        "prod": MongoDBConnectionConfig(
            instance_name="production",
            environment="prod",
            host="prod.example.com",
            database="mydb",
            username="prod_user",
            password="prod_pass",
            tls=True,
        ),
        "staging": MongoDBConnectionConfig(
            instance_name="staging",
            environment="staging",
            host="staging.example.com",
            database="mydb",
            username="staging_user",
            password="staging_pass",
        ),
        "dev": MongoDBConnectionConfig(
            instance_name="development",
            environment="dev",
            host="localhost",
            database="mydb_dev",
        ),
    }

    # List all instances
    print("   Available Instances:")
    for name, config in instances.items():
        print(f"     - {name}: {config}")

    # Select and use an instance
    selected = "dev"
    print(f"\n   Using instance: {selected}")
    conn = MongoDBConnection(config=instances[selected])
    info = conn.get_connection_info()
    print(f"     Connected to: {info['host']}:{info['port']}")
    print()


def example_connection_string_builder():
    """Demonstrate connection string building."""
    print("8. Connection String Building:")
    print("-" * 50)

    configs = [
        MongoDBConnectionConfig(host="localhost", database="mydb"),
        MongoDBConnectionConfig(
            host="localhost",
            database="mydb",
            username="user",
            password="pass",
        ),
        MongoDBConnectionConfig(
            host="localhost",
            database="mydb",
            username="user",
            password="pass",
            auth_mechanism="SCRAM-SHA-256",
            auth_source="admin",
        ),
        MongoDBConnectionConfig(
            host="kerberos.example.com",
            database="mydb",
            username="user@REALM",
            auth_mechanism="GSSAPI",
            auth_source="$external",
        ),
    ]

    for i, config in enumerate(configs, 1):
        conn_str = config.build_connection_string()
        print(f"   Config {i}: {conn_str}")
    print()


def example_safe_dict_export():
    """Demonstrate safe dictionary export (without passwords)."""
    print("9. Safe Configuration Export:")
    print("-" * 50)

    config = MongoDBConnectionConfig(
        host="localhost",
        database="mydb",
        username="myuser",
        password="super_secret_password",
        auth_mechanism="SCRAM-SHA-256",
    )

    print("   Full config (includes password):")
    print(f"     {config.to_dict()}")

    print("\n   Safe config (password removed):")
    print(f"     {config.to_safe_dict()}")
    print()


def main():
    """Run all configuration examples."""
    print("=" * 60)
    print("MongoDB Configuration Management Examples")
    print("=" * 60)
    print()

    example_basic_config()
    example_config_from_dict()
    example_config_reuse()
    example_config_modification()
    example_config_cloning()
    example_instance_config()
    example_multiple_instances()
    example_connection_string_builder()
    example_safe_dict_export()

    print("=" * 60)
    print("Benefits of Configuration Classes:")
    print("=" * 60)
    print("  1. Separation of Concerns")
    print("     - Configuration is separate from connection logic")
    print()
    print("  2. Reusability")
    print("     - Same config can be used for multiple connections")
    print()
    print("  3. Validation")
    print("     - Configuration is validated before use")
    print()
    print("  4. Type Safety")
    print("     - Strongly typed with clear interfaces")
    print()
    print("  5. Instance Management")
    print("     - Easy to manage multiple MongoDB instances")
    print()
    print("  6. Serialization")
    print("     - Easy to save/load configurations")
    print()
    print("  7. Security")
    print("     - Safe export without sensitive data")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
