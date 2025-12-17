# Testing in Python

## Frameworks

* **unittest**: Built-in, Java-style classes.
* **pytest**: Third-party, function-based, powerful fixtures. (Recommended)

## Pytest Basics

```python
# test_math.py
def test_addition():
    assert 1 + 1 == 2

def test_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

## Fixtures

```python
@pytest.fixture
def database():
    db = connect_db()
    yield db
    db.close()

def test_query(database):
    assert database.query("SELECT 1")
```
