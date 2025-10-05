"""
Snowflake Replication Module

This module handles Snowflake replication and failover group operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from croniter import croniter

from gds_snowflake.connection import SnowflakeConnection

logger = logging.getLogger(__name__)


class FailoverGroup:
    """Represents a Snowflake failover group with its properties."""

    def __init__(self, name: str, properties: dict):
        """
        Initialize a failover group.

        Args:
            name: Failover group name
            properties: Dictionary of failover group properties
        """
        self.name = name
        self.properties = properties
        self.type = properties.get('type', '')
        self.primary_account = properties.get('primary', '')
        self.secondary_accounts = self._parse_secondary_accounts(properties.get('secondary_state', ''))
        self.replication_schedule = properties.get('replication_schedule', '')
        self.next_scheduled_refresh = properties.get('next_scheduled_refresh', '')
        self.allowed_databases = properties.get('allowed_databases', '')
        self.allowed_shares = properties.get('allowed_shares', '')
        self.allowed_integration_types = properties.get('allowed_integration_types', '')

    def _parse_secondary_accounts(self, secondary_state: str) -> list[str]:
        """
        Parse secondary accounts from the secondary_state string.

        Args:
            secondary_state: Secondary state string from Snowflake

        Returns:
            List of secondary account names
        """
        # Example format: "ACCOUNT1:READY, ACCOUNT2:READY"
        if not secondary_state:
            return []

        accounts = []
        for part in secondary_state.split(','):
            part = part.strip()
            if ':' in part:
                account = part.split(':')[0].strip()
                accounts.append(account)
        return accounts

    def is_primary(self, current_account: str) -> bool:
        """
        Check if the current account is the primary for this failover group.

        Args:
            current_account: Current account name

        Returns:
            True if current account is primary, False otherwise
        """
        # Normalize account names for comparison
        current = current_account.upper().split('.')[0]
        primary = self.primary_account.upper().split('.')[0]
        return current == primary

    def get_secondary_account(self, current_account: str) -> Optional[str]:
        """
        Get a secondary account that is not the current account.

        Args:
            current_account: Current account name

        Returns:
            Secondary account name or None if no suitable account found
        """
        current = current_account.upper().split('.')[0]

        for account in self.secondary_accounts:
            account_normalized = account.upper().split('.')[0]
            if account_normalized != current:
                return account

        return None

    def __repr__(self):
        return f"FailoverGroup(name={self.name}, type={self.type}, primary={self.primary_account})"


class SnowflakeReplication:
    """Handles Snowflake replication monitoring and operations."""

    def __init__(self, connection: SnowflakeConnection):
        """
        Initialize replication handler.

        Args:
            connection: SnowflakeConnection instance
        """
        self.connection = connection

    def get_failover_groups(self) -> list[FailoverGroup]:
        """
        Retrieve all failover groups from Snowflake.

        Returns:
            List of FailoverGroup objects

        Raises:
            Exception: If query fails
        """
        try:
            logger.info("Retrieving failover groups")
            results = self.connection.execute_query("SHOW FAILOVER GROUPS")

            failover_groups = []
            for row in results:
                # Parse the row into a dictionary
                properties = {}
                if len(row) >= 2:
                    name = row[1]  # name is typically the second column

                    # Try to parse the properties from the row
                    # The exact column indices may vary, so we'll handle this robustly
                    if len(row) > 2:
                        properties['type'] = row[2] if len(row) > 2 else ''
                        properties['primary'] = row[5] if len(row) > 5 else ''
                        properties['secondary_state'] = row[8] if len(row) > 8 else ''
                        properties['replication_schedule'] = row[9] if len(row) > 9 else ''
                        properties['next_scheduled_refresh'] = row[10] if len(row) > 10 else ''
                        properties['allowed_databases'] = row[11] if len(row) > 11 else ''
                        properties['allowed_shares'] = row[12] if len(row) > 12 else ''
                        properties['allowed_integration_types'] = row[13] if len(row) > 13 else ''

                    fg = FailoverGroup(name, properties)
                    failover_groups.append(fg)
                    logger.info(
                        "Found failover group: %s (Primary: %s, Schedule: %s)",
                        fg.name,
                        fg.primary_account,
                        fg.replication_schedule
                    )

            logger.info("Retrieved %s failover groups", len(failover_groups))
            return failover_groups

        except Exception as e:
            logger.error("Error retrieving failover groups: %s", str(e))
            raise

    def get_replication_history(self, failover_group_name: str, limit: int = 10) -> list[dict]:
        """
        Get replication history for a failover group.

        Args:
            failover_group_name: Name of the failover group
            limit: Maximum number of history records to retrieve

        Returns:
            List of replication history records as dictionaries

        Raises:
            Exception: If query fails
        """
        try:
            query = f"""
            SELECT
                start_time,
                end_time,
                status,
                message
            FROM TABLE(INFORMATION_SCHEMA.REPLICATION_GROUP_REFRESH_HISTORY('{failover_group_name}'))
            ORDER BY start_time DESC
            LIMIT {limit}
            """

            logger.debug("Querying replication history for %s", failover_group_name)
            results = self.connection.execute_query_dict(query)

            return results

        except Exception as e:
            logger.error("Error retrieving replication history for %s: %s", failover_group_name, str(e))
            raise

    def parse_cron_schedule(self, cron_expression: str) -> Optional[int]:
        """
        Parse a cron schedule and calculate the interval in minutes.

        Args:
            cron_expression: Cron expression string (e.g., "USING CRON */10 * * * * UTC")

        Returns:
            Interval in minutes, or None if unable to parse
        """
        try:
            # Extract the cron part from the expression
            # Format: "USING CRON */10 * * * * UTC"
            if 'USING CRON' in cron_expression.upper():
                parts = cron_expression.split()
                # Find the cron expression (typically after 'CRON' keyword)
                cron_idx = next((i for i, p in enumerate(parts) if p.upper() == 'CRON'), None)
                if cron_idx is not None and len(parts) > cron_idx + 5:
                    # Get the 5 fields of cron expression
                    cron_fields = parts[cron_idx + 1:cron_idx + 6]
                    cron_str = ' '.join(cron_fields)

                    # Use croniter to calculate the interval
                    base_time = datetime.now()
                    cron = croniter(cron_str, base_time)
                    next_time = cron.get_next(datetime)
                    following_time = cron.get_next(datetime)

                    interval = (following_time - next_time).total_seconds() / 60
                    logger.debug("Parsed cron schedule '%s' -> %s minutes", cron_expression, interval)
                    return int(interval)

            logger.warning("Unable to parse cron schedule: %s", cron_expression)
            return None

        except Exception as e:
            logger.error("Error parsing cron schedule '%s': %s", cron_expression, str(e))
            return None

    def check_replication_failure(self, failover_group: FailoverGroup) -> tuple[bool, Optional[str]]:
        """
        Check if the last replication failed for a failover group.

        Args:
            failover_group: FailoverGroup object

        Returns:
            Tuple of (is_failed, error_message)
        """
        try:
            history = self.get_replication_history(failover_group.name, limit=1)

            if not history:
                logger.warning("No replication history found for %s", failover_group.name)
                return False, None

            last_run = history[0]
            status = last_run.get('STATUS', '').upper()

            if status == 'FAILED' or status == 'PARTIALLY_FAILED':
                message = last_run.get('MESSAGE', 'No error message available')
                logger.warning("Replication failed for %s: %s", failover_group.name, message)
                return True, message

            return False, None

        except Exception as e:
            logger.error("Error checking replication failure for %s: %s", failover_group.name, str(e))
            return False, None

    def check_replication_latency(self, failover_group: FailoverGroup) -> tuple[bool, Optional[str]]:
        """
        Check if there is replication latency for a failover group.

        Latency is calculated as: expected_time = last_completion + interval + (last_duration * 1.1)
        If current time > expected_time, then there is latency.

        Args:
            failover_group: FailoverGroup object

        Returns:
            Tuple of (has_latency, latency_message)
        """
        try:
            # Parse the cron schedule to get the interval
            interval_minutes = self.parse_cron_schedule(failover_group.replication_schedule)
            if interval_minutes is None:
                logger.warning("Cannot determine latency for %s - unable to parse schedule", failover_group.name)
                return False, None

            # Get the last replication history
            history = self.get_replication_history(failover_group.name, limit=1)
            if not history:
                logger.warning("No replication history found for %s", failover_group.name)
                return False, None

            last_run = history[0]
            end_time = last_run.get('END_TIME')
            start_time = last_run.get('START_TIME')

            if not end_time or not start_time:
                logger.warning("Missing time information for %s", failover_group.name)
                return False, None

            # Calculate the duration of the last replication
            duration = (end_time - start_time).total_seconds() / 60  # in minutes

            # Calculate expected next completion time
            # Formula: last_completion + interval + (duration * 1.1)
            expected_next = end_time + timedelta(minutes=interval_minutes + (duration * 1.1))

            current_time = datetime.now(end_time.tzinfo) if end_time.tzinfo else datetime.now()

            if current_time > expected_next:
                delay_minutes = (current_time - expected_next).total_seconds() / 60
                message = (f"Replication latency detected for {failover_group.name}. "
                           f"Expected completion by {expected_next}, but current time is {current_time}. "
                           f"Delay: {delay_minutes:.1f} minutes. "
                           f"Last replication took {duration:.1f} minutes, interval is {interval_minutes} minutes.")
                logger.warning(message)
                return True, message

            return False, None

        except Exception as e:
            logger.error(
                "Error checking replication latency for %s: %s",
                failover_group.name,
                str(e)
            )
            return False, None

    def switch_to_secondary_account(
        self, failover_group: FailoverGroup, current_account: str
    ) -> bool:
        """
        Switch connection to a secondary account for the failover group.

        Args:
            failover_group: FailoverGroup object
            current_account: Current account name

        Returns:
            True if successfully switched, False otherwise
        """
        try:
            if not failover_group.is_primary(current_account):
                logger.info("Already on secondary account for %s", failover_group.name)
                return True

            secondary_account = failover_group.get_secondary_account(current_account)
            if not secondary_account:
                logger.error("No secondary account found for %s", failover_group.name)
                return False

            logger.info(
                "Switching to secondary account %s for %s",
                secondary_account,
                failover_group.name
            )
            self.connection.switch_account(secondary_account)
            return True

        except Exception as e:
            logger.error("Error switching to secondary account: %s", str(e))
            return False
