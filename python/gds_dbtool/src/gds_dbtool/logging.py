"""Logging configuration for dbtool.

Provides rotating file-based logging for post-mortem analysis.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import get_log_dir

# Logger for the dbtool package
logger = logging.getLogger("dbtool")

# Default log settings
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_NAME = "dbtool.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5


def setup_file_logging(debug: bool = False) -> None:
    """Configure file-based rotating logging.

    Creates a rotating log file at the platform-appropriate location:
    - Windows: %APPDATA%/dbtool/logs/dbtool.log
    - Linux: ~/.local/state/dbtool/logs/dbtool.log

    Args:
        debug: If True, log at DEBUG level; otherwise INFO.
    """
    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    # Create rotating file handler
    handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    handler.setLevel(logging.DEBUG if debug else logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Also configure the dbtool logger specifically
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


def get_log_file_path() -> Path:
    """Get the path to the current log file.

    Returns:
        Path to the dbtool.log file.
    """
    return get_log_dir() / LOG_FILE_NAME


def log_command_start(command: str, args: dict) -> None:
    """Log the start of a command execution.

    Args:
        command: The command being executed.
        args: Command arguments (sensitive values should be masked).
    """
    # Mask sensitive values
    safe_args = {k: "****" if "password" in k.lower() or "token" in k.lower() else v for k, v in args.items()}
    logger.info(f"Command started: {command} with args: {safe_args}")


def log_command_end(command: str, exit_code: int, duration_ms: float) -> None:
    """Log the end of a command execution.

    Args:
        command: The command that was executed.
        exit_code: The exit code of the command.
        duration_ms: Duration in milliseconds.
    """
    logger.info(f"Command completed: {command}, exit_code={exit_code}, duration={duration_ms:.2f}ms")


def log_vault_operation(operation: str, path: str, success: bool) -> None:
    """Log a Vault operation.

    Args:
        operation: The operation type (list, get, put, delete).
        path: The Vault path (may be redacted).
        success: Whether the operation succeeded.
    """
    status = "success" if success else "failed"
    logger.info(f"Vault {operation}: {path} - {status}")


def log_database_query(target: str, query_type: str, reason: str | None = None) -> None:
    """Log a database query execution.

    Args:
        target: Target database identifier.
        query_type: Type of query (select, execute, script).
        reason: Audit reason if provided.
    """
    msg = f"Database query: target={target}, type={query_type}"
    if reason:
        msg += f", reason={reason}"
    logger.info(msg)
