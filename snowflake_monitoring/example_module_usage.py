#!/usr/bin/env python3
"""
Example: Using GDS Snowflake Package

This example demonstrates how to use the gds_snowflake package
in your own scripts.
"""

import os

from gds_snowflake import SnowflakeConnection, SnowflakeReplication


def example_basic_usage():
    """Example: Basic connection and failover group retrieval"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Create connection (using environment variables for Vault config)
    conn = SnowflakeConnection(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "myaccount"),
        user=os.getenv("SNOWFLAKE_USER", "myuser"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    try:
        # Connect to Snowflake
        conn.connect()
        print("✓ Connected to Snowflake")

        # Create replication handler
        replication = SnowflakeReplication(conn)

        # Get all failover groups
        failover_groups = replication.get_failover_groups()
        print(f"✓ Found {len(failover_groups)} failover groups")

        # Display information about each failover group
        for fg in failover_groups:
            print(f"\nFailover Group: {fg.name}")
            print(f"  Type: {fg.type}")
            print(f"  Primary: {fg.primary_account}")
            print(f"  Schedule: {fg.replication_schedule}")
            print(f"  Next Refresh: {fg.next_scheduled_refresh}")

    finally:
        conn.close()
        print("\n✓ Connection closed")


def example_check_replication_status():
    """Example: Check replication status for all failover groups"""
    print("\n" + "=" * 60)
    print("Example 2: Check Replication Status")
    print("=" * 60)

    # Using context manager for automatic connection cleanup (env vars for Vault)
    with SnowflakeConnection(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "myaccount"), user=os.getenv("SNOWFLAKE_USER", "myuser")
    ) as conn:
        replication = SnowflakeReplication(conn)
        failover_groups = replication.get_failover_groups()

        for fg in failover_groups:
            print(f"\nChecking: {fg.name}")

            # Check for failures
            is_failed, error_msg = replication.check_replication_failure(fg)
            if is_failed:
                print(f"  ✗ FAILED: {error_msg}")
            else:
                print("  ✓ Status: OK")

            # Check for latency
            has_latency, latency_msg = replication.check_replication_latency(fg)
            if has_latency:
                print(f"  ⚠ LATENCY: {latency_msg}")
            else:
                print("  ✓ Latency: OK")


def example_query_replication_history():
    """Example: Query replication history for a specific failover group"""
    print("\n" + "=" * 60)
    print("Example 3: Query Replication History")
    print("=" * 60)

    conn = SnowflakeConnection(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "myaccount"), user=os.getenv("SNOWFLAKE_USER", "myuser")
    )

    try:
        conn.connect()
        replication = SnowflakeReplication(conn)

        # Get first failover group
        failover_groups = replication.get_failover_groups()
        if failover_groups:
            fg = failover_groups[0]
            print(f"Querying history for: {fg.name}")

            # Get replication history
            history = replication.get_replication_history(fg.name, limit=5)

            print(f"\nLast {len(history)} replication runs:")
            for i, run in enumerate(history, 1):
                print(f"\n  Run {i}:")
                print(f"    Start: {run.get('START_TIME')}")
                print(f"    End: {run.get('END_TIME')}")
                print(f"    Status: {run.get('STATUS')}")
                if run.get("MESSAGE"):
                    print(f"    Message: {run.get('MESSAGE')}")
        else:
            print("No failover groups found")

    finally:
        conn.close()


def example_parse_cron_schedule():
    """Example: Parse cron schedules"""
    print("\n" + "=" * 60)
    print("Example 4: Parse Cron Schedules")
    print("=" * 60)

    conn = SnowflakeConnection(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "myaccount"), user=os.getenv("SNOWFLAKE_USER", "myuser")
    )

    try:
        conn.connect()
        replication = SnowflakeReplication(conn)

        # Example cron schedules
        test_schedules = [
            "USING CRON */10 * * * * UTC",  # Every 10 minutes
            "USING CRON */30 * * * * UTC",  # Every 30 minutes
            "USING CRON 0 * * * * UTC",  # Every hour
        ]

        for schedule in test_schedules:
            interval = replication.parse_cron_schedule(schedule)
            print(f"\nSchedule: {schedule}")
            print(f"Interval: {interval} minutes")

    finally:
        conn.close()


def example_execute_custom_query():
    """Example: Execute custom SQL queries"""
    print("\n" + "=" * 60)
    print("Example 5: Execute Custom Queries")
    print("=" * 60)

    with SnowflakeConnection(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "myaccount"), user=os.getenv("SNOWFLAKE_USER", "myuser")
    ) as conn:
        # Execute a simple query
        print("\nExecuting: SELECT CURRENT_VERSION()")
        results = conn.execute_query("SELECT CURRENT_VERSION()")
        print(f"Snowflake Version: {results[0][0]}")

        # Execute query and get results as dictionaries
        print("\nExecuting: SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
        results = conn.execute_query_dict(
            "SELECT CURRENT_ACCOUNT() as ACCOUNT, CURRENT_USER() as USER, CURRENT_ROLE() as ROLE"
        )
        for row in results:
            print(f"Account: {row['ACCOUNT']}")
            print(f"User: {row['USER']}")
            print(f"Role: {row['ROLE']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Snowflake Replication Module Examples")
    print("=" * 60)
    print("\nNote: Set these environment variables before running:")
    print("  - SNOWFLAKE_ACCOUNT")
    print("  - SNOWFLAKE_USER")
    print("  - SNOWFLAKE_WAREHOUSE (optional)")
    print("  - SNOWFLAKE_ROLE (optional)")
    print("\nVault configuration (for RSA key authentication):")
    print("  - VAULT_ADDR")
    print("  - VAULT_SECRET_PATH")
    print("  - VAULT_MOUNT_POINT")
    print("  - VAULT_ROLE_ID (optional)")
    print("  - VAULT_SECRET_ID (optional)")
    print("  - VAULT_NAMESPACE (optional)")

    try:
        # Run examples
        # Uncomment the examples you want to run

        # example_basic_usage()
        # example_check_replication_status()
        # example_query_replication_history()
        # example_parse_cron_schedule()
        # example_execute_custom_query()

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
