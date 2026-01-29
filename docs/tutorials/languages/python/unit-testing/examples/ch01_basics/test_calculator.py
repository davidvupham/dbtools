import pytest
from calculator import add, divide


def test_add_positive_numbers():
    # Arrange
    a, b = 10, 5

    # Act
    result = add(a, b)

    # Assert
    assert result == 15

def test_divide_by_zero():
    # Arrange
    a, b = 10, 0

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        divide(a, b)

    assert str(excinfo.value) == "Cannot divide by zero"
