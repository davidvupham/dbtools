"""
Database Engine abstraction.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from .base import DatabaseConnection, OperationResult
from .database import Database

if TYPE_CHECKING:
    from .metadata import EngineMetadata, LogEntry, Metric, ReplicationStatus


class DatabaseEngine(ABC):
    """
    Abstract base class representing a database engine (server/cluster).

    The engine is the entry point for database administration and management.
    It represents the server instance (e.g., MSSQL Server, Snowflake Account).
    """

    def __init__(self, connection: DatabaseConnection):
        """
        Initialize the database engine.

        Args:
            connection: The underlying database connection.
        """
        self.connection = connection

    @property
    @abstractmethod
    def metadata(self) -> "EngineMetadata":
        """
        Get engine metadata.

        Returns:
            EngineMetadata object.
        """
        pass

    # ============================================
    # LIFECYCLE MANAGEMENT
    # ============================================

    @abstractmethod
    def build(self, **kwargs) -> OperationResult:
        """
        Build/provision the database engine infrastructure.

        This method creates and initializes the database engine, including:
        - Starting database processes/containers
        - Configuring networking and storage
        - Initializing system databases
        - Setting up high availability (if applicable)

        Args:
            **kwargs: Platform-specific build options

        Returns:
            OperationResult indicating success or failure

        Example:
            >>> engine = MSSQLEngine(config)
            >>> result = engine.build(docker=True, replicas=3)
        """
        pass

    @abstractmethod
    def destroy(self, force: bool = False, **kwargs) -> OperationResult:
        """
        Destroy/teardown the database engine infrastructure.

        This method removes the database engine, including:
        - Stopping database processes/containers
        - Removing volumes and data (if specified)
        - Cleaning up networking resources

        Args:
            force: If True, forcefully destroy without graceful shutdown
            **kwargs: Platform-specific destroy options

        Returns:
            OperationResult indicating success or failure

        Warning:
            This operation is destructive and may result in data loss.
            Ensure proper backups exist before calling.

        Example:
            >>> result = engine.destroy(force=False, remove_volumes=True)
        """
        pass

    # ============================================
    # DATABASE OPERATIONS
    # ============================================

    @abstractmethod
    def get_version(self) -> str:
        """
        Return server version information.

        Returns:
            String containing version details.
        """
        pass

    @abstractmethod
    def get_server_time(self) -> datetime:
        """
        Get the current time on the database server.

        Returns:
            datetime object representing server time.
        """
        pass

    @abstractmethod
    def list_databases(self) -> List["Database"]:
        """
        List all databases on this engine.

        Returns:
            List of Database objects.
        """
        pass

    @abstractmethod
    def get_database(self, name: str) -> "Database":
        """
        Get a handle to a specific database.

        This method returns a Database object regardless of whether the
        database actually exists on the server. Use Database.exists()
        to check for existence.

        Args:
            name: Name of the database.

        Returns:
            Database object.
        """
        pass

    # Lifecycle Management
    @abstractmethod
    def startup(self, **kwargs) -> "OperationResult":
        """
        Start the database engine.

        Args:
            **kwargs: Platform-specific startup options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    @abstractmethod
    def shutdown(self, force: bool = False, **kwargs) -> "OperationResult":
        """
        Stop the database engine.

        Args:
            force: If True, force shutdown (e.g., kill connections).
            **kwargs: Platform-specific shutdown options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    # User Management
    @abstractmethod
    def list_users(self) -> List[str]:
        """
        List all users/logins on the engine.

        Returns:
            List of usernames.
        """
        pass

    @abstractmethod
    def create_user(self, name: str, password: str, **kwargs) -> "OperationResult":
        """
        Create a new user/login.

        Args:
            name: Username.
            password: Password.
            **kwargs: Platform-specific options (roles, etc.).

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    @abstractmethod
    def drop_user(self, name: str) -> "OperationResult":
        """
        Drop a user/login.

        Args:
            name: Username to drop.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    # Process Management
    @abstractmethod
    def list_processes(self) -> List[dict]:
        """
        List active processes/sessions.

        Returns:
            List of dictionaries containing process info (id, user, status, etc.).
        """
        pass

    @abstractmethod
    def kill_process(self, process_id: str) -> "OperationResult":
        """
        Terminate a process/session.

        Args:
            process_id: ID of the process to kill.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    # Configuration
    @abstractmethod
    def get_configuration(self) -> dict:
        """
        Get current server configuration.

        Returns:
            Dictionary of configuration parameters and values.
        """
        pass

    @abstractmethod
    def set_configuration(self, key: str, value: Any) -> "OperationResult":
        """
        Update server configuration.

        Args:
            key: Configuration parameter name.
            value: New value.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    # Observability
    @abstractmethod
    def get_metrics(self, start_time: datetime, end_time: datetime) -> List["Metric"]:
        """
        Get engine metrics (CPU, Memory, Connections, etc.).

        Args:
            start_time: Start of the time range.
            end_time: End of the time range.

        Returns:
            List of Metric objects.
        """
        pass

    @abstractmethod
    def get_logs(self, start_time: datetime, end_time: datetime, **kwargs) -> List["LogEntry"]:
        """
        Get engine logs.

        Args:
            start_time: Start of the time range.
            end_time: End of the time range.
            **kwargs: Filtering options (level, source, etc.).

        Returns:
            List of LogEntry objects.
        """
        pass

    # High Availability & Disaster Recovery
    @abstractmethod
    def get_replication_status(self) -> "ReplicationStatus":
        """
        Get current replication status.

        Returns:
            ReplicationStatus object.
        """
        pass

    @abstractmethod
    def failover(self, target_node: Optional[str] = None, **kwargs) -> "OperationResult":
        """
        Initiate a failover to a standby node.

        Args:
            target_node: Optional specific node to failover to.
            **kwargs: Platform-specific failover options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass
