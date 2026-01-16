"""Configuration management for Liquibase operations."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from gds_liquibase.exceptions import ConfigurationError


@dataclass
class LiquibaseConfig:
    """Liquibase configuration settings.

    Attributes:
        changelog_file: Path to the changelog file
        url: Database JDBC URL
        username: Database username
        password: Database password
        driver: JDBC driver class (optional, auto-detected from URL)
        classpath: Additional classpath for JDBC drivers (optional)
        contexts: Comma-separated list of contexts to execute (optional)
        labels: Comma-separated list of labels to execute (optional)
        default_schema: Default schema name (optional)
        liquibase_schema: Schema for Liquibase tracking tables (optional)
        log_level: Logging level (INFO, WARNING, DEBUG, etc.)
        output_file: File to write output to (optional)
    """

    changelog_file: str
    url: str
    username: str
    password: str
    driver: Optional[str] = None
    classpath: Optional[str] = None
    contexts: Optional[str] = None
    labels: Optional[str] = None
    default_schema: Optional[str] = None
    liquibase_schema: Optional[str] = None
    log_level: str = "INFO"
    output_file: Optional[str] = None
    extra_args: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.changelog_file:
            raise ConfigurationError("changelog_file is required")
        if not self.url:
            raise ConfigurationError("url is required")
        if not self.username:
            raise ConfigurationError("username is required")

        # Auto-detect driver from URL if not provided
        if not self.driver:
            self.driver = self._detect_driver()

    def _detect_driver(self) -> str:
        """Auto-detect JDBC driver from URL."""
        url_lower = self.url.lower()

        if "postgresql" in url_lower or "jdbc:postgresql" in url_lower:
            return "org.postgresql.Driver"
        elif "sqlserver" in url_lower or "jdbc:sqlserver" in url_lower:
            return "com.microsoft.sqlserver.jdbc.SQLServerDriver"
        elif "snowflake" in url_lower or "jdbc:snowflake" in url_lower:
            return "net.snowflake.client.jdbc.SnowflakeDriver"
        elif "mongodb" in url_lower or "mongodb://" in url_lower:
            return "liquibase.ext.mongodb.database.MongoConnection"
        elif "h2" in url_lower or "jdbc:h2" in url_lower:
            return "org.h2.Driver"
        else:
            return ""

    @classmethod
    def from_properties_file(cls, properties_file: Path) -> "LiquibaseConfig":
        """Load configuration from liquibase.properties file.

        Args:
            properties_file: Path to the properties file

        Returns:
            LiquibaseConfig instance

        Raises:
            ConfigurationError: If file not found or invalid
        """
        if not properties_file.exists():
            raise ConfigurationError(f"Properties file not found: {properties_file}")

        config: Dict[str, str] = {}
        extra_args: Dict[str, str] = {}

        with open(properties_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Expand environment variables
                    if value.startswith("${") and value.endswith("}"):
                        env_var = value[2:-1]
                        value = os.getenv(env_var, "")

                    # Map to known fields or store in extra_args
                    known_fields = {
                        "changeLogFile",
                        "url",
                        "username",
                        "password",
                        "driver",
                        "classpath",
                        "contexts",
                        "labels",
                        "defaultSchemaName",
                        "liquibaseSchemaName",
                        "logLevel",
                        "outputFile",
                    }

                    if key in known_fields:
                        config[key] = value
                    else:
                        extra_args[key] = value

        return cls(
            changelog_file=config.get("changeLogFile", ""),
            url=config.get("url", ""),
            username=config.get("username", ""),
            password=config.get("password", ""),
            driver=config.get("driver"),
            classpath=config.get("classpath"),
            contexts=config.get("contexts"),
            labels=config.get("labels"),
            default_schema=config.get("defaultSchemaName"),
            liquibase_schema=config.get("liquibaseSchemaName"),
            log_level=config.get("logLevel", "INFO"),
            output_file=config.get("outputFile"),
            extra_args=extra_args,
        )

    @classmethod
    def from_env(cls) -> "LiquibaseConfig":
        """Load configuration from environment variables.

        Environment variables:
            LIQUIBASE_CHANGELOG_FILE
            LIQUIBASE_URL
            LIQUIBASE_USERNAME
            LIQUIBASE_PASSWORD
            LIQUIBASE_DRIVER (optional)
            LIQUIBASE_CONTEXTS (optional)
            LIQUIBASE_LABELS (optional)
            LIQUIBASE_DEFAULT_SCHEMA (optional)
            LIQUIBASE_SCHEMA (optional)
            LIQUIBASE_LOG_LEVEL (optional)

        Returns:
            LiquibaseConfig instance

        Raises:
            ConfigurationError: If required variables are missing
        """
        return cls(
            changelog_file=os.getenv("LIQUIBASE_CHANGELOG_FILE", ""),
            url=os.getenv("LIQUIBASE_URL", ""),
            username=os.getenv("LIQUIBASE_USERNAME", ""),
            password=os.getenv("LIQUIBASE_PASSWORD", ""),
            driver=os.getenv("LIQUIBASE_DRIVER"),
            classpath=os.getenv("LIQUIBASE_CLASSPATH"),
            contexts=os.getenv("LIQUIBASE_CONTEXTS"),
            labels=os.getenv("LIQUIBASE_LABELS"),
            default_schema=os.getenv("LIQUIBASE_DEFAULT_SCHEMA"),
            liquibase_schema=os.getenv("LIQUIBASE_SCHEMA"),
            log_level=os.getenv("LIQUIBASE_LOG_LEVEL", "INFO"),
            output_file=os.getenv("LIQUIBASE_OUTPUT_FILE"),
        )

    def to_command_args(self) -> List[str]:
        """Convert configuration to Liquibase command-line arguments.

        Returns:
            List of command-line arguments
        """
        args = [
            f"--changelog-file={self.changelog_file}",
            f"--url={self.url}",
            f"--username={self.username}",
            f"--password={self.password}",
        ]

        if self.driver:
            args.append(f"--driver={self.driver}")
        if self.classpath:
            args.append(f"--classpath={self.classpath}")
        if self.contexts:
            args.append(f"--contexts={self.contexts}")
        if self.labels:
            args.append(f"--labels={self.labels}")
        if self.default_schema:
            args.append(f"--default-schema-name={self.default_schema}")
        if self.liquibase_schema:
            args.append(f"--liquibase-schema-name={self.liquibase_schema}")
        if self.log_level:
            args.append(f"--log-level={self.log_level}")
        if self.output_file:
            args.append(f"--output-file={self.output_file}")

        # Add extra arguments
        for key, value in self.extra_args.items():
            args.append(f"--{key}={value}")

        return args
