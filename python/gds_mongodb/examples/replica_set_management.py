"""
Example usage of MongoDB Replica Set Management.

This module demonstrates how to use the MongoDBReplicaSetManager class to
manage MongoDB replica sets, including adding and removing members, getting
status and configuration, and monitoring replica set health.
"""

from gds_mongodb import MongoDBConnection, MongoDBReplicaSetManager


def example_basic_status():
    """Example: Get replica set status and configuration."""
    print("=" * 70)
    print("Example 1: Getting Replica Set Status and Configuration")
    print("=" * 70)

    # Connect to a replica set member
    # Note: Connect to the admin database for replica set operations
    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
        replica_set="myReplicaSet",
    )

    try:
        conn.connect()

        # Create replica set manager
        rs_manager = MongoDBReplicaSetManager(conn)

        # Get replica set status
        print("\nReplica Set Status:")
        status = rs_manager.get_status()
        print(f"  Replica set name: {status['set']}")
        print(f"  My state: {status['myState']}")
        print(f"  Number of members: {len(status['members'])}")

        print("\nMembers:")
        for member in status["members"]:
            print(f"  - {member['name']}: {member['stateStr']}")
            print(f"    Health: {member.get('health', 'unknown')}")
            print(f"    Uptime: {member.get('uptime', 'unknown')} seconds")

        # Get replica set configuration
        print("\nReplica Set Configuration:")
        config = rs_manager.get_config()
        print(f"  Config version: {config['version']}")
        print(f"  Replica set name: {config['_id']}")

        print("\nConfigured Members:")
        for member in config["members"]:
            print(f"  - ID {member['_id']}: {member['host']}")
            print(f"    Priority: {member.get('priority', 1)}")
            print(f"    Votes: {member.get('votes', 1)}")
            if member.get("arbiterOnly"):
                print("    Role: Arbiter")
            if member.get("hidden"):
                print("    Hidden: Yes")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_member_management():
    """Example: Add and remove replica set members."""
    print("=" * 70)
    print("Example 2: Adding and Removing Replica Set Members")
    print("=" * 70)

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
        replica_set="myReplicaSet",
    )

    try:
        conn.connect()
        rs_manager = MongoDBReplicaSetManager(conn)  # noqa: F841

        # Add a new regular member
        print("\nAdding a new member...")
        print("  Host: replica4.example.com:27017")
        # Note: Uncomment the following line to actually add a member
        # rs_manager.add_member('replica4.example.com:27017')
        print("  (Commented out to prevent actual changes)")

        # Add a member with custom priority
        print("\nAdding a priority 0 member (cannot become primary)...")
        print("  Host: replica5.example.com:27017")
        print("  Priority: 0")
        # Note: Uncomment the following line to actually add a member
        # rs_manager.add_member('replica5.example.com:27017', priority=0)
        print("  (Commented out to prevent actual changes)")

        # Add an arbiter
        print("\nAdding an arbiter (no data, voting only)...")
        print("  Host: arbiter1.example.com:27017")
        # Note: Uncomment the following line to actually add a member
        # rs_manager.add_member(
        #     'arbiter1.example.com:27017',
        #     arbiter_only=True
        # )
        print("  (Commented out to prevent actual changes)")

        # Add a hidden member with delayed replication (for backups)
        print("\nAdding a hidden, delayed member (for point-in-time backups)...")
        print("  Host: backup.example.com:27017")
        print("  Hidden: Yes")
        print("  Slave delay: 3600 seconds (1 hour)")
        print("  Priority: 0 (auto-set for hidden/delayed members)")
        # Note: Uncomment the following lines to actually add a member
        # rs_manager.add_member(
        #     'backup.example.com:27017',
        #     hidden=True,
        #     slave_delay=3600,
        #     priority=0
        # )
        print("  (Commented out to prevent actual changes)")

        # Remove a member
        print("\nRemoving a member...")
        print("  Host: replica4.example.com:27017")
        # Note: Uncomment the following line to actually remove a member
        # rs_manager.remove_member('replica4.example.com:27017')
        print("  (Commented out to prevent actual changes)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_monitoring():
    """Example: Monitor replica set health and replication."""
    print("=" * 70)
    print("Example 3: Monitoring Replica Set Health and Replication")
    print("=" * 70)

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
        replica_set="myReplicaSet",
    )

    try:
        conn.connect()
        rs_manager = MongoDBReplicaSetManager(conn)

        # Get primary node
        print("\nPrimary Node:")
        primary = rs_manager.get_primary()
        if primary:
            print(f"  {primary}")
        else:
            print("  No primary available (election in progress?)")

        # Get secondary nodes
        print("\nSecondary Nodes:")
        secondaries = rs_manager.get_secondaries()
        if secondaries:
            for secondary in secondaries:
                print(f"  - {secondary}")
        else:
            print("  No secondaries available")

        # Get arbiters
        print("\nArbiters:")
        arbiters = rs_manager.get_arbiters()
        if arbiters:
            for arbiter in arbiters:
                print(f"  - {arbiter}")
        else:
            print("  No arbiters configured")

        # Check member health
        print("\nMember Health:")
        health = rs_manager.get_member_health()
        for member, is_healthy in health.items():
            status = "✓ Healthy" if is_healthy else "✗ Unhealthy"
            print(f"  {member}: {status}")

        # Get member states
        print("\nMember States:")
        states = rs_manager.get_member_states()
        for member, state in states.items():
            print(f"  {member}: {state}")

        # Get replication lag
        print("\nReplication Lag:")
        lags = rs_manager.get_replication_lag()
        if lags:
            for member, lag_seconds in lags.items():
                if lag_seconds == 0:
                    print(f"  {member}: No lag (up to date)")
                elif lag_seconds < 10:
                    print(f"  {member}: {lag_seconds}s (minimal lag)")
                elif lag_seconds < 60:
                    print(f"  {member}: {lag_seconds}s (acceptable lag)")
                else:
                    print(f"  {member}: {lag_seconds}s ({lag_seconds // 60}m {lag_seconds % 60}s - significant lag!)")
        else:
            print("  No replication lag data available")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def example_advanced_operations():
    """Example: Advanced replica set operations."""
    print("=" * 70)
    print("Example 4: Advanced Replica Set Operations")
    print("=" * 70)

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="admin",
        username="admin",
        password="secret",
        replica_set="myReplicaSet",
    )

    try:
        conn.connect()
        rs_manager = MongoDBReplicaSetManager(conn)  # noqa: F841

        # Step down primary (for maintenance)
        print("\nStepping down primary for maintenance...")
        print("  Duration: 60 seconds")
        # Note: Uncomment the following line to actually step down
        # rs_manager.step_down(seconds=60)
        print("  (Commented out to prevent actual changes)")
        print("  This forces the primary to become a secondary and triggers an election")

        # Freeze a member (prevent it from becoming primary)
        print("\nFreezing a member to prevent election...")
        print("  Duration: 120 seconds")
        # Note: Uncomment the following line to actually freeze
        # rs_manager.freeze(120)
        print("  (Commented out to prevent actual changes)")
        print("  Useful during maintenance or when you want to control which")
        print("  member becomes primary during an election")

        # Unfreeze a member
        print("\nUnfreezing a member...")
        # Note: Uncomment the following line to actually unfreeze
        # rs_manager.freeze(0)
        print("  (Commented out to prevent actual changes)")

        # Reconfigure replica set (advanced)
        print("\nReconfiguring replica set...")
        print("  Example: Changing member priorities")
        # Note: This is an advanced operation - use with caution!
        # config = rs_manager.get_config()
        # config['version'] += 1
        # for member in config['members']:
        #     if member['host'] == 'replica1.example.com:27017':
        #         member['priority'] = 10  # Make this member preferred primary
        # rs_manager.reconfigure(config)
        print("  (Commented out to prevent actual changes)")
        print("  WARNING: Incorrect configuration can make replica set")
        print("  unavailable. Always test in non-production first!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()

    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MongoDB Replica Set Management Examples")
    print("=" * 70)
    print()

    # Note: These examples require a running MongoDB replica set
    # To run these examples:
    # 1. Set up a MongoDB replica set (or use Docker Compose)
    # 2. Update connection parameters (host, username, password, etc.)
    # 3. Uncomment the actual operation calls in each example
    # 4. Run this script

    print("NOTE: This example connects to a MongoDB replica set.")
    print("      Update connection parameters before running.")
    print("      Most operations are commented out to prevent accidental")
    print("      changes to your replica set.")
    print()

    try:
        # Run examples
        example_basic_status()
        example_member_management()
        example_monitoring()
        example_advanced_operations()

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("  1. A running MongoDB replica set")
        print("  2. Correct connection parameters")
        print("  3. Appropriate user permissions (dbAdminAnyDatabase or clusterAdmin)")

    print("\n" + "=" * 70)
    print("Examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
