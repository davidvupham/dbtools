"""
Database entity abstraction.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from .base import OperationResult
from .metadata import BackupType, DatabaseMetadata

if TYPE_CHECKING:
    from .engine import DatabaseEngine


class Database(ABC):
    """
    Abstract base class representing a specific database.

    A database is a logical container of data (tables, views, etc.)
    managed by a DatabaseEngine.
    """

    def __init__(self, engine: "DatabaseEngine", name: str):
        """
        Initialize the database object.

        Args:
            engine: The parent DatabaseEngine.
            name: The name of the database.
        """
        self.engine = engine
        self.name = name
        self._metadata: Optional[DatabaseMetadata] = None

    @property
    @abstractmethod
    def metadata(self) -> DatabaseMetadata:
        """
        Get database metadata.

        Implementations should cache metadata and provide a refresh mechanism.

        Returns:
            DatabaseMetadata object.
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        """
        Check if the database exists on the server.

        Returns:
            True if database exists, False otherwise.
        """
        pass

    @abstractmethod
    def create(self, **options) -> OperationResult:
        """
        Create the database.

        Args:
            **options: Platform-specific creation options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    @abstractmethod
    def drop(self, force: bool = False) -> OperationResult:
        """
        Drop the database.

        Args:
            force: If True, force drop (e.g., close existing connections).

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    @abstractmethod
    def backup(self, path: str, backup_type: BackupType = BackupType.FULL, **options) -> OperationResult:
        """
        Backup the database.

        Args:
            path: Destination path for the backup.
            backup_type: Type of backup (full, diff, log).
            **options: Platform-specific backup options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    @abstractmethod
    def restore(self, path: str, **options) -> OperationResult:
        """
        Restore the database from backup.

        Args:
            path: Source path of the backup file.
            **options: Platform-specific restore options.

        Returns:
            OperationResult indicating success or failure.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"

    def __str__(self) -> str:
        return self.name
