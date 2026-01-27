"""Shared fixtures for dbtool unit tests."""

from __future__ import annotations

import pytest
from gds_dbtool.main import app
from typer.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CliRunner instance."""
    return CliRunner()


@pytest.fixture
def invoke(cli_runner: CliRunner):
    """Shortcut to invoke the CLI app."""

    def _invoke(args: list[str], **kwargs):
        return cli_runner.invoke(app, args, **kwargs)

    return _invoke
