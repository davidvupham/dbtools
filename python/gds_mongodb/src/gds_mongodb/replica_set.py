"""
MongoDB replica set management module.

This module provides functionality for managing MongoDB replica sets,
including adding and removing members, getting configuration and status,
and monitoring replica set health.
"""

import logging
import time
from typing import TYPE_CHECKING, Any, Optional, Union

from gds_database import (
    ConfigurationError,
    DatabaseConnectionError,
    QueryError,
)
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from .connection import MongoDBConnection

if TYPE_CHECKING:
    from .monitoring import Alert, AlertType

logger = logging.getLogger(__name__)


class MongoDBReplicaSetManager:
    """
    MongoDB replica set management class.

    Provides comprehensive replica set management functionality including:
    - Getting replica set status and configuration
    - Adding and removing replica set members
    - Reconfiguring replica sets
    - Monitoring member health and roles
    - Managing replica set priorities and votes

    Examples:
        # Using with MongoDBConnection
        conn = MongoDBConnection(
            host='replica1.example.com',
            database='admin',
            username='admin',
            password='secret',
            replica_set='myReplicaSet'
        )
        conn.connect()

        rs_manager = MongoDBReplicaSetManager(conn)

        # Get replica set status
        status = rs_manager.get_status()
        print(f"Replica set: {status['set']}")
        print(f"Members: {len(status['members'])}")

        # Get configuration
        config = rs_manager.get_config()
        print(f"Config version: {config['version']}")

        # Add a new member
        rs_manager.add_member('replica4.example.com:27017')

        # Remove a member
        rs_manager.remove_member('replica4.example.com:27017')

        # Get primary node
        primary = rs_manager.get_primary()
        print(f"Primary: {primary}")

        # Check member health
        health = rs_manager.get_member_health()
        for member, is_healthy in health.items():
            print(f"{member}: {'healthy' if is_healthy else 'unhealthy'}")
    """

    def __init__(
        self,
        connection: Union[MongoDBConnection, MongoClient],
    ):
        """
        Initialize replica set manager.

        Args:
            connection: MongoDBConnection instance or MongoClient

        Raises:
            ValueError: If connection is invalid or not provided
        """
        if isinstance(connection, MongoDBConnection):
            self.client = connection.client
            self.connection = connection
        elif isinstance(connection, MongoClient):
            self.client = connection
            self.connection = None
        else:
            raise ValueError("connection must be MongoDBConnection or MongoClient instance")

        if not self.client:
            raise ValueError("Connection not established")

    def get_status(self) -> dict[str, Any]:
        """
        Get replica set status.

        Returns detailed status information about the replica set including
        member states, health, replication lag, and more.

        Returns:
            Dictionary containing replica set status:
                - set: Replica set name
                - date: Current timestamp
                - myState: State of current member
                - members: List of member status information
                - ok: Command success indicator

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> status = rs_manager.get_status()
            >>> print(f"Replica set: {status['set']}")
            >>> print(f"My state: {status['myState']}")
            >>> for member in status["members"]:
            ...     print(f"  {member['name']}: {member['stateStr']}")
        """
        try:
            logger.debug("Getting replica set status")
            result = self.client.admin.command("replSetGetStatus")
            logger.info("Successfully retrieved replica set status")
            return result

        except OperationFailure as e:
            if "not running with --replSet" in str(e):
                error_msg = "Server is not running as part of a replica set"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg) from e
            error_msg = f"Failed to get replica set status: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except ServerSelectionTimeoutError as e:
            error_msg = f"Server selection timeout getting replica set status: {e}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting replica set status: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_config(self) -> dict[str, Any]:
        """
        Get replica set configuration.

        Returns the current replica set configuration including member
        definitions, settings, and version information.

        Returns:
            Dictionary containing replica set configuration:
                - _id: Replica set name
                - version: Configuration version number
                - members: List of member configurations
                - settings: Replica set settings

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If config retrieval fails

        Examples:
            >>> config = rs_manager.get_config()
            >>> print(f"Replica set: {config['_id']}")
            >>> print(f"Version: {config['version']}")
            >>> for member in config["members"]:
            ...     priority = member.get("priority", 1)
            ...     print(f"  {member['host']} - priority: {priority}")
        """
        try:
            logger.debug("Getting replica set configuration")
            result = self.client.admin.command("replSetGetConfig")
            config = result.get("config", {})
            logger.info("Successfully retrieved replica set configuration")
            return config

        except OperationFailure as e:
            if "not running with --replSet" in str(e):
                error_msg = "Server is not running as part of a replica set"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg) from e
            error_msg = f"Failed to get replica set configuration: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting replica set configuration: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def add_member(
        self,
        host: str,
        priority: int = 1,
        votes: int = 1,
        arbiter_only: bool = False,
        hidden: bool = False,
        slave_delay: int = 0,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Add a new member to the replica set.

        Args:
            host: Host address in format 'hostname:port'
            priority: Member priority for elections (0-1000, default: 1)
                     Priority 0 members cannot become primary
            votes: Number of votes in elections (0 or 1, default: 1)
            arbiter_only: If True, member is arbiter (no data, only votes)
            hidden: If True, member is hidden from application queries
            slave_delay: Delay replication by this many seconds
                        (for delayed backups)
            tags: Custom tags for read preference and write concern targeting

        Returns:
            Dictionary containing the result of the reconfiguration

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If member addition fails
            ConfigurationError: If configuration is invalid

        Examples:
            >>> # Add a regular data-bearing member
            >>> rs_manager.add_member("replica4.example.com:27017")

            >>> # Add a priority 0 member (cannot become primary)
            >>> rs_manager.add_member("replica5.example.com:27017", priority=0)

            >>> # Add an arbiter (no data, voting only)
            >>> rs_manager.add_member("arbiter1.example.com:27017", arbiter_only=True)

            >>> # Add a hidden member with delayed replication
            >>> rs_manager.add_member(
            ...     "backup.example.com:27017",
            ...     hidden=True,
            ...     slave_delay=3600,  # 1 hour delay
            ...     priority=0,
            ... )

            >>> # Add member with custom tags
            >>> rs_manager.add_member(
            ...     "replica6.example.com:27017", tags={"dc": "east", "usage": "analytics"}
            ... )
        """
        if not host or ":" not in host:
            raise ConfigurationError("Host must be in format 'hostname:port', e.g. 'localhost:27017'")

        try:
            logger.debug(f"Adding member {host} to replica set")

            # Get current configuration
            config = self.get_config()

            # Check if member already exists
            for member in config.get("members", []):
                if member.get("host") == host:
                    raise ConfigurationError(f"Member with host {host} already exists in replica set")

            # Find next available member ID
            member_ids = [m.get("_id", 0) for m in config.get("members", [])]
            max_id = max(member_ids, default=-1)
            new_member_id = max_id + 1

            # Build new member configuration
            new_member: dict[str, Any] = {
                "_id": new_member_id,
                "host": host,
            }

            if arbiter_only:
                new_member["arbiterOnly"] = True
                new_member["priority"] = 0  # Arbiters must have priority 0
            else:
                if priority != 1:
                    new_member["priority"] = priority
                if votes != 1:
                    new_member["votes"] = votes
                if hidden:
                    new_member["hidden"] = True
                    if priority > 0:
                        logger.warning("Hidden members should have priority 0, setting priority to 0")
                        new_member["priority"] = 0
                if slave_delay > 0:
                    new_member["slaveDelay"] = slave_delay
                    if priority > 0:
                        logger.warning("Delayed members should have priority 0, setting priority to 0")
                        new_member["priority"] = 0
                if tags:
                    new_member["tags"] = tags

            # Add new member to configuration
            config["members"].append(new_member)

            # Increment version
            config["version"] += 1

            # Apply new configuration
            logger.debug(f"Applying new replica set configuration (version {config['version']})")
            result = self.client.admin.command("replSetReconfig", config)

            logger.info(f"Successfully added member {host} to replica set")
            return result

        except ConfigurationError:
            raise
        except OperationFailure as e:
            error_msg = f"Failed to add member to replica set: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error adding member to replica set: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def remove_member(self, host: str) -> dict[str, Any]:
        """
        Remove a member from the replica set.

        Args:
            host: Host address of member to remove (format: 'hostname:port')

        Returns:
            Dictionary containing the result of the reconfiguration

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If member removal fails
            ConfigurationError: If member not found

        Examples:
            >>> # Remove a member by host
            >>> rs_manager.remove_member("replica4.example.com:27017")

            >>> # Remove an arbiter
            >>> rs_manager.remove_member("arbiter1.example.com:27017")
        """
        if not host:
            raise ConfigurationError("Host must be specified")

        try:
            logger.debug(f"Removing member {host} from replica set")

            # Get current configuration
            config = self.get_config()

            # Find and remove the member
            members = config.get("members", [])
            original_count = len(members)

            config["members"] = [m for m in members if m.get("host") != host]

            if len(config["members"]) == original_count:
                raise ConfigurationError(f"Member with host {host} not found in replica set")

            # Increment version
            config["version"] += 1

            # Apply new configuration
            version = config["version"]
            logger.debug(f"Applying new replica set configuration (version {version})")
            result = self.client.admin.command("replSetReconfig", config)

            logger.info(f"Successfully removed member {host} from replica set")
            return result

        except ConfigurationError:
            raise
        except OperationFailure as e:
            error_msg = f"Failed to remove member from replica set: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error removing member from replica set: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_primary(self) -> Optional[str]:
        """
        Get the current primary member of the replica set.

        Returns:
            Host address of the primary member, or None if no primary exists

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> primary = rs_manager.get_primary()
            >>> if primary:
            ...     print(f"Primary: {primary}")
            ... else:
            ...     print("No primary available")
        """
        try:
            status = self.get_status()
            for member in status.get("members", []):
                if member.get("stateStr") == "PRIMARY":
                    return member.get("name")
            return None

        except Exception as e:
            error_msg = f"Error getting primary member: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_secondaries(self) -> list[str]:
        """
        Get list of secondary members in the replica set.

        Returns:
            List of host addresses of secondary members

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> secondaries = rs_manager.get_secondaries()
            >>> print(f"Secondaries: {', '.join(secondaries)}")
        """
        try:
            status = self.get_status()
            secondaries = []
            for member in status.get("members", []):
                if member.get("stateStr") == "SECONDARY":
                    secondaries.append(member.get("name"))
            return secondaries

        except Exception as e:
            error_msg = f"Error getting secondary members: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_arbiters(self) -> list[str]:
        """
        Get list of arbiter members in the replica set.

        Returns:
            List of host addresses of arbiter members

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> arbiters = rs_manager.get_arbiters()
            >>> print(f"Arbiters: {', '.join(arbiters)}")
        """
        try:
            status = self.get_status()
            arbiters = []
            for member in status.get("members", []):
                if member.get("stateStr") == "ARBITER":
                    arbiters.append(member.get("name"))
            return arbiters

        except Exception as e:
            error_msg = f"Error getting arbiter members: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_member_health(self) -> dict[str, bool]:
        """
        Get health status of all replica set members.

        Returns:
            Dictionary mapping member host addresses to health status
            (True=healthy)

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> health = rs_manager.get_member_health()
            >>> for member, is_healthy in health.items():
            ...     status = "healthy" if is_healthy else "unhealthy"
            ...     print(f"{member}: {status}")
        """
        try:
            status = self.get_status()
            health = {}
            for member in status.get("members", []):
                name = member.get("name")
                # health field: 1 = up, 0 = down
                health[name] = member.get("health", 0) == 1
            return health

        except Exception as e:
            error_msg = f"Error getting member health: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_member_states(self) -> dict[str, str]:
        """
        Get current state of all replica set members.

        Returns:
            Dictionary mapping member host addresses to their state strings
            (PRIMARY, SECONDARY, ARBITER, RECOVERING, etc.)

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> states = rs_manager.get_member_states()
            >>> for member, state in states.items():
            ...     print(f"{member}: {state}")
        """
        try:
            status = self.get_status()
            states = {}
            for member in status.get("members", []):
                name = member.get("name")
                state = member.get("stateStr", "UNKNOWN")
                states[name] = state
            return states

        except Exception as e:
            error_msg = f"Error getting member states: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_replication_lag(self) -> dict[str, int]:
        """
        Get replication lag (in seconds) for all secondary members.

        Returns:
            Dictionary mapping secondary member host addresses to their
            replication lag in seconds

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If status retrieval fails

        Examples:
            >>> lag = rs_manager.get_replication_lag()
            >>> for member, lag_seconds in lag.items():
            ...     print(f"{member}: {lag_seconds}s behind")
        """
        try:
            status = self.get_status()
            lags = {}

            # Find primary's optime
            primary_optime = None
            for member in status.get("members", []):
                if member.get("stateStr") == "PRIMARY":
                    primary_optime = member.get("optimeDate")
                    break

            if not primary_optime:
                logger.warning("No primary found, cannot calculate replication lag")
                return lags

            # Calculate lag for each secondary
            for member in status.get("members", []):
                if member.get("stateStr") == "SECONDARY":
                    name = member.get("name")
                    member_optime = member.get("optimeDate")
                    if member_optime:
                        delta = (primary_optime - member_optime).total_seconds()
                        lag_seconds = int(delta)
                        lags[name] = lag_seconds

            return lags

        except Exception as e:
            error_msg = f"Error getting replication lag: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def reconfigure(self, config: dict[str, Any], force: bool = False) -> dict[str, Any]:
        """
        Apply a new replica set configuration.

        Warning: This is an advanced operation. Incorrect configuration
        can make the replica set unavailable. Use with caution.

        Args:
            config: New replica set configuration dictionary
            force: If True, force reconfiguration even if not connected
                  to primary

        Returns:
            Dictionary containing the result of the reconfiguration

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If reconfiguration fails
            ConfigurationError: If configuration is invalid

        Examples:
            >>> # Get current config, modify it, and reapply
            >>> config = rs_manager.get_config()
            >>> config["version"] += 1
            >>> # Modify member priorities
            >>> for member in config["members"]:
            ...     if member["host"] == "replica1.example.com:27017":
            ...         member["priority"] = 10
            >>> rs_manager.reconfigure(config)
        """
        if not config:
            raise ConfigurationError("Configuration cannot be empty")

        if "version" not in config:
            raise ConfigurationError("Configuration must include version number")

        if "members" not in config or not config["members"]:
            raise ConfigurationError("Configuration must include members")

        try:
            logger.debug(f"Applying replica set configuration (version {config.get('version')})")

            if force:
                result = self.client.admin.command("replSetReconfig", config, force=True)
            else:
                result = self.client.admin.command("replSetReconfig", config)

            logger.info("Successfully applied replica set configuration")
            return result

        except OperationFailure as e:
            error_msg = f"Failed to apply replica set configuration: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error applying replica set configuration: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def step_down(self, seconds: int = 60) -> dict[str, Any]:
        """
        Force the primary to step down and become a secondary.

        Args:
            seconds: Number of seconds the primary will wait before
                    attempting to become primary again (default: 60)

        Returns:
            Dictionary containing the result of the step down operation

        Raises:
            DatabaseConnectionError: If not connected to primary
            QueryError: If step down fails

        Examples:
            >>> # Step down primary for 60 seconds
            >>> rs_manager.step_down()

            >>> # Step down for 5 minutes
            >>> rs_manager.step_down(seconds=300)
        """
        try:
            logger.debug(f"Stepping down primary for {seconds} seconds")
            result = self.client.admin.command("replSetStepDown", seconds)
            logger.info("Successfully stepped down primary")
            return result

        except OperationFailure as e:
            error_msg = f"Failed to step down primary: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error stepping down primary: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def freeze(self, seconds: int) -> dict[str, Any]:
        """
        Prevent a replica set member from seeking election for specified time.

        Args:
            seconds: Number of seconds to freeze the member (0 to unfreeze)

        Returns:
            Dictionary containing the result of the freeze operation

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If freeze operation fails

        Examples:
            >>> # Freeze member for 2 minutes
            >>> rs_manager.freeze(120)

            >>> # Unfreeze member
            >>> rs_manager.freeze(0)
        """
        try:
            logger.debug(f"Freezing member for {seconds} seconds")
            result = self.client.admin.command("replSetFreeze", seconds)
            logger.info(f"Successfully {'unfroze' if seconds == 0 else 'froze'} member")
            return result

        except OperationFailure as e:
            error_msg = f"Failed to freeze member: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error freezing member: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def monitor_health(self, alert_manager: Optional[Any] = None) -> dict[str, Any]:
        """
        Comprehensive health monitoring for the replica set.

        Performs multiple health checks and generates alerts for issues.

        Args:
            alert_manager: Optional alert manager for notifications

        Returns:
            Dictionary containing health status and any alerts

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If monitoring fails

        Examples:
            >>> health = rs_manager.monitor_health()
            >>> print(f"Overall health: {health['overall_health']}")
            >>> for alert in health["alerts"]:
            ...     print(f"Alert: {alert['type']} - {alert['message']}")
        """
        try:
            health_data = {
                "timestamp": time.time(),
                "overall_health": "healthy",
                "checks": {},
                "alerts": [],
            }

            # Check replica set status
            status = self.get_status()
            health_data["checks"]["replica_set_status"] = self._check_replica_set_status(status)

            # Check member health
            member_health = self.get_member_health()
            health_data["checks"]["member_health"] = self._check_member_health(member_health)

            # Check replication lag
            replication_lag = self.get_replication_lag()
            health_data["checks"]["replication_lag"] = self._check_replication_lag(replication_lag)

            # Check primary availability
            primary = self.get_primary()
            health_data["checks"]["primary_availability"] = self._check_primary_availability(primary, status)

            # Check configuration consistency
            config = self.get_config()
            health_data["checks"]["configuration_consistency"] = self._check_configuration_consistency(config, status)

            # Determine overall health
            health_data["overall_health"] = self._determine_overall_health(health_data["checks"])

            # Generate alerts
            alerts = self._generate_replica_set_alerts(health_data)
            health_data["alerts"] = alerts

            # Send alerts to alert manager
            if alert_manager:
                for alert in alerts:
                    alert_manager.add_alert(alert)

            return health_data

        except Exception as e:
            error_msg = f"Error monitoring replica set health: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def troubleshoot_replication_issues(self) -> dict[str, Any]:
        """
        Comprehensive troubleshooting for replica set replication issues.

        Performs diagnostic checks and provides recommendations for fixing
        common replication problems.

        Returns:
            Dictionary containing diagnostic information and recommendations

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If diagnostics fail

        Examples:
            >>> diagnostics = rs_manager.troubleshoot_replication_issues()
            >>> for issue in diagnostics["issues"]:
            ...     print(f"Issue: {issue['description']}")
            ...     print(f"Recommendation: {issue['recommendation']}")
        """
        try:
            diagnostics = {
                "timestamp": time.time(),
                "issues": [],
                "recommendations": [],
                "diagnostic_data": {},
            }

            # Get current status
            status = self.get_status()
            diagnostics["diagnostic_data"]["status"] = status

            # Check for common issues
            self._diagnose_primary_issues(status, diagnostics)
            self._diagnose_member_issues(status, diagnostics)
            self._diagnose_network_issues(status, diagnostics)
            self._diagnose_oplog_issues(status, diagnostics)

            return diagnostics

        except Exception as e:
            error_msg = f"Error troubleshooting replication issues: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_replication_metrics(self) -> dict[str, Any]:
        """
        Get detailed replication metrics for monitoring and alerting.

        Returns comprehensive metrics about replication performance,
        lag, throughput, and member states.

        Returns:
            Dictionary containing replication metrics

        Raises:
            DatabaseConnectionError: If not connected to replica set
            QueryError: If metrics retrieval fails

        Examples:
            >>> metrics = rs_manager.get_replication_metrics()
            >>> print(f"Replication lag: {metrics['max_lag_seconds']}s")
            >>> print(f"Oplog window: {metrics['oplog_window_hours']}h")
        """
        try:
            metrics = {
                "timestamp": time.time(),
                "replication_lag": {},
                "member_states": {},
                "oplog_info": {},
                "throughput": {},
            }

            # Get status and lag information
            status = self.get_status()
            metrics["replication_lag"] = self.get_replication_lag()
            metrics["member_states"] = self.get_member_states()

            # Calculate max lag
            lag_values = list(metrics["replication_lag"].values())
            metrics["max_lag_seconds"] = max(lag_values) if lag_values else 0

            # Get oplog information
            metrics["oplog_info"] = self._get_oplog_info()

            # Calculate throughput metrics
            metrics["throughput"] = self._calculate_replication_throughput(status)

            return metrics

        except Exception as e:
            error_msg = f"Error getting replication metrics: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def _check_replica_set_status(self, status: dict[str, Any]) -> dict[str, Any]:
        """Check overall replica set status."""
        check_result = {"status": "healthy", "details": {}, "issues": []}

        # Check if replica set is initialized
        if "set" not in status:
            check_result["status"] = "critical"
            check_result["issues"].append("Replica set not initialized")
            return check_result

        # Check member count
        members = status.get("members", [])
        member_count = len(members)
        check_result["details"]["member_count"] = member_count

        if member_count < 3:
            check_result["status"] = "warning"
            check_result["issues"].append(f"Low member count: {member_count} (recommended: 3+)")

        # Check for quorum
        healthy_members = sum(1 for m in members if m.get("health") == 1)
        check_result["details"]["healthy_members"] = healthy_members

        if healthy_members < (member_count // 2 + 1):
            check_result["status"] = "critical"
            check_result["issues"].append("No quorum available")

        return check_result

    def _check_member_health(self, member_health: dict[str, bool]) -> dict[str, Any]:
        """Check individual member health."""
        check_result = {"status": "healthy", "details": {}, "issues": []}

        unhealthy_members = [member for member, healthy in member_health.items() if not healthy]
        check_result["details"]["unhealthy_members"] = unhealthy_members

        if unhealthy_members:
            check_result["status"] = "critical"
            check_result["issues"].extend([f"Member {member} is unhealthy" for member in unhealthy_members])

        return check_result

    def _check_replication_lag(self, replication_lag: dict[str, int]) -> dict[str, Any]:
        """Check replication lag across members."""
        check_result = {"status": "healthy", "details": {}, "issues": []}

        # Default thresholds
        warning_threshold = 30  # seconds
        critical_threshold = 300  # seconds

        high_lag_members = []
        for member, lag in replication_lag.items():
            check_result["details"][f"lag_{member}"] = lag
            if lag > critical_threshold:
                high_lag_members.append((member, lag, "critical"))
            elif lag > warning_threshold:
                high_lag_members.append((member, lag, "warning"))

        if high_lag_members:
            max_severity = max(severity for _, _, severity in high_lag_members)
            check_result["status"] = max_severity

            for member, lag, _severity in high_lag_members:
                check_result["issues"].append(f"High replication lag on {member}: {lag}s")

        return check_result

    def _check_primary_availability(self, primary: Optional[str], status: dict[str, Any]) -> dict[str, Any]:
        """Check primary availability."""
        check_result = {"status": "healthy", "details": {}, "issues": []}

        check_result["details"]["primary"] = primary

        if not primary:
            check_result["status"] = "critical"
            check_result["issues"].append("No primary available - possible election in progress or split brain")

            # Check if this is an election
            members = status.get("members", [])
            electing_members = [m for m in members if m.get("stateStr") == "STARTUP2"]
            if electing_members:
                check_result["issues"].append("Election in progress")

        return check_result

    def _check_configuration_consistency(self, config: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
        """Check configuration consistency."""
        check_result = {"status": "healthy", "details": {}, "issues": []}

        config_members = config.get("members", [])
        status_members = status.get("members", [])

        config_hosts = {m.get("host") for m in config_members}
        status_hosts = {m.get("name") for m in status_members}

        # Check for missing members
        missing_in_status = config_hosts - status_hosts
        if missing_in_status:
            check_result["status"] = "warning"
            check_result["issues"].extend([f"Member {host} configured but not in status" for host in missing_in_status])

        # Check for extra members
        extra_in_status = status_hosts - config_hosts
        if extra_in_status:
            check_result["status"] = "warning"
            check_result["issues"].extend([f"Member {host} in status but not configured" for host in extra_in_status])

        return check_result

    def _determine_overall_health(self, checks: dict[str, Any]) -> str:
        """Determine overall health from individual checks."""
        severity_levels = {"healthy": 0, "warning": 1, "error": 2, "critical": 3}

        max_severity = 0
        for _check_name, check_result in checks.items():
            status = check_result.get("status", "healthy")
            severity = severity_levels.get(status, 0)
            max_severity = max(max_severity, severity)

        severity_names = {0: "healthy", 1: "warning", 2: "error", 3: "critical"}
        return severity_names[max_severity]

    def _generate_replica_set_alerts(self, health_data: dict[str, Any]) -> list["Alert"]:
        """Generate alerts from health check results."""
        alerts = []

        # Import here to avoid circular imports
        from .monitoring import Alert, AlertSeverity

        for check_name, check_result in health_data["checks"].items():
            status = check_result.get("status")
            issues = check_result.get("issues", [])

            if status in ["warning", "error", "critical"]:
                severity_map = {
                    "warning": AlertSeverity.WARNING,
                    "error": AlertSeverity.ERROR,
                    "critical": AlertSeverity.CRITICAL,
                }

                for issue in issues:
                    alert_type = self._map_check_to_alert_type(check_name)
                    alert = Alert(
                        alert_type=alert_type,
                        severity=severity_map[status],
                        message=issue,
                        source=f"replica_set_{check_name}",
                        timestamp=health_data["timestamp"],
                    )
                    alerts.append(alert)

        return alerts

    def _map_check_to_alert_type(self, check_name: str) -> "AlertType":
        """Map health check names to alert types."""
        from .monitoring import AlertType

        mapping = {
            "replica_set_status": AlertType.REPLICA_SET_SPLIT_BRAIN,
            "member_health": AlertType.MEMBER_UNHEALTHY,
            "replication_lag": AlertType.REPLICA_LAG_HIGH,
            "primary_availability": AlertType.REPLICA_SET_NO_PRIMARY,
            "configuration_consistency": AlertType.REPLICA_SET_SPLIT_BRAIN,
        }

        return mapping.get(check_name, AlertType.REPLICA_SET_SPLIT_BRAIN)

    def _diagnose_primary_issues(self, status: dict[str, Any], diagnostics: dict[str, Any]):
        """Diagnose primary-related issues."""
        primary = None
        for member in status.get("members", []):
            if member.get("stateStr") == "PRIMARY":
                primary = member
                break

        if not primary:
            diagnostics["issues"].append(
                {
                    "type": "no_primary",
                    "description": "No primary member available",
                    "severity": "critical",
                    "recommendation": "Check if election is in progress or if there is a network partition",
                }
            )

        # Check primary stability
        my_state = status.get("myState")
        if my_state != 1:  # 1 = PRIMARY
            diagnostics["issues"].append(
                {
                    "type": "primary_instability",
                    "description": f"Current member is not primary (state: {my_state})",
                    "severity": "warning",
                    "recommendation": "Monitor for election activity or connectivity issues",
                }
            )

    def _diagnose_member_issues(self, status: dict[str, Any], diagnostics: dict[str, Any]):
        """Diagnose member-related issues."""
        members = status.get("members", [])

        for member in members:
            name = member.get("name")
            state = member.get("stateStr")
            health = member.get("health")

            if health != 1:
                diagnostics["issues"].append(
                    {
                        "type": "unhealthy_member",
                        "description": f"Member {name} is unhealthy (state: {state})",
                        "severity": "critical",
                        "recommendation": f"Check connectivity and logs for member {name}",
                    }
                )

            # Check for long-running operations that might block replication
            if state == "RECOVERING":
                diagnostics["issues"].append(
                    {
                        "type": "recovering_member",
                        "description": f"Member {name} is in RECOVERING state",
                        "severity": "warning",
                        "recommendation": f"Check oplog and disk space on member {name}",
                    }
                )

    def _diagnose_network_issues(self, status: dict[str, Any], diagnostics: dict[str, Any]):
        """Diagnose network-related issues."""
        members = status.get("members", [])

        for member in members:
            name = member.get("name")
            ping_ms = member.get("pingMs")

            if ping_ms and ping_ms > 1000:  # High latency
                diagnostics["issues"].append(
                    {
                        "type": "high_latency",
                        "description": f"High network latency to {name}: {ping_ms}ms",
                        "severity": "warning",
                        "recommendation": "Check network connectivity between members",
                    }
                )

    def _diagnose_oplog_issues(self, status: dict[str, Any], diagnostics: dict[str, Any]):
        """Diagnose oplog-related issues."""
        # Get oplog information
        try:
            oplog_info = self._get_oplog_info()
            oplog_window = oplog_info.get("oplog_window_hours", 0)

            if oplog_window < 24:  # Less than 24 hours
                diagnostics["issues"].append(
                    {
                        "type": "small_oplog",
                        "description": f"Oplog window too small: {oplog_window:.1f} hours",
                        "severity": "warning",
                        "recommendation": "Consider increasing oplog size for better durability",
                    }
                )

        except Exception as e:
            diagnostics["issues"].append(
                {
                    "type": "oplog_access_error",
                    "description": f"Cannot access oplog information: {e}",
                    "severity": "warning",
                    "recommendation": "Check oplog collection access permissions",
                }
            )

    def _get_oplog_info(self) -> dict[str, Any]:
        """Get oplog information."""
        try:
            # Switch to local database
            local_db = self.client.local

            # Get oplog stats
            oplog_stats = local_db.command("collStats", "oplog.rs")

            # Get first and last oplog entries
            first_entry = local_db.oplog.rs.find().sort("$natural", 1).limit(1)
            last_entry = local_db.oplog.rs.find().sort("$natural", -1).limit(1)

            first_ts = None
            last_ts = None

            if first_entry.count():
                first_ts = first_entry[0].get("ts")
            if last_entry.count():
                last_ts = last_entry[0].get("ts")

            oplog_info = {
                "oplog_size_mb": oplog_stats.get("size", 0) / (1024 * 1024),
                "oplog_count": oplog_stats.get("count", 0),
                "first_ts": first_ts,
                "last_ts": last_ts,
                "oplog_window_hours": 0,
            }

            # Calculate oplog window
            if first_ts and last_ts:
                # Convert timestamps to datetime
                from datetime import datetime

                first_time = datetime.fromtimestamp(first_ts.time)
                last_time = datetime.fromtimestamp(last_ts.time)
                window_seconds = (last_time - first_time).total_seconds()
                oplog_info["oplog_window_hours"] = window_seconds / 3600

            return oplog_info

        except Exception as e:
            logger.warning(f"Could not get oplog info: {e}")
            return {}

    def _calculate_replication_throughput(self, status: dict[str, Any]) -> dict[str, Any]:
        """Calculate replication throughput metrics."""
        throughput = {"oplog_entries_per_second": 0, "data_replicated_mb_per_second": 0}

        # This is a simplified calculation - in practice, you'd need historical data
        # For now, just return placeholder values
        return throughput
