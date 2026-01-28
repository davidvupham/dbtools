"""
MongoDB engine and database implementations.

Provides concrete implementations of the DatabaseEngine and Database
abstract base classes from gds_database for MongoDB.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from gds_database import (
    Database,
    DatabaseEngine,
    OperationResult,
)
from gds_database.metadata import (
    BackupType,
    DatabaseMetadata,
    DatabaseState,
    DatabaseType,
    EngineMetadata,
    LogEntry,
    Metric,
    ReplicationStatus,
)
from pymongo.errors import OperationFailure

if TYPE_CHECKING:
    from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoDBDatabase(Database):
    """
    MongoDB database implementation.

    Represents a specific MongoDB database managed by a MongoDBEngine.
    """

    @property
    def metadata(self) -> DatabaseMetadata:
        """Get database metadata, caching the result."""
        if self._metadata is None:
            self._metadata = self._fetch_metadata()
        return self._metadata

    def refresh_metadata(self) -> DatabaseMetadata:
        """Force refresh of cached metadata."""
        self._metadata = self._fetch_metadata()
        return self._metadata

    def _fetch_metadata(self) -> DatabaseMetadata:
        """Fetch metadata from the MongoDB server."""
        client: MongoClient = self.engine.connection.client
        try:
            db = client[self.name]
            stats = db.command("dbStats", scale=1)
            return DatabaseMetadata(
                name=self.name,
                type=DatabaseType.MONGODB,
                size_bytes=stats.get("dataSize"),
                state=DatabaseState.ONLINE,
                additional_attributes={
                    "collections": stats.get("collections", 0),
                    "objects": stats.get("objects", 0),
                    "indexes": stats.get("indexes", 0),
                    "storage_size": stats.get("storageSize", 0),
                    "index_size": stats.get("indexSize", 0),
                },
            )
        except Exception as e:
            logger.warning("Failed to fetch metadata for database '%s': %s", self.name, e)
            return DatabaseMetadata(
                name=self.name,
                type=DatabaseType.MONGODB,
                state=DatabaseState.UNKNOWN,
            )

    def exists(self) -> bool:
        """Check if database exists on the server."""
        client: MongoClient = self.engine.connection.client
        return self.name in client.list_database_names()

    def create(self, **options: Any) -> OperationResult:
        """
        Create the database.

        MongoDB creates databases implicitly on first write. This method
        creates a placeholder collection to materialize the database.

        Args:
            **options: Optional 'collection' name (default: '_placeholder').
        """
        client: MongoClient = self.engine.connection.client
        collection_name = options.get("collection", "_placeholder")
        try:
            db = client[self.name]
            db.create_collection(collection_name)
            return OperationResult.success_result(
                f"Database '{self.name}' created with collection '{collection_name}'"
            )
        except Exception as e:
            return OperationResult.failure_result(
                f"Failed to create database '{self.name}'", error=str(e)
            )

    def drop(self, force: bool = False) -> OperationResult:
        """Drop the database."""
        client: MongoClient = self.engine.connection.client
        try:
            client.drop_database(self.name)
            return OperationResult.success_result(f"Database '{self.name}' dropped")
        except Exception as e:
            return OperationResult.failure_result(
                f"Failed to drop database '{self.name}'", error=str(e)
            )

    def backup(self, path: str, backup_type: BackupType = BackupType.FULL, **options: Any) -> OperationResult:
        """
        Backup the database.

        MongoDB backups are typically performed via mongodump or filesystem
        snapshots. This method provides an interface but requires external
        tooling for actual backup execution.
        """
        return OperationResult.failure_result(
            "MongoDB backups require mongodump or filesystem snapshots. "
            f"Use mongodump --db={self.name} --out={path} from the command line."
        )

    def restore(self, path: str, **options: Any) -> OperationResult:
        """
        Restore database from backup.

        MongoDB restores are typically performed via mongorestore.
        """
        return OperationResult.failure_result(
            "MongoDB restores require mongorestore. "
            f"Use mongorestore --db={self.name} {path} from the command line."
        )


class MongoDBEngine(DatabaseEngine):
    """
    MongoDB engine implementation.

    Represents a MongoDB server or replica set and provides
    administration operations.
    """

    @property
    def metadata(self) -> EngineMetadata:
        """Get engine metadata."""
        client: MongoClient = self.connection.client
        try:
            server_info = client.server_info()
            build_info = client.admin.command("buildInfo")
            return EngineMetadata(
                name="mongodb",
                version=server_info.get("version", "unknown"),
                edition=build_info.get("modules", ["community"])[0] if build_info.get("modules") else "community",
                host=self.connection.config.get("host"),
                port=self.connection.config.get("port"),
                status="online",
            )
        except Exception as e:
            logger.warning("Failed to fetch engine metadata: %s", e)
            return EngineMetadata(
                name="mongodb",
                version="unknown",
                host=self.connection.config.get("host"),
                port=self.connection.config.get("port"),
                status="unknown",
            )

    def build(self, **kwargs: Any) -> OperationResult:
        """
        Build/provision MongoDB infrastructure.

        MongoDB provisioning is typically done via container orchestration
        or cloud providers. This is a placeholder for integration.
        """
        return OperationResult.failure_result(
            "MongoDB provisioning requires external tooling (Docker, Kubernetes, Atlas)."
        )

    def destroy(self, force: bool = False, **kwargs: Any) -> OperationResult:
        """
        Destroy MongoDB infrastructure.

        MongoDB teardown is typically done via container orchestration
        or cloud providers.
        """
        return OperationResult.failure_result(
            "MongoDB teardown requires external tooling (Docker, Kubernetes, Atlas)."
        )

    def get_version(self) -> str:
        """Return MongoDB server version."""
        client: MongoClient = self.connection.client
        server_info = client.server_info()
        return server_info.get("version", "unknown")

    def get_server_time(self) -> datetime:
        """Get current time on the MongoDB server."""
        client: MongoClient = self.connection.client
        result = client.admin.command("serverStatus")
        local_time = result.get("localTime")
        if isinstance(local_time, datetime):
            return local_time
        return datetime.now()

    def list_databases(self) -> list[MongoDBDatabase]:
        """List all databases on this engine."""
        client: MongoClient = self.connection.client
        return [
            MongoDBDatabase(engine=self, name=name)
            for name in client.list_database_names()
        ]

    def get_database(self, name: str) -> MongoDBDatabase:
        """Get a handle to a specific database."""
        return MongoDBDatabase(engine=self, name=name)

    def startup(self, **kwargs: Any) -> OperationResult:
        """Start the database engine (connect)."""
        try:
            self.connection.connect()
            return OperationResult.success_result("Connected to MongoDB")
        except Exception as e:
            return OperationResult.failure_result("Failed to start MongoDB", error=str(e))

    def shutdown(self, force: bool = False, **kwargs: Any) -> OperationResult:
        """
        Shutdown the MongoDB server.

        Sends the shutdown command to the server. Requires appropriate privileges.
        """
        client: MongoClient = self.connection.client
        try:
            client.admin.command("shutdown", force=force)
            return OperationResult.success_result("MongoDB shutdown initiated")
        except Exception as e:
            # Shutdown typically closes the connection, which raises an error
            if "connection closed" in str(e).lower() or "network" in str(e).lower():
                return OperationResult.success_result("MongoDB shutdown initiated")
            return OperationResult.failure_result("Failed to shutdown MongoDB", error=str(e))

    def list_users(self) -> list[str]:
        """List all users on the admin database."""
        client: MongoClient = self.connection.client
        result = client.admin.command("usersInfo")
        return [user["user"] for user in result.get("users", [])]

    def create_user(self, name: str, password: str, **kwargs: Any) -> OperationResult:
        """
        Create a new MongoDB user.

        Args:
            name: Username.
            password: Password.
            **kwargs: Optional 'roles' (list of dicts), 'db' (auth database).
        """
        client: MongoClient = self.connection.client
        db_name = kwargs.get("db", "admin")
        roles = kwargs.get("roles", [{"role": "readWrite", "db": db_name}])
        try:
            client[db_name].command("createUser", name, pwd=password, roles=roles)
            return OperationResult.success_result(f"User '{name}' created on '{db_name}'")
        except OperationFailure as e:
            return OperationResult.failure_result(f"Failed to create user '{name}'", error=str(e))

    def drop_user(self, name: str) -> OperationResult:
        """Drop a MongoDB user from the admin database."""
        client: MongoClient = self.connection.client
        try:
            client.admin.command("dropUser", name)
            return OperationResult.success_result(f"User '{name}' dropped")
        except OperationFailure as e:
            return OperationResult.failure_result(f"Failed to drop user '{name}'", error=str(e))

    def list_processes(self) -> list[dict]:
        """List active operations (currentOp)."""
        client: MongoClient = self.connection.client
        result = client.admin.command("currentOp")
        return [
            {
                "id": op.get("opid"),
                "user": op.get("client", ""),
                "status": op.get("op", "unknown"),
                "duration_ms": op.get("microsecs_running", 0) / 1000,
                "namespace": op.get("ns", ""),
                "waiting_for_lock": op.get("waitingForLock", False),
            }
            for op in result.get("inprog", [])
        ]

    def kill_process(self, process_id: str) -> OperationResult:
        """Kill an active operation."""
        client: MongoClient = self.connection.client
        try:
            client.admin.command("killOp", op=int(process_id))
            return OperationResult.success_result(f"Process {process_id} killed")
        except Exception as e:
            return OperationResult.failure_result(f"Failed to kill process {process_id}", error=str(e))

    def get_configuration(self) -> dict:
        """Get current server configuration parameters."""
        client: MongoClient = self.connection.client
        result = client.admin.command("getParameter", "*")
        return {k: v for k, v in result.items() if k != "ok"}

    def set_configuration(self, key: str, value: Any) -> OperationResult:
        """Set a server configuration parameter."""
        client: MongoClient = self.connection.client
        try:
            client.admin.command("setParameter", **{key: value})
            return OperationResult.success_result(f"Parameter '{key}' set to '{value}'")
        except OperationFailure as e:
            return OperationResult.failure_result(f"Failed to set parameter '{key}'", error=str(e))

    def get_metrics(self, start_time: datetime, end_time: datetime) -> list[Metric]:
        """
        Get engine metrics from serverStatus.

        Note: MongoDB does not natively store time-series metrics.
        This returns a snapshot of current metrics.
        """
        client: MongoClient = self.connection.client
        now = datetime.now()
        status = client.admin.command("serverStatus")
        metrics = []

        connections = status.get("connections", {})
        metrics.append(Metric(
            name="connections_current",
            value=float(connections.get("current", 0)),
            unit="count",
            timestamp=now,
        ))
        metrics.append(Metric(
            name="connections_available",
            value=float(connections.get("available", 0)),
            unit="count",
            timestamp=now,
        ))

        mem = status.get("mem", {})
        metrics.append(Metric(
            name="memory_resident_mb",
            value=float(mem.get("resident", 0)),
            unit="MB",
            timestamp=now,
        ))

        opcounters = status.get("opcounters", {})
        for op_name, op_count in opcounters.items():
            metrics.append(Metric(
                name=f"opcounter_{op_name}",
                value=float(op_count),
                unit="count",
                timestamp=now,
            ))

        return metrics

    def get_logs(self, start_time: datetime, end_time: datetime, **kwargs: Any) -> list[LogEntry]:
        """
        Get engine logs via getLog command.

        Args:
            start_time: Start of time range (used for filtering).
            end_time: End of time range (used for filtering).
            **kwargs: Optional 'log_type' ('global', 'startupWarnings').
        """
        client: MongoClient = self.connection.client
        log_type = kwargs.get("log_type", "global")
        try:
            result = client.admin.command("getLog", log_type)
            entries = []
            for line in result.get("log", []):
                entries.append(LogEntry(
                    timestamp=datetime.now(),
                    level="INFO",
                    message=line,
                    source="mongodb",
                ))
            return entries
        except OperationFailure:
            return []

    def get_replication_status(self) -> ReplicationStatus:
        """Get current replication status."""
        client: MongoClient = self.connection.client
        try:
            rs_status = client.admin.command("replSetGetStatus")
            my_state = rs_status.get("myState", 0)
            role_map = {1: "primary", 2: "secondary", 7: "arbiter"}
            role = role_map.get(my_state, "unknown")

            members = rs_status.get("members", [])
            partners = [m["name"] for m in members if m.get("stateStr") != role_map.get(my_state)]

            # Calculate max lag
            primary_optime = None
            max_lag = 0.0
            for m in members:
                if m.get("stateStr") == "PRIMARY":
                    primary_optime = m.get("optimeDate")
                    break

            if primary_optime:
                for m in members:
                    if m.get("stateStr") == "SECONDARY":
                        secondary_optime = m.get("optimeDate")
                        if secondary_optime:
                            lag = (primary_optime - secondary_optime).total_seconds()
                            max_lag = max(max_lag, lag)

            return ReplicationStatus(
                enabled=True,
                mode="asynchronous",
                role=role,
                lag_seconds=max_lag,
                sync_state="synchronized" if max_lag < 10 else "syncing",
                partners=partners,
            )
        except OperationFailure:
            return ReplicationStatus(
                enabled=False,
                mode="standalone",
                role="standalone",
            )

    def failover(self, target_node: str | None = None, **kwargs: Any) -> OperationResult:
        """Initiate a failover (step down primary)."""
        client: MongoClient = self.connection.client
        step_down_seconds = kwargs.get("step_down_seconds", 60)
        try:
            client.admin.command("replSetStepDown", step_down_seconds)
            return OperationResult.success_result("Primary step-down initiated")
        except OperationFailure as e:
            return OperationResult.failure_result("Failed to initiate failover", error=str(e))
