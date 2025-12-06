import importlib.util
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip if aiohttp not installed
if importlib.util.find_spec("aiohttp") is None:
    pytest.skip("aiohttp not installed", allow_module_level=True)

from gds_vault.async_client import AsyncVaultClient
from gds_vault.auth import AsyncAppRoleAuth


@pytest.mark.asyncio
async def test_async_client_initialization():
    # Use mock auth to avoid credential check during intialization
    client = AsyncVaultClient(
        vault_addr="http://localhost:8200", auth=MagicMock(spec=AsyncAppRoleAuth)
    )
    assert not client.is_initialized
    async with client as c:
        assert c.is_initialized
    assert not client.is_initialized


@pytest.mark.asyncio
async def test_async_auth_success():
    with patch("aiohttp.ClientSession.post") as mock_post:
        # Mock response for login
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {
            "auth": {"client_token": "test-token", "lease_duration": 3600}
        }
        mock_post.return_value.__aenter__.return_value = mock_resp

        # Manually create auth with credentials
        auth = AsyncAppRoleAuth(role_id="r", secret_id="s")
        client = AsyncVaultClient(
            vault_addr="http://localhost:8200", auth=auth)

        await client.initialize()
        success = await client.authenticate()
        assert success
        assert client.is_authenticated
        assert client._token == "test-token"

        await client.cleanup()


@pytest.mark.asyncio
async def test_async_get_secret():
    with (
        patch("aiohttp.ClientSession.post") as mock_post,
        patch("aiohttp.ClientSession.get") as mock_get,
    ):
        # Auth mock
        mock_auth_resp = AsyncMock()
        mock_auth_resp.status = 200
        mock_auth_resp.json.return_value = {
            "auth": {"client_token": "t", "lease_duration": 3600}
        }
        mock_post.return_value.__aenter__.return_value = mock_auth_resp

        # Secret mock
        mock_secret_resp = AsyncMock()
        mock_secret_resp.status = 200
        mock_secret_resp.json.return_value = {"data": {"data": {"foo": "bar"}}}
        # raise_for_status should be a sync Mock, not AsyncMock because generally it's sync in aiohttp,
        # but AsyncMock makes everything async.
        # Actually simplest way is to just let it pass or ensure it's not a coroutine.
        mock_secret_resp.raise_for_status = MagicMock()
        mock_get.return_value.__aenter__.return_value = mock_secret_resp

        # Manually create auth with credentials
        auth = AsyncAppRoleAuth(role_id="r", secret_id="s")
        client = AsyncVaultClient(
            vault_addr="http://localhost:8200", auth=auth)

        async with client:
            secret = await client.get_secret("my/secret")
            assert secret == {"foo": "bar"}
