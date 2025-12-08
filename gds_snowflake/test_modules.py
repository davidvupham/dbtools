#!/usr/bin/env python3
"""
Test script to validate the gds_snowflake package structure and imports
"""


def test_imports():
    """Test that all modules can be imported"""
    print("Testing package imports...")

    try:
        from gds_snowflake import SnowflakeConnection

        print("✓ gds_snowflake.SnowflakeConnection imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SnowflakeConnection: {e}")
        return False

    try:
        from gds_snowflake import FailoverGroup, SnowflakeReplication

        print("✓ gds_snowflake.SnowflakeReplication and FailoverGroup imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SnowflakeReplication/FailoverGroup: {e}")
        return False

    try:
        import gds_snowflake

        print(f"✓ gds_snowflake package imported (version: {gds_snowflake.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import gds_snowflake package: {e}")
        return False

    return True


def test_class_instantiation():
    """Test that classes can be instantiated"""
    print("\nTesting class instantiation...")

    try:
        from gds_snowflake import SnowflakeConnection

        # Test creating a connection object (without actually connecting)
        SnowflakeConnection(
            account="test_account", user="test_user", vault_secret_path="data/snowflake", vault_mount_point="secret"
        )
        print("✓ SnowflakeConnection object created successfully")

    except Exception as e:
        print(f"✗ Failed to create SnowflakeConnection: {e}")
        return False

    try:
        from gds_snowflake import FailoverGroup

        # Test creating a failover group object
        fg = FailoverGroup(
            "test_fg",
            {
                "type": "PRIMARY",
                "primary": "TEST_ACCOUNT",
                "secondary_state": "TEST_ACCOUNT2:READY",
                "replication_schedule": "USING CRON */10 * * * * UTC",
            },
        )
        print("✓ FailoverGroup object created successfully")
        print(f"  - Name: {fg.name}")
        print(f"  - Type: {fg.type}")
        print(f"  - Primary: {fg.primary_account}")
        print(f"  - Schedule: {fg.replication_schedule}")

    except Exception as e:
        print(f"✗ Failed to create FailoverGroup: {e}")
        return False

    return True


def test_module_structure():
    """Test that modules have expected functions and classes"""
    print("\nTesting module structure...")

    try:
        from gds_snowflake import SnowflakeConnection

        # Check for expected methods
        expected_methods = [
            "connect",
            "close",
            "get_connection",
            "execute_query",
            "execute_query_dict",
            "switch_account",
        ]

        for method in expected_methods:
            if not hasattr(SnowflakeConnection, method):
                print(f"✗ SnowflakeConnection missing method: {method}")
                return False

        print("✓ SnowflakeConnection has all expected methods")

    except Exception as e:
        print(f"✗ Error checking SnowflakeConnection structure: {e}")
        return False

    try:
        from gds_snowflake import FailoverGroup, SnowflakeReplication

        # Check FailoverGroup methods
        expected_fg_methods = ["is_primary", "get_secondary_account"]

        for method in expected_fg_methods:
            if not hasattr(FailoverGroup, method):
                print(f"✗ FailoverGroup missing method: {method}")
                return False

        print("✓ FailoverGroup has all expected methods")

        # Check SnowflakeReplication methods
        expected_repl_methods = [
            "get_failover_groups",
            "get_replication_history",
            "parse_cron_schedule",
            "check_replication_failure",
            "check_replication_latency",
            "switch_to_secondary_account",
        ]

        for method in expected_repl_methods:
            if not hasattr(SnowflakeReplication, method):
                print(f"✗ SnowflakeReplication missing method: {method}")
                return False

        print("✓ SnowflakeReplication has all expected methods")

    except Exception as e:
        print(f"✗ Error checking snowflake_replication structure: {e}")
        return False

    return True


def test_failover_group_logic():
    """Test FailoverGroup logic"""
    print("\nTesting FailoverGroup logic...")

    try:
        from gds_snowflake import FailoverGroup

        # Create a test failover group
        fg = FailoverGroup(
            "TEST_FG",
            {
                "type": "PRIMARY",
                "primary": "ACCOUNT1.US-WEST-2",
                "secondary_state": "ACCOUNT2.US-EAST-1:READY, ACCOUNT3.EU-WEST-1:READY",
                "replication_schedule": "USING CRON */15 * * * * UTC",
                "next_scheduled_refresh": "2025-10-02 11:00:00",
            },
        )

        # Test is_primary
        assert fg.is_primary("ACCOUNT1"), "Should be primary for ACCOUNT1"
        assert fg.is_primary("ACCOUNT1.US-WEST-2"), "Should be primary for ACCOUNT1.US-WEST-2"
        assert not fg.is_primary("ACCOUNT2"), "Should not be primary for ACCOUNT2"
        print("✓ is_primary() works correctly")

        # Test get_secondary_account
        secondary = fg.get_secondary_account("ACCOUNT1")
        assert secondary is not None, "Should find secondary account"
        print(f"✓ get_secondary_account() returns: {secondary}")

        # Test secondary account parsing
        assert len(fg.secondary_accounts) == 2, "Should find 2 secondary accounts"
        print(f"✓ Secondary accounts parsed: {fg.secondary_accounts}")

    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing FailoverGroup logic: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Module Structure Validation")
    print("=" * 60)

    all_passed = True

    if not test_imports():
        all_passed = False

    if not test_class_instantiation():
        all_passed = False

    if not test_module_structure():
        all_passed = False

    if not test_failover_group_logic():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    print("✗ Some tests failed")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
