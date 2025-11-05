"""
MongoDB Configuration Management Examples

This script demonstrates how to use the MongoDBConfiguration class
to retrieve and modify MongoDB server configuration settings.

Reference: https://www.mongodb.com/docs/manual/reference/command/getParameter/
"""

from gds_mongodb import (
    MongoDBConnection,
    MongoDBConnectionConfig,
    MongoDBConfiguration,
)
from pymongo.errors import PyMongoError


def example_basic_configuration_retrieval():
    """Example 1: Basic configuration retrieval"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Configuration Retrieval")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        # Create configuration manager
        config = MongoDBConfiguration(conn)

        # Get a single configuration setting
        log_level = config.get("logLevel")
        print(f"Log Level: {log_level}")

        # Get another configuration
        max_bson_size = config.get("maxBsonObjectSize")
        print(f"Max BSON Object Size: {max_bson_size} bytes")


def example_configuration_details():
    """Example 2: Get configuration details (with metadata)"""
    print("\n" + "=" * 70)
    print("Example 2: Configuration Details with Metadata")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get detailed information about a configuration
        details = config.get_details("maxBsonObjectSize")

        print(f"Configuration: {details['name']}")
        print(f"Value: {details['value']}")
        print(f"Can be set at runtime: {details.get('settable_at_runtime')}")
        print(f"Can be set at startup: {details.get('settable_at_startup')}")

        # Get details for another configuration
        log_details = config.get_details("logLevel")
        print("\nLog Level Configuration:")
        print(f"  Value: {log_details['value']}")
        print(f"  Runtime settable: {log_details.get('settable_at_runtime')}")


def example_all_configurations():
    """Example 3: Retrieve all configurations"""
    print("\n" + "=" * 70)
    print("Example 3: Retrieve All Configurations")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get all configurations (simple values only)
        all_settings = config.get_all()

        print(f"Total configurations: {len(all_settings)}")
        print("\nSample configurations:")
        for i, (name, value) in enumerate(list(all_settings.items())[:10]):
            print(f"  {name}: {value}")

        print("\n... (and {} more)".format(len(all_settings) - 10))


def example_all_configurations_with_details():
    """Example 4: Retrieve all configurations with details"""
    print("\n" + "=" * 70)
    print("Example 4: All Configurations with Details")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get all configurations with details
        all_detailed = config.get_all(include_details=True)

        print(f"Total configurations: {len(all_detailed)}")
        print("\nSample configurations with details:")
        for i, (name, details) in enumerate(list(all_detailed.items())[:5]):
            if isinstance(details, dict):
                value = details.get("value", details)
                runtime = details.get("settableAtRuntime", "N/A")
                startup = details.get("settableAtStartup", "N/A")
                print(f"\n{name}:")
                print(f"  Value: {value}")
                print(f"  Runtime: {runtime}, Startup: {startup}")
            else:
                print(f"\n{name}: {details}")


def example_all_configurations_list():
    """Example 5: Get all configurations as a list of detail dicts"""
    print("\n" + "=" * 70)
    print("Example 5: All Configurations as List")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get all configurations as list
        all_list = config.get_all_details()

        print(f"Total configurations: {len(all_list)}")
        print("\nFirst 5 configurations:")
        for setting in all_list[:5]:
            print(f"\n{setting['name']}: {setting['value']}")
            if setting.get("settable_at_runtime") is not None:
                print(
                    f"  Runtime: {setting.get('settable_at_runtime')}, "
                    f"Startup: {setting.get('settable_at_startup')}"
                )


def example_runtime_configurations():
    """Example 6: Get runtime-settable configurations"""
    print("\n" + "=" * 70)
    print("Example 6: Runtime-Settable Configurations")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        try:
            # Get configurations that can be changed at runtime
            runtime_settings = config.get_runtime_configurable()

            print(f"Runtime-settable configurations: {len(runtime_settings)}")
            print("\nFirst 10 runtime-settable configurations:")
            for i, (name, value) in enumerate(list(runtime_settings.items())[:10]):
                print(f"  {name}: {value}")

        except PyMongoError as e:
            print(f"Error: {e}")
            print("Your MongoDB version may not support this feature.")


def example_startup_configurations():
    """Example 7: Get startup-only configurations"""
    print("\n" + "=" * 70)
    print("Example 7: Startup-Only Configurations")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        try:
            # Get configurations that can only be set at startup
            startup_settings = config.get_startup_configurable()

            print(f"Startup-only configurations: {len(startup_settings)}")
            print("\nFirst 10 startup-only configurations:")
            for i, (name, value) in enumerate(list(startup_settings.items())[:10]):
                print(f"  {name}: {value}")

        except PyMongoError as e:
            print(f"Error: {e}")
            print("Your MongoDB version may not support this feature.")


def example_configurations_by_prefix():
    """Example 8: Get configurations by prefix"""
    print("\n" + "=" * 70)
    print("Example 8: Configurations by Prefix")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get all replication-related configurations
        repl_settings = config.get_by_prefix("repl")
        print(f"Replication configurations ({len(repl_settings)}):")
        for name, value in repl_settings.items():
            print(f"  {name}: {value}")

        print()

        # Get all network-related configurations
        net_settings = config.get_by_prefix("net")
        print(f"\nNetwork configurations ({len(net_settings)}):")
        for name, value in list(net_settings.items())[:5]:
            print(f"  {name}: {value}")


def example_search_configurations():
    """Example 9: Search configurations by keyword"""
    print("\n" + "=" * 70)
    print("Example 9: Search Configurations")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Search for configurations containing "log"
        log_settings = config.search("log")
        print(f"Configurations containing 'log' ({len(log_settings)}):")
        for name, value in log_settings.items():
            print(f"  {name}: {value}")

        print()

        # Search for configurations containing "timeout"
        timeout_settings = config.search("timeout", case_sensitive=False)
        print(f"\nConfigurations containing 'timeout' ({len(timeout_settings)}):")
        for name, value in timeout_settings.items():
            print(f"  {name}: {value}")


def example_set_configuration():
    """Example 10: Set a configuration value"""
    print("\n" + "=" * 70)
    print("Example 10: Set Configuration Value")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get current value
        current_value = config.get("logLevel")
        print(f"Current log level: {current_value}")

        # Check if it's runtime-settable
        details = config.get_details("logLevel")
        if details.get("settable_at_runtime"):
            print("Log level is runtime-settable")

            # Set new value (be careful in production!)
            print("\nSetting log level to 1 (verbose)...")
            try:
                result = config.set("logLevel", 1)
                print(f"Result: {result}")

                # Verify new value
                new_value = config.get("logLevel")
                print(f"New log level: {new_value}")

                # Reset to original value
                print(f"\nResetting to original value ({current_value})...")
                config.set("logLevel", current_value)
                print("Reset complete")

            except PyMongoError as e:
                print(f"Error setting configuration: {e}")
        else:
            print("Log level is not runtime-settable")


def example_set_multiple_configurations():
    """Example 11: Set multiple configurations at once"""
    print("\n" + "=" * 70)
    print("Example 11: Set Multiple Configurations")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Get current values
        log_level = config.get("logLevel")
        quiet = config.get("quiet")

        print("Current values:")
        print(f"  logLevel: {log_level}")
        print(f"  quiet: {quiet}")

        # Set multiple configurations
        settings = {"logLevel": 1, "quiet": 0}

        print("\nSetting multiple configurations...")
        try:
            result = config.set_multiple(settings, comment="Batch configuration update")
            print(f"Result: {result}")

            # Verify new values
            print("\nNew values:")
            print(f"  logLevel: {config.get('logLevel')}")
            print(f"  quiet: {config.get('quiet')}")

            # Reset to original values
            print("\nResetting to original values...")
            original = {"logLevel": log_level, "quiet": quiet}
            config.set_multiple(original)
            print("Reset complete")

        except PyMongoError as e:
            print(f"Error setting configurations: {e}")


def example_reset_configuration():
    """Example 12: Reset configuration to default"""
    print("\n" + "=" * 70)
    print("Example 12: Reset Configuration to Default")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Set a non-default value
        print("Setting logLevel to 2...")
        config.set("logLevel", 2)
        print(f"Current value: {config.get('logLevel')}")

        # Reset to default
        print("\nResetting to default...")
        if config.reset("logLevel"):
            print("Reset successful")
            print(f"New value: {config.get('logLevel')}")
        else:
            print("Reset failed or default unknown")


def example_to_dict():
    """Example 13: Export configurations as dictionary"""
    print("\n" + "=" * 70)
    print("Example 13: Export Configurations as Dictionary")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Export all configurations
        config_dict = config.to_dict()

        print(f"Total configurations: {len(config_dict)}")
        print("\nFirst 10 configurations:")
        for i, (name, value) in enumerate(list(config_dict.items())[:10]):
            print(f"  {name}: {value}")


def example_error_handling():
    """Example 14: Error handling"""
    print("\n" + "=" * 70)
    print("Example 14: Error Handling")
    print("=" * 70)

    cfg = MongoDBConnectionConfig(host="localhost", port=27017, database="admin")

    with MongoDBConnection(config=cfg) as conn:
        config = MongoDBConfiguration(conn)

        # Try to get non-existent configuration
        print("Trying to get non-existent configuration...")
        try:
            value = config.get("nonExistentConfig")
            print(f"Value: {value}")
        except PyMongoError as e:
            print(f"Error (expected): {e}")

        # Try to set startup-only configuration
        print("\nTrying to set startup-only configuration at runtime...")
        try:
            # Most MongoDB installations have storage.dbPath as startup-only
            config.set("storage.dbPath", "/new/path")
        except PyMongoError as e:
            print(f"Error (expected): {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MongoDB Configuration Management Examples")
    print("=" * 70)

    examples = [
        example_basic_configuration_retrieval,
        example_configuration_details,
        example_all_configurations,
        example_all_configurations_with_details,
        example_all_configurations_list,
        example_runtime_configurations,
        example_startup_configurations,
        example_configurations_by_prefix,
        example_search_configurations,
        example_set_configuration,
        example_set_multiple_configurations,
        example_reset_configuration,
        example_to_dict,
        example_error_handling,
    ]

    print("\nThis script demonstrates the MongoDBConfiguration class.")
    print("Examples will run sequentially...")
    print("\nPress Ctrl+C to cancel at any time.\n")

    try:
        for example_func in examples:
            example_func()
            print()
    except KeyboardInterrupt:
        print("\n\nExamples cancelled by user.")
    except Exception as e:
        print(f"\n\nError running examples: {e}")


if __name__ == "__main__":
    main()
