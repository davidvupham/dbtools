# FastAPI Tutorial

**Level**: Intermediate
**Category**: Web Framework

**FastAPI** is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.

## 📦 Installation

To install FastAPI and the standard server (Uvicorn), run:

```bash
pip install "fastapi[standard]"
```

## 🚀 Basic Usage

FastAPI uses Python type hints to validate, serialize, and deserialize data, and to automatically generate OpenAPI documentation.

### Hello World

Create a file named `01_hello_world.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

Run the server:

```bash
fastapi dev 01_hello_world.py
```

Or using `uvicorn` directly:

```bash
uvicorn 01_hello_world:app --reload
```

Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000). You will see the JSON response:

```json
{"message": "Hello World"}
```

## 🔑 Key Concepts

### Automatic Documentation

FastAPI automatically generates interactive API documentation (using Swagger UI) based on your standard Python type hints.

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see the interactive API docs.

### Path Parameters & Query Parameters

You can declare path parameters and query parameters with type hints.

```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

- `item_id`: Path parameter (typed as `int`).
- `q`: Query parameter (typed as `Union[str, None]`, default is `None`).

### Request Body & Pydantic models

Use [Pydantic](https://docs.pydantic.dev/) models to declare request bodies.

```python
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

app = FastAPI()

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
```

## 🧠 Advanced Features

### Dependency Injection

FastAPI has a very powerful but intuitive **Dependency Injection** system.

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

### Testing with `TestClient`

FastAPI provides `TestClient`, based on `httpx`, for easy and fast testing.

```python
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

## ✅ Best Practices

1. **Use Type Hints**: Standard Python type hints are the core of FastAPI. Use them everywhere for validation and editor support.
2. **Structure your App**: Use `APIRouter` to split your application into multiple files (e.g., `routers/items.py`, `routers/users.py`) as it grows.
3. **Pydantic Models**: Use Pydantic models for all your data schemas (request bodies, responses, etc.).
4. **Async/Await**: Use `async def` for your path operation functions appropriately, especially when doing I/O operations.

## 📚 Resources

- [Official FastAPI Documentation](https://fastapi.tiangolo.com/) - One of the best documentations out there.
- [FastAPI on GitHub](https://github.com/fastapi/fastapi)

---

**Next Steps**: comprehensive tutorial [official tutorial](https://fastapi.tiangolo.com/tutorial/).
