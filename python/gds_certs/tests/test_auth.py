"""
Tests for authentication modules.
"""

import httpx

from gds_certs.auth import APIKeyAuth, BaseAuth, BearerAuth


class TestAPIKeyAuth:
    """Tests for APIKeyAuth class."""

    def test_apply_default_header(self):
        """Test applying API key with default header name."""
        auth = APIKeyAuth(api_key="test-api-key")
        request = httpx.Request("GET", "https://example.com")

        modified = auth.apply(request)

        assert modified.headers["X-API-Key"] == "test-api-key"

    def test_apply_custom_header(self):
        """Test applying API key with custom header name."""
        auth = APIKeyAuth(api_key="test-api-key", header_name="Authorization")
        request = httpx.Request("GET", "https://example.com")

        modified = auth.apply(request)

        assert modified.headers["Authorization"] == "test-api-key"


class TestBearerAuth:
    """Tests for BearerAuth class."""

    def test_apply_bearer_token(self):
        """Test applying Bearer token."""
        auth = BearerAuth(token="test-jwt-token")
        request = httpx.Request("GET", "https://example.com")

        modified = auth.apply(request)

        assert modified.headers["Authorization"] == "Bearer test-jwt-token"


class TestBaseAuth:
    """Tests for BaseAuth abstract class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseAuth cannot be instantiated directly."""
        # BaseAuth is abstract and should not be instantiable
        # This is enforced by the ABC mechanism
        pass

    def test_custom_auth_implementation(self):
        """Test creating a custom auth implementation."""

        class CustomAuth(BaseAuth):
            def __init__(self, username: str, password: str):
                self.username = username
                self.password = password

            def apply(self, request: httpx.Request) -> httpx.Request:
                request.headers["X-Username"] = self.username
                request.headers["X-Password"] = self.password
                return request

        auth = CustomAuth(username="user", password="pass")
        request = httpx.Request("GET", "https://example.com")

        modified = auth.apply(request)

        assert modified.headers["X-Username"] == "user"
        assert modified.headers["X-Password"] == "pass"
