"""Liquibase command execution wrapper."""

import logging
import shutil
import subprocess
from typing import List, Optional

from liquibase_config import LiquibaseConfig

logger = logging.getLogger(__name__)


class LiquibaseMigrationRunner:
    """Execute Liquibase commands with Python."""

    def __init__(self, config: LiquibaseConfig):
        self.config = config
        self.liquibase_path = self._find_liquibase()

    def _find_liquibase(self) -> str:
        """Find the Liquibase executable on the system."""
        liquibase = shutil.which("liquibase")
        if not liquibase:
            raise RuntimeError("Liquibase executable not found in PATH")
        return liquibase

    def _build_base_args(self) -> List[str]:
        """Build base command arguments."""
        return [self.liquibase_path] + self.config.to_command_args()

    def _execute(self, args: List[str]) -> subprocess.CompletedProcess:
        """Execute Liquibase command."""
        logger.info(f"Executing: {' '.join(args)}")
        result = subprocess.run(args, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            raise subprocess.CalledProcessError(
                result.returncode, args, result.stdout, result.stderr
            )

        logger.info(f"Command output: {result.stdout}")
        return result

    def update(
        self, contexts: Optional[str] = None, labels: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Execute liquibase update command."""
        args = self._build_base_args()
        args.append("update")

        if contexts:
            args.extend(["--contexts", contexts])
        if labels:
            args.extend(["--labels", labels])

        return self._execute(args)

    def rollback(self, tag: str) -> subprocess.CompletedProcess:
        """Rollback database to specified tag."""
        args = self._build_base_args()
        args.extend(["rollback", tag])
        return self._execute(args)

    def validate(self) -> subprocess.CompletedProcess:
        """Validate changelog files."""
        args = self._build_base_args()
        args.append("validate")
        return self._execute(args)

    def status(self, verbose: bool = False) -> subprocess.CompletedProcess:
        """Get migration status."""
        args = self._build_base_args()
        args.append("status")
        if verbose:
            args.append("--verbose")
        return self._execute(args)

    def tag(self, tag_name: str) -> subprocess.CompletedProcess:
        """Tag current database state."""
        args = self._build_base_args()
        args.extend(["tag", tag_name])
        return self._execute(args)

    def generate_changelog(self, output_file: str) -> subprocess.CompletedProcess:
        """Generate changelog from existing database."""
        args = self._build_base_args()
        args.extend(["generate-changelog", f"--changelog-file={output_file}"])
        return self._execute(args)

    def diff(
        self, reference_url: str, reference_username: str, reference_password: str
    ) -> subprocess.CompletedProcess:
        """Compare databases."""
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
