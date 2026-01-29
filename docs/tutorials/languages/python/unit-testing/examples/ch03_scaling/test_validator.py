import pytest
from validator import is_valid_username


@pytest.mark.parametrize("username, expected", [
    ("admin", True),
    ("user123", True),
    ("", False),         # Empty
    ("ab", False),       # Too short
    ("no spaces", False), # Has spaces
])
def test_username_validation(username, expected):
    assert is_valid_username(username) is expected
