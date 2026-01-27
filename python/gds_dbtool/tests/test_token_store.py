"""Tests for secure token storage."""

from __future__ import annotations

from unittest.mock import patch

from gds_dbtool.token_store import (
    delete_token,
    get_token_location,
    load_token,
    save_token,
)


class TestTokenFileStorage:
    """Tests for file-based token storage (fallback)."""

    def test_save_and_load_token(self, tmp_path):
        """Test saving and loading a token from file."""
        token_file = tmp_path / ".dbtool_token"

        with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
            with patch("gds_dbtool.token_store._use_keyring", return_value=False):
                save_token("test-token-123")
                assert token_file.exists()

                loaded = load_token()
                assert loaded == "test-token-123"

    def test_file_permissions(self, tmp_path):
        """Test that token file has restricted permissions."""
        token_file = tmp_path / ".dbtool_token"

        with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
            with patch("gds_dbtool.token_store._use_keyring", return_value=False):
                save_token("test-token")

                # Check file permissions (600 = owner read/write only)
                mode = token_file.stat().st_mode & 0o777
                assert mode == 0o600

    def test_delete_token(self, tmp_path):
        """Test deleting a token."""
        token_file = tmp_path / ".dbtool_token"
        token_file.write_text("test-token")

        with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
            with patch("gds_dbtool.token_store._use_keyring", return_value=False):
                delete_token()
                assert not token_file.exists()

    def test_load_missing_token_returns_none(self, tmp_path):
        """Test that loading missing token returns None."""
        token_file = tmp_path / ".dbtool_token"

        with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
            with patch("gds_dbtool.token_store._use_keyring", return_value=False):
                result = load_token()
                assert result is None

    def test_load_empty_token_returns_none(self, tmp_path):
        """Test that loading empty token file returns None."""
        token_file = tmp_path / ".dbtool_token"
        token_file.write_text("")

        with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
            with patch("gds_dbtool.token_store._use_keyring", return_value=False):
                result = load_token()
                assert result is None


class TestKeyringStorage:
    """Tests for keyring-based token storage."""

    def test_use_keyring_returns_bool(self):
        """Test that _use_keyring returns a boolean."""
        from gds_dbtool.token_store import _use_keyring

        result = _use_keyring()
        assert isinstance(result, bool)

    def test_fallback_to_file_when_keyring_fails(self, tmp_path):
        """Test fallback to file when keyring is unavailable."""
        token_file = tmp_path / ".dbtool_token"
        token_file.write_text("file-token")

        with patch("gds_dbtool.token_store._use_keyring", return_value=False):
            with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
                result = load_token()
                assert result == "file-token"

    def test_token_storage_roundtrip(self, tmp_path):
        """Test that tokens can be saved and loaded."""
        token_file = tmp_path / ".dbtool_token"

        with patch("gds_dbtool.token_store._use_keyring", return_value=False):
            with patch("gds_dbtool.token_store.TOKEN_FILE", token_file):
                save_token("roundtrip-token")
                result = load_token()
                assert result == "roundtrip-token"


class TestGetTokenLocation:
    """Tests for get_token_location function."""

    def test_keyring_location(self):
        """Test location string when using keyring."""
        with patch("gds_dbtool.token_store._use_keyring", return_value=True):
            location = get_token_location()
            assert location == "system keyring"

    def test_file_location(self):
        """Test location string when using file."""
        with patch("gds_dbtool.token_store._use_keyring", return_value=False):
            location = get_token_location()
            assert ".dbtool_token" in location
