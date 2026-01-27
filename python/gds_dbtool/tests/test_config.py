"""Tests for configuration management."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gds_dbtool.config import (
    GlobalConfig,
    ProfileConfig,
    VaultConfig,
    AuthConfig,
    get_config_path,
    get_log_dir,
    load_config,
    resolve_vault_path,
)


class TestConfigPath:
    """Tests for configuration path resolution."""

    def test_linux_config_path(self):
        """Test config path on Linux."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.name", "posix"):
                path = get_config_path()
                assert ".config/dbtool/config.toml" in str(path)

    def test_linux_xdg_config_path(self):
        """Test config path with XDG_CONFIG_HOME on Linux."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            with patch("os.name", "posix"):
                path = get_config_path()
                assert path == Path("/custom/config/dbtool/config.toml")

    def test_config_path_contains_dbtool(self):
        """Test that config path contains dbtool directory."""
        # This tests the actual behavior on current platform
        path = get_config_path()
        assert "dbtool" in str(path)
        assert "config.toml" in str(path)


class TestLogDir:
    """Tests for log directory resolution."""

    def test_linux_log_dir(self):
        """Test log directory on Linux."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.name", "posix"):
                path = get_log_dir()
                assert ".local/state/dbtool/logs" in str(path)

    def test_linux_xdg_state_dir(self):
        """Test log directory with XDG_STATE_HOME."""
        with patch.dict(os.environ, {"XDG_STATE_HOME": "/custom/state"}):
            with patch("os.name", "posix"):
                path = get_log_dir()
                assert path == Path("/custom/state/dbtool/logs")


class TestGlobalConfig:
    """Tests for GlobalConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GlobalConfig()
        assert config.current_profile == "default"
        assert "default" in config.profile
        assert config.defaults.output_format == "table"

    def test_active_profile_vault(self):
        """Test active profile vault configuration."""
        config = GlobalConfig()
        vault = config.active_profile.vault
        assert isinstance(vault, VaultConfig)
        assert vault.url == "https://vault.example.com"

    def test_custom_profile(self):
        """Test custom profile configuration."""
        config = GlobalConfig(
            profile={
                "default": ProfileConfig(vault_url="https://vault.default.com"),
                "prod": ProfileConfig(
                    vault_url="https://vault.prod.com",
                    vault_namespace="prod-ns",
                ),
            },
            current_profile="prod",
        )
        vault = config.active_profile.vault
        assert vault.url == "https://vault.prod.com"
        assert vault.namespace == "prod-ns"


class TestResolveVaultPath:
    """Tests for Vault path resolution."""

    def test_resolve_alias(self):
        """Test resolving a path alias."""
        config = GlobalConfig()
        config.vault.aliases = {"logins": "secret/data/teams/gds/logins"}

        result = resolve_vault_path(config, "logins")
        assert result == "secret/data/teams/gds/logins"

    def test_resolve_full_path(self):
        """Test that full paths are returned unchanged."""
        config = GlobalConfig()
        result = resolve_vault_path(config, "secret/data/mypath")
        assert result == "secret/data/mypath"

    def test_resolve_relative_path(self):
        """Test that relative paths are appended to base_path."""
        config = GlobalConfig()
        result = resolve_vault_path(config, "mykey")
        assert result == "secret/data/mykey"

    def test_resolve_none_returns_base_path(self):
        """Test that None returns the base path."""
        config = GlobalConfig()
        result = resolve_vault_path(config, None)
        assert result == "secret/data"


class TestLoadConfig:
    """Tests for loading configuration from file."""

    def test_load_missing_config_returns_default(self, tmp_path):
        """Test that missing config file returns defaults."""
        with patch("gds_dbtool.config.get_config_path", return_value=tmp_path / "missing.toml"):
            config = load_config()
            assert config.current_profile == "default"

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid config file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[auth]
vault_url = "https://custom-vault.com"
ad_domain = "TESTDOMAIN"

[defaults]
output_format = "json"

[profile.default]
vault_url = "https://custom-vault.com"

[vault.aliases]
myalias = "secret/data/test"
""")

        with patch("gds_dbtool.config.get_config_path", return_value=config_file):
            config = load_config()
            assert config.auth.vault_url == "https://custom-vault.com"
            assert config.auth.ad_domain == "TESTDOMAIN"
            assert config.defaults.output_format == "json"
            assert config.vault.aliases["myalias"] == "secret/data/test"

    def test_load_invalid_config_returns_default(self, tmp_path):
        """Test that invalid config file returns defaults."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("invalid toml {{{{")

        with patch("gds_dbtool.config.get_config_path", return_value=config_file):
            config = load_config()
            # Should return defaults on error
            assert config.current_profile == "default"
