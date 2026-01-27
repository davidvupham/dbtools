"""Shared helper functions for command modules.

Provides lazy-access helpers for global application state to avoid
circular imports between command modules and the main module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


def get_console() -> Console:
    """Get the Rich console from app state."""
    from ..main import state

    return state.console


def is_quiet() -> bool:
    """Check if quiet mode is enabled."""
    from ..main import state

    return state.quiet


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from ..main import state

    return state.dry_run
