def add(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divides integers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
