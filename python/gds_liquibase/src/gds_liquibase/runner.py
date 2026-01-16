"""Liquibase command execution wrapper."""

import logging
import shutil
import subprocess
from typing import List, Optional

from gds_liquibase.config import LiquibaseConfig
from gds_liquibase.exceptions import ExecutionError, LiquibaseNotFoundError

logger = logging.getLogger(__name__)


class LiquibaseMigrationRunner:
    """Execute Liquibase commands with Python.

    This class provides a Python wrapper around the Liquibase CLI,
    allowing you to execute database migrations programmatically.

    Example:
        >>> config = LiquibaseConfig.from_env()
        >>> runner = LiquibaseMigrationRunner(config)
        >>> runner.update()
    """

    def __init__(self, config: LiquibaseConfig, liquibase_path: Optional[str] = None):
        """Initialize the migration runner.

        Args:
            config: Liquibase configuration
            liquibase_path: Optional path to liquibase executable
        """
        self.config = config
        self.liquibase_path = liquibase_path or self._find_liquibase()

    def _find_liquibase(self) -> str:
        """Find the Liquibase executable on the system.

        Returns:
            Path to liquibase executable

        Raises:
            LiquibaseNotFoundError: If liquibase is not found
        """
        liquibase = shutil.which("liquibase")
        if not liquibase:
            raise LiquibaseNotFoundError(
                "Liquibase executable not found in PATH. "
                "Please install Liquibase or provide liquibase_path."
            )
        return liquibase

    def _build_base_args(self) -> List[str]:
        """Build base command arguments.

        Returns:
            List of base arguments including liquibase path and config
        """
        return [self.liquibase_path] + self.config.to_command_args()

    def _execute(self, args: List[str]) -> subprocess.CompletedProcess:
        """Execute Liquibase command.

        Args:
            args: Complete command arguments

        Returns:
            CompletedProcess instance

        Raises:
            ExecutionError: If command fails
        """
        logger.info(f"Executing: {' '.join(args)}")

        result = subprocess.run(args, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            raise ExecutionError(f"Liquibase command failed: {result.stderr or result.stdout}")

        logger.info(f"Command output: {result.stdout}")
        return result

    def update(
        self, contexts: Optional[str] = None, labels: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Execute liquibase update command.

        Args:
            contexts: Override contexts from config
            labels: Override labels from config

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("update")

        if contexts:
            args.extend(["--contexts", contexts])
        if labels:
            args.extend(["--labels", labels])

        return self._execute(args)

    def rollback(self, tag: str) -> subprocess.CompletedProcess:
        """Rollback database to specified tag.

        Args:
            tag: Tag name to rollback to

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(["rollback", tag])
        return self._execute(args)

    def rollback_count(self, count: int) -> subprocess.CompletedProcess:
        """Rollback a specific number of changesets.

        Args:
            count: Number of changesets to rollback

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(["rollback-count", str(count)])
        return self._execute(args)

    def validate(self) -> subprocess.CompletedProcess:
        """Validate changelog files.

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("validate")
        return self._execute(args)

    def status(self, verbose: bool = False) -> subprocess.CompletedProcess:
        """Get migration status.

        Args:
            verbose: Include verbose output

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("status")
        if verbose:
            args.append("--verbose")
        return self._execute(args)

    def tag(self, tag_name: str) -> subprocess.CompletedProcess:
        """Tag current database state.

        Args:
            tag_name: Name for the tag

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(["tag", tag_name])
        return self._execute(args)

    def update_sql(self, output_file: Optional[str] = None) -> subprocess.CompletedProcess:
        """Generate SQL for update without executing.

        Args:
            output_file: Optional file to write SQL to

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("update-sql")

        if output_file:
            args.extend([">", output_file])

        return self._execute(args)

    def rollback_sql(
        self, tag: str, output_file: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Generate SQL for rollback without executing.

        Args:
            tag: Tag to rollback to
            output_file: Optional file to write SQL to

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(["rollback-sql", tag])

        if output_file:
            args.extend([">", output_file])

        return self._execute(args)

    def generate_changelog(self, output_file: str) -> subprocess.CompletedProcess:
        """Generate changelog from existing database.

        Args:
            output_file: File to write changelog to

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(["generate-changelog", f"--changelog-file={output_file}"])
        return self._execute(args)

    def diff(
        self,
        reference_url: str,
        reference_username: str,
        reference_password: str,
    ) -> subprocess.CompletedProcess:
        """Compare databases.

        Args:
            reference_url: Reference database JDBC URL
            reference_username: Reference database username
            reference_password: Reference database password

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(
            [
                "diff",
                f"--reference-url={reference_url}",
                f"--reference-username={reference_username}",
                f"--reference-password={reference_password}",
            ]
        )
        return self._execute(args)

    def diff_changelog(
        self,
        reference_url: str,
        reference_username: str,
        reference_password: str,
        output_file: str,
    ) -> subprocess.CompletedProcess:
        """Generate changelog of differences between databases.

        Args:
            reference_url: Reference database JDBC URL
            reference_username: Reference database username
            reference_password: Reference database password
            output_file: File to write changelog to

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.extend(
            [
                "diff-changelog",
                f"--changelog-file={output_file}",
                f"--reference-url={reference_url}",
                f"--reference-username={reference_username}",
                f"--reference-password={reference_password}",
            ]
        )
        return self._execute(args)

    def clear_checksums(self) -> subprocess.CompletedProcess:
        """Clear all checksums in the DATABASECHANGELOG table.

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("clear-checksums")
        return self._execute(args)

    def changelog_sync(self) -> subprocess.CompletedProcess:
        """Mark all changes as executed in the database.

        Returns:
            CompletedProcess instance
        """
        args = self._build_base_args()
        args.append("changelog-sync")
        return self._execute(args)
