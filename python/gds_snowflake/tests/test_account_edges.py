"""
Additional edge-case tests for gds_snowflake.account
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gds_snowflake.account import AccountInfo, SnowflakeAccount


def test_get_current_account_empty_raises(tmp_path):
    """get_current_account raises ValueError when no rows are returned."""
    mock_conn = MagicMock()
    mock_conn.execute_query_dict.return_value = []

    mgr = SnowflakeAccount(mock_conn, data_dir=str(tmp_path))

    with pytest.raises(ValueError, match="No account information returned"):
        mgr.get_current_account()


def test_list_saved_account_files_error_returns_empty(tmp_path, monkeypatch):
    """Return empty list when data_dir.glob raises during file listing."""
    mgr = SnowflakeAccount(MagicMock(), data_dir=str(tmp_path))

    def boom(*args, **kwargs):
        raise OSError("read error")

    # default ok
    monkeypatch.setattr(
        Path,
        "glob",
        lambda *_: (_ for _ in ()),
    )
    # Simulate exception when listing by patching
    # data_dir.glob on this instance
    with patch.object(mgr, "data_dir", wraps=mgr.data_dir) as p:
        p.glob.side_effect = boom
        files = mgr.list_saved_account_files()
        assert files == []


def test_ensure_data_directory_error(tmp_path):
    """Constructor propagates OSError if data directory cannot be created."""
    # Force mkdir to raise to hit error handling
    mock_conn = MagicMock()

    def raise_mkdir(self, *args, **kwargs):  # self is Path
        raise OSError("cannot create dir")

    with patch.object(Path, "mkdir", raise_mkdir), pytest.raises(OSError, match="cannot create dir"):
        SnowflakeAccount(mock_conn, data_dir=str(tmp_path / "a" / "b"))


def test_load_accounts_roundtrip(tmp_path):
    """
    Save then load accounts JSON and ensure names are preserved in order.
    """
    mock_conn = MagicMock()
    mgr = SnowflakeAccount(mock_conn, data_dir=str(tmp_path))
    accounts = [
        AccountInfo(account_name="A", is_org_admin=True),
        AccountInfo(account_name="B", is_org_admin=False),
    ]
    path = mgr.save_accounts_to_json(accounts, filename="acc.json")
    loaded = mgr.load_accounts_from_json(path.name)
    assert [a.account_name for a in loaded] == ["A", "B"]
