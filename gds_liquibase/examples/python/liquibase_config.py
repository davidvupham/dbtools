"""Configuration management for Liquibase operations."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class LiquibaseConfig:
    """Liquibase configuration settings."""

    changelog_file: str
    url: str
    username: str
    password: str
    driver: Optional[str] = None
    classpath: Optional[str] = None
    contexts: Optional[str] = None
    labels: Optional[str] = None

    @classmethod
    def from_properties_file(cls, properties_file: Path) -> "LiquibaseConfig":
        """Load configuration from liquibase.properties file."""
        config = {}
        with open(properties_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

        return cls(
            changelog_file=config.get("changeLogFile", ""),
            url=config.get("url", ""),
            username=config.get("username", ""),
            password=os.getenv(config.get("password", "").replace("${", "").replace("}", ""), ""),
            driver=config.get("driver"),
            contexts=config.get("contexts"),
            labels=config.get("labels"),
        )

    @classmethod
    def from_env(cls) -> "LiquibaseConfig":
        """Load configuration from environment variables."""
        return cls(
            changelog_file=os.getenv("LIQUIBASE_CHANGELOG_FILE", ""),
            url=os.getenv("LIQUIBASE_URL", ""),
            username=os.getenv("LIQUIBASE_USERNAME", ""),
            password=os.getenv("LIQUIBASE_PASSWORD", ""),
            driver=os.getenv("LIQUIBASE_DRIVER"),
            contexts=os.getenv("LIQUIBASE_CONTEXTS"),
            labels=os.getenv("LIQUIBASE_LABELS"),
        )

    def to_command_args(self) -> List[str]:
        """Convert configuration to Liquibase command-line arguments."""
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

        return args
