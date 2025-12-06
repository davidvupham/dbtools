from unittest.mock import MagicMock, patch


from gds_vault import VaultClient


class MockMetrics:
    def __init__(self):
        self.counts = {}
        self.timings = {}

    def increment(self, name, value=1, labels=None):
        key = name
        self.counts[key] = self.counts.get(key, 0) + value

    def gauge(self, name, value, labels=None):
        pass

    def histogram(self, name, value, labels=None):
        pass

    def timing(self, name, value_ms, labels=None):
        key = name
        self.timings[key] = value_ms


@patch("requests.post")
@patch("requests.get")
def test_metrics_integration(mock_get, mock_post):
    # Setup mocks
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "auth": {"client_token": "test-token", "lease_duration": 3600}
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": {"data": {"foo": "bar"}}}

    metrics = MockMetrics()

    client = VaultClient(
        vault_addr="http://localhost:8200", auth=MagicMock(), metrics=metrics
    )

    # Mock auth strategy to return token
    client._auth.authenticate.return_value = ("test-token", 3600)

    # Authenticate
    client.authenticate()
    assert metrics.counts.get("vault.auth.success") == 1

    # Get secret
    client.get_secret("test/secret")
    assert metrics.counts.get("vault.secret.hit") == 1
    assert "vault.secret.fetch" in metrics.timings
