import pytest

class MockDB:
    def __init__(self):
        self.status = "connected"

    def close(self):
        self.status = "closed"

@pytest.fixture(scope="function")
def db():
    """Simulates a database connection."""
    database = MockDB()
    yield database
    database.close()
