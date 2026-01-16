"""Pytest configuration and shared fixtures for gds_liquibase tests."""

import pytest


@pytest.fixture
def sample_changelog_path(tmp_path) -> str:
    """Create a temporary changelog file path for testing."""
    changelog = tmp_path / "changelog.xml"
    changelog.write_text('<?xml version="1.0"?><databaseChangeLog/>')
    return str(changelog)
