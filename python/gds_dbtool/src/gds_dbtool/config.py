"""Configuration management for dbtool.

Handles loading of config.toml, profile management, and alias resolution.
Configuration follows the schema defined in technical-architecture.md.
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """Authentication configuration."""

    ad_domain: str = Field(default="")
    vault_url: str = Field(default="https://vault.example.com")
    vault_namespace: str | None = None


class VaultConfig(BaseModel):
    """Vault-specific configuration for a profile."""

    url: str = Field(default="https://vault.example.com")
    namespace: str | None = None
    base_path: str = Field(default="secret/data")


class VaultAliases(BaseModel):
    """Vault path aliases for convenience."""

    aliases: dict[str, str] = Field(default_factory=dict)


class DefaultsConfig(BaseModel):
    """Default settings."""

    output_format: str = Field(default="table")


class ProfileConfig(BaseModel):
    """Configuration for a specific profile."""

    vault_url: str = Field(default="https://vault.example.com")
    vault_namespace: str | None = None


class GlobalConfig(BaseModel):
    """Root configuration object matching the TOML schema.

    Example config.toml:
        [auth]
        ad_domain = "CONTOSO"
        vault_url = "https://vault.example.com"
        vault_namespace = "db-ops"

        [defaults]
        output_format = "table"

        [profile.default]
        vault_url = "https://vault.example.com"
        vault_namespace = "db-ops"

        [profile.prod]
        vault_url = "https://vault.example.com"
        vault_namespace = "db-ops-prod"

        [vault.aliases]
        logins = "secret/data/teams/gds/common/logins"
        certs = "secret/data/teams/gds/common/certs"
    """

    auth: AuthConfig = Field(default_factory=AuthConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    current_profile: str = "default"
    profile: dict[str, ProfileConfig] = Field(default_factory=lambda: {"default": ProfileConfig()})
    vault: VaultAliases = Field(default_factory=VaultAliases)

    class ActiveProfile:
        """Helper class for accessing active profile with vault config."""

        def __init__(self, config: "GlobalConfig") -> None:
            self._config = config

        @property
        def vault(self) -> VaultConfig:
            """Get vault config from active profile merged with auth."""
            profile = self._config.profile.get(
                self._config.current_profile,
                self._config.profile.get("default", ProfileConfig()),
            )
            return VaultConfig(
                url=profile.vault_url or self._config.auth.vault_url,
                namespace=profile.vault_namespace or self._config.auth.vault_namespace,
                base_path="secret/data",
            )

        @property
        def aliases(self) -> dict[str, str]:
            """Get vault aliases."""
            return self._config.vault.aliases

    @property
    def active_profile(self) -> ActiveProfile:
        """Get the currently active profile configuration."""
        return self.ActiveProfile(self)


def get_config_path() -> Path:
    """Determine the configuration file path based on OS.

    Returns:
        Path to config.toml following platform conventions:
        - Windows: %APPDATA%/dbtool/config.toml
        - Linux/Mac: ~/.config/dbtool/config.toml (or XDG_CONFIG_HOME)
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "dbtool" / "config.toml"

    # Linux/Mac: XDG config or ~/.config
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "dbtool" / "config.toml"

    return Path.home() / ".config" / "dbtool" / "config.toml"


def get_log_dir() -> Path:
    """Determine the log directory based on OS.

    Returns:
        Path to log directory following platform conventions:
        - Windows: %APPDATA%/dbtool/logs/
        - Linux/Mac: ~/.local/state/dbtool/logs/
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "dbtool" / "logs"

    # Linux/Mac: XDG state or ~/.local/state
    xdg_state = os.getenv("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state) / "dbtool" / "logs"

    return Path.home() / ".local" / "state" / "dbtool" / "logs"


def load_config() -> GlobalConfig:
    """Load configuration from disk.

    Configuration precedence (highest to lowest):
    1. CLI flags (handled in main.py)
    2. Environment variables (handled in main.py)
    3. Configuration file
    4. Built-in defaults

    Returns:
        GlobalConfig instance with merged configuration.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return GlobalConfig()

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)

        return GlobalConfig(**data)
    except Exception:
        # Fallback to defaults on error
        return GlobalConfig()


def save_config(config: GlobalConfig) -> None:
    """Save configuration to disk.

    Args:
        config: Configuration to save.
    """
    import tomli_w

    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "wb") as f:
        tomli_w.dump(config.model_dump(exclude_none=True), f)


def resolve_vault_path(config: GlobalConfig, path_input: str | None) -> str:
    """Resolve alias or relative path to full Vault path.

    Args:
        config: Global configuration.
        path_input: Path or alias to resolve.

    Returns:
        Resolved full path.
    """
    if not path_input:
        return config.active_profile.vault.base_path

    # Check if it's an alias
    aliases = config.active_profile.aliases
    if path_input in aliases:
        return aliases[path_input]

    # If path doesn't contain '/', treat as relative to base_path
    if "/" not in path_input:
        base = config.active_profile.vault.base_path.rstrip("/")
        return f"{base}/{path_input}"

    return path_input
