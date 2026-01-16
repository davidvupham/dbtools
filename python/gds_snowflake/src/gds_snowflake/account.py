"""
Snowflake Account Management Module

This module provides functionality to retrieve and manage Snowflake account information,
including all accounts accessible to the user and their attributes. Data is stored in
JSON format in a configurable data directory.

Classes:
    SnowflakeAccount: Manages Snowflake account information and metadata
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .connection import SnowflakeConnection

logger = logging.getLogger(__name__)


@dataclass
class AccountInfo:
    """
    Data class representing a Snowflake account and its attributes.

    Attributes:
        account_name: The name of the Snowflake account
        organization_name: The organization the account belongs to
        account_locator: The unique locator for the account
        region: The cloud region where the account is hosted
        cloud_provider: The cloud provider (AWS, Azure, GCP)
        account_url: The URL for accessing the account
        created_on: When the account was created
        comment: Optional description or comment about the account
        is_org_admin: Whether the account has organization admin privileges
        account_edition: The Snowflake edition (Standard, Enterprise, Business Critical)
        is_current: Whether this is the currently connected account
        retrieved_at: Timestamp when this information was retrieved
    """

    account_name: str
    organization_name: Optional[str] = None
    account_locator: Optional[str] = None
    region: Optional[str] = None
    cloud_provider: Optional[str] = None
    account_url: Optional[str] = None
    created_on: Optional[str] = None
    comment: Optional[str] = None
    is_org_admin: bool = False
    account_edition: Optional[str] = None
    is_current: bool = False
    retrieved_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert AccountInfo to dictionary."""
        return asdict(self)


class SnowflakeAccount:
    """
    Manages Snowflake account information retrieval and storage.

    This class provides methods to:
    - Retrieve all Snowflake accounts accessible to the authenticated user
    - Get detailed attributes for each account
    - Store account information in JSON format
    - Manage the data directory for account metadata

    The data directory location is retrieved from the GDS_DATA_DIR environment variable.
    If not set, it defaults to './data' in the current working directory.

    Example:
        >>> conn = SnowflakeConnection(account="myaccount", user="myuser")
        >>> conn.connect()
        >>> account_mgr = SnowflakeAccount(conn)
        >>> accounts = account_mgr.get_all_accounts()
        >>> account_mgr.save_accounts_to_json(accounts)
    """

    def __init__(self, connection: SnowflakeConnection, data_dir: Optional[str] = None):
        """
        Initialize the Snowflake account manager.

        Args:
            connection: Active SnowflakeConnection instance
            data_dir: Optional data directory path. If not provided,
                     uses GDS_DATA_DIR environment variable or defaults to './data'
        """
        self.connection = connection
        self.data_dir = self._get_data_directory(data_dir)
        self._ensure_data_directory()

    def _get_data_directory(self, data_dir: Optional[str] = None) -> Path:
        """
        Get the data directory path.

        Priority order:
        1. Explicitly provided data_dir parameter
        2. GDS_DATA_DIR environment variable
        3. Default to './data' in current working directory

        Args:
            data_dir: Optional explicit data directory path

        Returns:
            Path object for the data directory
        """
        if data_dir:
            return Path(data_dir)

        env_data_dir = os.getenv("GDS_DATA_DIR")
        if env_data_dir:
            return Path(env_data_dir)

        # Default to ./data
        return Path("./data")

    def _ensure_data_directory(self) -> None:
        """
        Ensure the data directory exists, create if it doesn't.

        Raises:
            OSError: If directory cannot be created
        """
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Data directory ready: %s", self.data_dir)
        except Exception as e:
            logger.error("Failed to create data directory %s: %s", self.data_dir, e)
            raise

    def get_current_account(self) -> AccountInfo:
        """
        Get information about the currently connected account.

        Returns:
            AccountInfo object with current account details

        Raises:
            Exception: If query execution fails
        """
        query = """
        SELECT
            CURRENT_ACCOUNT() as account_name,
            CURRENT_ORGANIZATION_NAME() as organization_name,
            CURRENT_ACCOUNT_NAME() as account_locator,
            CURRENT_REGION() as region,
            CURRENT_VERSION() as version
        """

        try:
            logger.info("Retrieving current account information")
            results = self.connection.execute_query_dict(query)

            if not results:
                raise ValueError("No account information returned")

            account_data = results[0]

            return AccountInfo(
                account_name=account_data.get("ACCOUNT_NAME", ""),
                organization_name=account_data.get("ORGANIZATION_NAME"),
                account_locator=account_data.get("ACCOUNT_LOCATOR"),
                region=account_data.get("REGION"),
                is_current=True,
                retrieved_at=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("Error retrieving current account information: %s", e)
            raise

    def get_all_accounts(self) -> list[AccountInfo]:
        """
        Get information about all Snowflake accounts in the organization.

        This method queries the SNOWFLAKE.ORGANIZATION_USAGE.ACCOUNTS view
        to retrieve all accounts accessible to the authenticated user.

        Note: Requires appropriate privileges to access ORGANIZATION_USAGE schema.

        Returns:
            List of AccountInfo objects for all accessible accounts

        Raises:
            Exception: If query execution fails or user lacks privileges
        """
        query = """
        SELECT
            ACCOUNT_NAME,
            ORGANIZATION_NAME,
            ACCOUNT_LOCATOR,
            ACCOUNT_LOCATOR_URL,
            REGION,
            CLOUD,
            CREATED_ON,
            COMMENT,
            IS_ORG_ADMIN,
            EDITION
        FROM SNOWFLAKE.ORGANIZATION_USAGE.ACCOUNTS
        ORDER BY ACCOUNT_NAME
        """

        try:
            logger.info("Retrieving all accounts in organization")
            results = self.connection.execute_query_dict(query)

            accounts = []
            current_account_name = self.connection.account
            retrieved_at = datetime.now().isoformat()

            for row in results:
                account = AccountInfo(
                    account_name=row.get("ACCOUNT_NAME", ""),
                    organization_name=row.get("ORGANIZATION_NAME"),
                    account_locator=row.get("ACCOUNT_LOCATOR"),
                    region=row.get("REGION"),
                    cloud_provider=row.get("CLOUD"),
                    account_url=row.get("ACCOUNT_LOCATOR_URL"),
                    created_on=(row.get("CREATED_ON").isoformat() if row.get("CREATED_ON") else None),
                    comment=row.get("COMMENT"),
                    is_org_admin=row.get("IS_ORG_ADMIN", False),
                    account_edition=row.get("EDITION"),
                    is_current=(row.get("ACCOUNT_LOCATOR") == current_account_name),
                    retrieved_at=retrieved_at,
                )
                accounts.append(account)

            logger.info("Retrieved %d accounts from organization", len(accounts))
            return accounts

        except Exception as e:
            logger.error("Error retrieving accounts: %s", e)
            logger.warning(
                "If you see a permission error, ensure you have access to "
                "SNOWFLAKE.ORGANIZATION_USAGE.ACCOUNTS view. "
                "Organization admin privileges may be required."
            )
            raise

    def get_account_parameters(self, account_name: Optional[str] = None) -> dict[str, Any]:
        """
        Get account-level parameters and settings.

        Args:
            account_name: Optional account name. If not provided, uses current account.

        Returns:
            Dictionary of account parameters and their values

        Raises:
            Exception: If query execution fails
        """
        query = "SHOW PARAMETERS IN ACCOUNT"

        try:
            if account_name:
                logger.info("Retrieving parameters for account: %s", account_name)
            else:
                logger.info("Retrieving parameters for current account")

            results = self.connection.execute_query_dict(query)

            parameters = {}
            for row in results:
                param_name = row.get("key", row.get("KEY", ""))
                param_value = row.get("value", row.get("VALUE", ""))
                parameters[param_name] = param_value

            logger.info("Retrieved %d account parameters", len(parameters))
            return parameters

        except Exception as e:
            logger.error("Error retrieving account parameters: %s", e)
            raise

    def save_accounts_to_json(self, accounts: list[AccountInfo], filename: Optional[str] = None) -> Path:
        """
        Save account information to a JSON file in the data directory.

        Args:
            accounts: List of AccountInfo objects to save
            filename: Optional filename. If not provided, generates timestamped filename.

        Returns:
            Path to the saved JSON file

        Raises:
            Exception: If file writing fails
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snowflake_accounts_{timestamp}.json"

        filepath = self.data_dir / filename

        try:
            # Convert accounts to dictionaries
            accounts_data = [account.to_dict() for account in accounts]

            # Create output structure
            output = {
                "metadata": {
                    "retrieved_at": datetime.now().isoformat(),
                    "account_count": len(accounts),
                    "data_directory": str(self.data_dir),
                },
                "accounts": accounts_data,
            }

            # Write to JSON file with pretty formatting
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, default=str)

            logger.info("Saved %d accounts to %s", len(accounts), filepath)
            return filepath

        except Exception as e:
            logger.error("Error saving accounts to JSON: %s", e)
            raise

    def load_accounts_from_json(self, filename: str) -> list[AccountInfo]:
        """
        Load account information from a JSON file.

        Args:
            filename: Name of the JSON file in the data directory

        Returns:
            List of AccountInfo objects

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If file reading or parsing fails
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Account data file not found: {filepath}")

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            accounts = []
            for account_dict in data.get("accounts", []):
                account = AccountInfo(**account_dict)
                accounts.append(account)

            logger.info("Loaded %d accounts from %s", len(accounts), filepath)
            return accounts

        except Exception as e:
            logger.error("Error loading accounts from JSON: %s", e)
            raise

    def get_account_summary(self, accounts: list[AccountInfo]) -> dict[str, Any]:
        """
        Generate a summary of account information.

        Args:
            accounts: List of AccountInfo objects

        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            "total_accounts": len(accounts),
            "organizations": len({a.organization_name for a in accounts if a.organization_name}),
            "regions": {},
            "cloud_providers": {},
            "editions": {},
            "org_admin_accounts": 0,
        }

        for account in accounts:
            # Count by region
            if account.region:
                summary["regions"][account.region] = summary["regions"].get(account.region, 0) + 1

            # Count by cloud provider
            if account.cloud_provider:
                summary["cloud_providers"][account.cloud_provider] = (
                    summary["cloud_providers"].get(account.cloud_provider, 0) + 1
                )

            # Count by edition
            if account.account_edition:
                summary["editions"][account.account_edition] = summary["editions"].get(account.account_edition, 0) + 1

            # Count org admin accounts
            if account.is_org_admin:
                summary["org_admin_accounts"] += 1

        return summary

    def list_saved_account_files(self) -> list[Path]:
        """
        List all saved account JSON files in the data directory.

        Returns:
            List of Path objects for JSON files
        """
        try:
            json_files = list(self.data_dir.glob("snowflake_accounts_*.json"))
            json_files.sort(reverse=True)  # Most recent first
            logger.info("Found %d saved account files", len(json_files))
            return json_files
        except Exception as e:
            logger.error("Error listing account files: %s", e)
            return []

    def get_latest_account_file(self) -> Optional[Path]:
        """
        Get the most recently saved account JSON file.

        Returns:
            Path to the latest file, or None if no files exist
        """
        files = self.list_saved_account_files()
        return files[0] if files else None
