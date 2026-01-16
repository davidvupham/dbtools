import logging
import os
import subprocess
import tempfile

from .constants import DEFAULT_HAMMERDB_CLI_PATH

logger = logging.getLogger(__name__)


class HammerDBExecutor:
    """Executes HammerDB CLI commands."""

    def __init__(self, cli_path: str = DEFAULT_HAMMERDB_CLI_PATH):
        self.cli_path = cli_path

    def run_script(self, script_content: str) -> str:
        """
        Writes the script content to a temp file and executes it with hammerdbcli.

        Returns:
            str: The stdout of the command.

        Raises:
            subprocess.CalledProcessError: If the command fails.
            FileNotFoundError: If the CLI executable is not found.
        """
        if not os.path.isfile(self.cli_path):
            # For development/testing where the tool might not exist,
            # we might want to mock this or raise an error.
            # raising error for now to be explicit.
            raise FileNotFoundError(f"HammerDB CLI not found at: {self.cli_path}")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tcl", delete=False) as temp_script:
            temp_script.write(script_content)
            temp_script_path = temp_script.name

        try:
            logger.info(f"Executing HammerDB script: {temp_script_path}")
            # hammerdbcli auto <script_path>
            # Note: HammerDB CLI behavior might vary slightly by version,
            # but 'hammerdbcli auto' is standard for running a tcl script.
            command = [self.cli_path, "auto", temp_script_path]

            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"HammerDB execution failed. Stderr: {e.stderr}")
            raise
        finally:
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)
