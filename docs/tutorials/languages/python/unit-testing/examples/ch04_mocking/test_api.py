from unittest.mock import patch
from api_client import get_user_status

@patch("api_client.slow_api_call")
def test_get_user_status_mocks_api(mock_api):
    # Arrange
    # Configure the mock to return specific data WITHOUT sleeping
    mock_api.return_value = {"id": 123, "active": True}
    
    # Act
    status = get_user_status(123)
    
    # Assert
    assert status == "Active User"
    
    # Verify the mock was actually called
    mock_api.assert_called_once_with(123)
