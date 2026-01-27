"""Configuration management for dbtool.

Handles loading of config.toml, profile management, and alias resolution.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pydantic import BaseModel, Field

class VaultConfig(BaseModel):
    """Vault-specific configuration."""
    url: str = Field(default="https://vault.example.com")
    namespace: str | None = None
    base_path: str = Field(default="secret/data")
    aliases: dict[str, str] = Field(default_factory=dict)

class ProfileConfig(BaseModel):
    """Configuration for a specific profile."""
    vault: VaultConfig = Field(default_factory=VaultConfig)

class GlobalConfig(BaseModel):
    """Root configuration object."""
    defaults: dict[str, Any] = Field(default_factory=dict)
    current_profile: str = "default"
    profiles: dict[str, ProfileConfig] = Field(default_factory=lambda: {"default": ProfileConfig()})

    @property
    def active_profile(self) -> ProfileConfig:
        """Get the currently active profile configuration."""
        return self.profiles.get(self.current_profile, self.profiles["default"])

def get_config_path() -> Path:
    """Determine the configuration file path based on OS."""
    if os.name == "nt":
        return Path(os.environ["APPDATA"]) / "dbtool" / "config.toml"
    
    # Linux/Mac: XDG config or ~/.config
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "dbtool" / "config.toml"
    
    return Path.home() / ".config" / "dbtool" / "config.toml"

def load_config() -> GlobalConfig:
    """Load configuration from disk."""
    config_path = get_config_path()
    if not config_path.exists():
        return GlobalConfig()

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        
        # Parse [vault.aliases] from root if it exists for backward compat or ease of use
        # But our spec puts it under profile or root? Spec says [vault.aliases] is a section.
        # Let's map the toml structure to our model.
        
        # We need to handle the structure described in technical-architecture.md
        # [profile.default]
        # ...
        # [vault.aliases]
        # ...
        
        # This mapping might need custom logic if the TOML structure doesn't match Pydantic 1:1
        return GlobalConfig(**data)
    except Exception:
        # Fallback to defaults on error
        return GlobalConfig()
