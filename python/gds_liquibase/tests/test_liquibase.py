"""Unit tests for gds_liquibase package."""

import tempfile
from pathlib import Path

import pytest
from gds_liquibase import (
    ChangelogManager,
    ConfigurationError,
    LiquibaseConfig,
    LiquibaseMigrationRunner,
)


class TestLiquibaseConfig:
    """Tests for LiquibaseConfig class."""

    def test_config_from_dict(self):
        """Test creating config with required parameters."""
        config = LiquibaseConfig(
            changelog_file="db.changelog.xml",
            url="jdbc:postgresql://localhost:5432/testdb",
            username="testuser",
            password="testpass",
        )

        assert config.changelog_file == "db.changelog.xml"
        assert config.url == "jdbc:postgresql://localhost:5432/testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.driver == "org.postgresql.Driver"  # Auto-detected

    def test_config_missing_required(self):
        """Test that missing required fields raise ConfigurationError."""
        with pytest.raises(ConfigurationError):
            LiquibaseConfig(
                changelog_file="",
                url="jdbc:postgresql://localhost:5432/testdb",
                username="testuser",
                password="testpass",
            )

    def test_config_driver_detection(self):
        """Test automatic driver detection from URL."""
        configs = [
            ("jdbc:postgresql://localhost/db", "org.postgresql.Driver"),
            (
                "jdbc:sqlserver://localhost;database=db",
                "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            ),
            (
                "jdbc:snowflake://account.snowflakecomputing.com",
                "net.snowflake.client.jdbc.SnowflakeDriver",
            ),
            ("mongodb://localhost:27017/db", "liquibase.ext.mongodb.database.MongoConnection"),
            ("jdbc:h2:mem:test", "org.h2.Driver"),
        ]

        for url, expected_driver in configs:
            config = LiquibaseConfig(
                changelog_file="test.xml",
                url=url,
                username="user",
                password="pass",
            )
            assert config.driver == expected_driver

    def test_config_to_command_args(self):
        """Test conversion to command-line arguments."""
        config = LiquibaseConfig(
            changelog_file="db.changelog.xml",
            url="jdbc:postgresql://localhost:5432/testdb",
            username="testuser",
            password="testpass",
            contexts="dev,test",
            labels="v1.0",
        )

        args = config.to_command_args()

        assert "--changelog-file=db.changelog.xml" in args
        assert "--url=jdbc:postgresql://localhost:5432/testdb" in args
        assert "--username=testuser" in args
        assert "--password=testpass" in args
        assert "--contexts=dev,test" in args
        assert "--labels=v1.0" in args

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("LIQUIBASE_CHANGELOG_FILE", "db.changelog.xml")
        monkeypatch.setenv("LIQUIBASE_URL", "jdbc:postgresql://localhost:5432/testdb")
        monkeypatch.setenv("LIQUIBASE_USERNAME", "testuser")
        monkeypatch.setenv("LIQUIBASE_PASSWORD", "testpass")
        monkeypatch.setenv("LIQUIBASE_CONTEXTS", "dev")

        config = LiquibaseConfig.from_env()

        assert config.changelog_file == "db.changelog.xml"
        assert config.url == "jdbc:postgresql://localhost:5432/testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.contexts == "dev"


class TestChangelogManager:
    """Tests for ChangelogManager class."""

    def test_create_changelog(self):
        """Test creating a new changelog file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            manager = ChangelogManager(tmppath)

            changelog = manager.create_changelog(
                author="test@example.com",
                description="Test changelog",
                output_file=tmppath / "test.xml",
            )

            assert changelog.exists()
            assert changelog.name == "test.xml"

            # Verify it's valid XML
            root = manager.parse_changelog(changelog)
            assert root.tag.endswith("databaseChangeLog")

    def test_list_changesets_empty(self):
        """Test listing changesets from empty changelog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            manager = ChangelogManager(tmppath)

            changelog = manager.create_changelog(
                author="test@example.com",
                description="Empty changelog",
                output_file=tmppath / "empty.xml",
            )

            changesets = manager.list_changesets(changelog)
            assert len(changesets) == 0


def test_version():
    """Test that package version is accessible."""
    from gds_liquibase import __version__

    assert __version__ == "0.1.0"


def test_exports():
    """Test that all expected symbols are exported."""
    from gds_liquibase import (
        ChangelogManager,
        ConfigurationError,
        ExecutionError,
        LiquibaseConfig,
        LiquibaseError,
        ValidationError,
    )

    assert LiquibaseConfig is not None
    assert LiquibaseMigrationRunner is not None
    assert ChangelogManager is not None
    assert LiquibaseError is not None
    assert ConfigurationError is not None
    assert ExecutionError is not None
    assert ValidationError is not None
