"""
Example usage of the SnowflakeAccount class.

This example demonstrates how to:
1. Connect to Snowflake
2. Retrieve account information
3. Save account data to JSON
4. Load account data from JSON
5. Generate account summaries
"""

import os
from gds_snowflake import SnowflakeConnection, SnowflakeAccount


def main():
    """Main example function."""

    # Set data directory (optional - can also use GDS_DATA_DIR env var)
    data_dir = os.getenv("GDS_DATA_DIR", "./data")

    # Connect to Snowflake
    # Requires VAULT_* environment variables to be set for authentication
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="data/snowflake",
        vault_mount_point="secret",
    )

    try:
        conn.connect()
        print("Connected to Snowflake successfully!")

        # Create account manager
        account_mgr = SnowflakeAccount(conn, data_dir=data_dir)

        # Example 1: Get current account information
        print("\n" + "=" * 80)
        print("Example 1: Current Account Information")
        print("=" * 80)
        current_account = account_mgr.get_current_account()
        print(f"Account Name: {current_account.account_name}")
        print(f"Organization: {current_account.organization_name}")
        print(f"Region: {current_account.region}")

        # Example 2: Get all accounts in organization
        print("\n" + "=" * 80)
        print("Example 2: All Accounts in Organization")
        print("=" * 80)
        try:
            accounts = account_mgr.get_all_accounts()
            print(f"Found {len(accounts)} accounts:")
            for account in accounts:
                current_marker = " (CURRENT)" if account.is_current else ""
                print(
                    f"  - {account.account_name}: "
                    f"{account.region} / {account.cloud_provider} / "
                    f"{account.account_edition}{current_marker}"
                )
        except Exception as e:
            print(
                "Note: Could not retrieve all accounts. This may require organization admin privileges."
            )
            print(f"Error: {e}")
            # Use current account only for demonstration
            accounts = [current_account]

        # Example 3: Save accounts to JSON
        print("\n" + "=" * 80)
        print("Example 3: Save Accounts to JSON")
        print("=" * 80)
        filepath = account_mgr.save_accounts_to_json(accounts)
        print(f"Saved account data to: {filepath}")

        # Example 4: Load accounts from JSON
        print("\n" + "=" * 80)
        print("Example 4: Load Accounts from JSON")
        print("=" * 80)
        loaded_accounts = account_mgr.load_accounts_from_json(filepath.name)
        print(f"Loaded {len(loaded_accounts)} accounts from {filepath.name}")

        # Example 5: Generate account summary
        print("\n" + "=" * 80)
        print("Example 5: Account Summary")
        print("=" * 80)
        summary = account_mgr.get_account_summary(accounts)
        print(f"Total Accounts: {summary['total_accounts']}")
        print(f"Organizations: {summary['organizations']}")
        print(f"Org Admin Accounts: {summary['org_admin_accounts']}")
        print("\nRegions:")
        for region, count in summary["regions"].items():
            print(f"  {region}: {count}")
        print("\nCloud Providers:")
        for provider, count in summary["cloud_providers"].items():
            print(f"  {provider}: {count}")
        print("\nEditions:")
        for edition, count in summary["editions"].items():
            print(f"  {edition}: {count}")

        # Example 6: Get account parameters
        print("\n" + "=" * 80)
        print("Example 6: Account Parameters")
        print("=" * 80)
        parameters = account_mgr.get_account_parameters()
        print(f"Retrieved {len(parameters)} account parameters")
        # Print a few interesting parameters
        interesting_params = [
            "TIMEZONE",
            "WEEK_START",
            "CLIENT_SESSION_KEEP_ALIVE",
            "STATEMENT_TIMEOUT_IN_SECONDS",
            "MAX_CONCURRENCY_LEVEL",
        ]
        for param in interesting_params:
            if param in parameters:
                print(f"  {param}: {parameters[param]}")

        # Example 7: List saved account files
        print("\n" + "=" * 80)
        print("Example 7: List Saved Account Files")
        print("=" * 80)
        saved_files = account_mgr.list_saved_account_files()
        print(f"Found {len(saved_files)} saved account files:")
        for file in saved_files[:5]:  # Show first 5
            print(f"  - {file.name}")

        # Example 8: Get latest saved file
        print("\n" + "=" * 80)
        print("Example 8: Latest Saved File")
        print("=" * 80)
        latest_file = account_mgr.get_latest_account_file()
        if latest_file:
            print(f"Latest saved file: {latest_file.name}")
        else:
            print("No saved files found")

        print("\n" + "=" * 80)
        print("Examples completed successfully!")
        print("=" * 80)

    finally:
        conn.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
