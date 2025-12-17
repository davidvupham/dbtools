# Litestar Tutorial

High-performance async web framework for Python.

## Overview

**Litestar** is a modern, fast ASGI web framework built for building APIs. It offers type safety, dependency injection, automatic OpenAPI documentation, and excellent performance through its use of msgspec for validation and serialization.

| | |
|---|---|
| **Package** | `litestar` |
| **Install** | `pip install litestar[standard]` |
| **Documentation** | [docs.litestar.dev](https://docs.litestar.dev/) |
| **GitHub** | [litestar-org/litestar](https://github.com/litestar-org/litestar) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Route Handlers](#route-handlers)
4. [Controllers](#controllers)
5. [Request and Response](#request-and-response)
6. [Dependency Injection](#dependency-injection)
7. [DTOs and Validation](#dtos-and-validation)
8. [Database Integration](#database-integration)
9. [OpenAPI Documentation](#openapi-documentation)
10. [Middleware and Guards](#middleware-and-guards)
11. [Comparison with FastAPI](#comparison-with-fastapi)

---

## Installation

```bash
# Standard installation (includes uvicorn)
pip install litestar[standard]

# Minimal installation
pip install litestar

# With specific extras
pip install litestar[sqlalchemy]  # SQLAlchemy integration
pip install litestar[jinja]       # Jinja2 templates
```

---

## Quick Start

```python
from litestar import Litestar, get

@get("/")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello, World!"}

@get("/users/{user_id:int}")
async def get_user(user_id: int) -> dict[str, int]:
    return {"user_id": user_id}

app = Litestar(route_handlers=[hello_world, get_user])
```

Run with:

```bash
litestar run
# or
uvicorn main:app --reload
```

---

## Route Handlers

### HTTP Methods

```python
from litestar import Litestar, get, post, put, patch, delete

@get("/items")
async def list_items() -> list[dict]:
    return [{"id": 1, "name": "Item 1"}]

@get("/items/{item_id:int}")
async def get_item(item_id: int) -> dict:
    return {"id": item_id, "name": f"Item {item_id}"}

@post("/items")
async def create_item(data: dict) -> dict:
    return {"id": 1, **data}

@put("/items/{item_id:int}")
async def replace_item(item_id: int, data: dict) -> dict:
    return {"id": item_id, **data}

@patch("/items/{item_id:int}")
async def update_item(item_id: int, data: dict) -> dict:
    return {"id": item_id, **data}

@delete("/items/{item_id:int}")
async def delete_item(item_id: int) -> None:
    return None
```

### Path Parameters

```python
from litestar import get

# Integer parameter
@get("/users/{user_id:int}")
async def get_user(user_id: int) -> dict:
    return {"user_id": user_id}

# String parameter
@get("/users/{username:str}")
async def get_user_by_name(username: str) -> dict:
    return {"username": username}

# UUID parameter
from uuid import UUID

@get("/orders/{order_id:uuid}")
async def get_order(order_id: UUID) -> dict:
    return {"order_id": str(order_id)}

# Path (captures everything including slashes)
@get("/files/{file_path:path}")
async def get_file(file_path: str) -> dict:
    return {"path": file_path}
```

### Query Parameters

```python
from litestar import get

@get("/search")
async def search(
    q: str,                          # Required
    page: int = 1,                   # Optional with default
    limit: int = 10,
    sort: str | None = None,         # Optional
) -> dict:
    return {
        "query": q,
        "page": page,
        "limit": limit,
        "sort": sort,
    }
```

---

## Controllers

Group related routes using controllers:

```python
from litestar import Controller, Litestar, get, post, delete
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

class UserController(Controller):
    path = "/users"
    tags = ["users"]

    @get("/")
    async def list_users(self) -> list[User]:
        return [User(id=1, name="John", email="john@example.com")]

    @get("/{user_id:int}")
    async def get_user(self, user_id: int) -> User:
        return User(id=user_id, name="John", email="john@example.com")

    @post("/")
    async def create_user(self, data: User) -> User:
        return data

    @delete("/{user_id:int}")
    async def delete_user(self, user_id: int) -> None:
        return None

app = Litestar(route_handlers=[UserController])
```

### Nested Controllers

```python
class TeamController(Controller):
    path = "/teams"

    @get("/")
    async def list_teams(self) -> list[dict]:
        return []

class MemberController(Controller):
    path = "/teams/{team_id:int}/members"

    @get("/")
    async def list_members(self, team_id: int) -> list[dict]:
        return []

    @post("/")
    async def add_member(self, team_id: int, data: dict) -> dict:
        return {"team_id": team_id, **data}

app = Litestar(route_handlers=[TeamController, MemberController])
```

---

## Request and Response

### Request Data

```python
from litestar import post, Request
from dataclasses import dataclass

@dataclass
class CreateUser:
    name: str
    email: str

# Body data (automatically parsed)
@post("/users")
async def create_user(data: CreateUser) -> CreateUser:
    return data

# Access raw request
@post("/raw")
async def handle_raw(request: Request) -> dict:
    body = await request.body()
    headers = dict(request.headers)
    return {"received": len(body)}
```

### Response Customization

```python
from litestar import get, Response
from litestar.status_codes import HTTP_201_CREATED

# Custom status code
@get("/created", status_code=HTTP_201_CREATED)
async def created_response() -> dict:
    return {"status": "created"}

# Custom response
@get("/custom")
async def custom_response() -> Response:
    return Response(
        content={"message": "custom"},
        status_code=200,
        headers={"X-Custom-Header": "value"},
    )
```

### Response Models

```python
from litestar import get
from dataclasses import dataclass

@dataclass
class UserResponse:
    id: int
    name: str
    # Note: password is not included

@get("/users/{user_id:int}")
async def get_user(user_id: int) -> UserResponse:
    # Only fields in UserResponse are returned
    return UserResponse(id=user_id, name="John")
```

---

## Dependency Injection

### Basic Dependencies

```python
from litestar import Litestar, get, Provide

async def get_db_connection() -> str:
    return "database_connection"

@get("/data", dependencies={"db": Provide(get_db_connection)})
async def get_data(db: str) -> dict:
    return {"connection": db}
```

### Application-Level Dependencies

```python
from litestar import Litestar, get, Provide
from dataclasses import dataclass

@dataclass
class Settings:
    app_name: str = "MyApp"
    debug: bool = False

def get_settings() -> Settings:
    return Settings()

@get("/info")
async def get_info(settings: Settings) -> dict:
    return {"app": settings.app_name}

app = Litestar(
    route_handlers=[get_info],
    dependencies={"settings": Provide(get_settings)},
)
```

### Dependency Scopes

```python
from litestar import Litestar, Provide

# Singleton (once per app)
app = Litestar(
    dependencies={
        "config": Provide(get_config, sync_to_thread=False),
    }
)

# Per-request (default)
@get("/", dependencies={"user": Provide(get_current_user)})
async def handler(user: User) -> dict:
    pass
```

---

## DTOs and Validation

### Data Transfer Objects

```python
from litestar import Litestar, get, post
from litestar.dto import DTOConfig, DataclassDTO
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str  # Sensitive!

# DTO that excludes password
class UserReadDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"password"})

class UserCreateDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"id"})

@get("/users/{user_id:int}", return_dto=UserReadDTO)
async def get_user(user_id: int) -> User:
    return User(id=user_id, name="John", email="john@example.com", password="secret")

@post("/users", dto=UserCreateDTO, return_dto=UserReadDTO)
async def create_user(data: User) -> User:
    data.id = 1
    return data
```

### Msgspec Models

Litestar uses msgspec for ultra-fast validation:

```python
import msgspec
from litestar import post

class CreateOrder(msgspec.Struct):
    product_id: int
    quantity: int
    notes: str | None = None

@post("/orders")
async def create_order(data: CreateOrder) -> dict:
    return {"product_id": data.product_id, "quantity": data.quantity}
```

### Pydantic Models

```python
from litestar import post
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

@post("/users")
async def create_user(data: UserCreate) -> dict:
    return data.model_dump()
```

---

## Database Integration

### SQLAlchemy Async

```python
from litestar import Litestar, get, post
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///./db.sqlite"
)

plugin = SQLAlchemyPlugin(config=sqlalchemy_config)

@get("/users")
async def list_users(db_session) -> list[User]:
    result = await db_session.execute(select(User))
    return result.scalars().all()

app = Litestar(
    route_handlers=[list_users],
    plugins=[plugin],
)
```

---

## OpenAPI Documentation

Litestar automatically generates OpenAPI 3.1 documentation:

```python
from litestar import Litestar
from litestar.openapi import OpenAPIConfig

app = Litestar(
    route_handlers=[...],
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="API documentation",
    ),
)
```

Access docs at:

- `/schema` - OpenAPI JSON
- `/schema/swagger` - Swagger UI
- `/schema/redoc` - ReDoc
- `/schema/elements` - Stoplight Elements

### Document Endpoints

```python
from litestar import get

@get(
    "/users",
    summary="List Users",
    description="Retrieve a paginated list of users.",
    tags=["users"],
)
async def list_users() -> list[dict]:
    """
    List all users in the system.

    Returns:
        A list of user objects.
    """
    return []
```

---

## Middleware and Guards

### Middleware

```python
from litestar import Litestar, Request, Response
from litestar.middleware import AbstractMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

class LoggingMiddleware(AbstractMiddleware):
    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] == "http":
            print(f"Request: {scope['method']} {scope['path']}")
        await self.app(scope, receive, send)

app = Litestar(
    route_handlers=[...],
    middleware=[LoggingMiddleware],
)
```

### Guards (Authorization)

```python
from litestar import Litestar, get, Request
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler
from litestar.exceptions import NotAuthorizedException

async def auth_guard(
    connection: ASGIConnection,
    handler: BaseRouteHandler,
) -> None:
    if "Authorization" not in connection.headers:
        raise NotAuthorizedException("Missing auth header")

@get("/protected", guards=[auth_guard])
async def protected_route() -> dict:
    return {"message": "You are authenticated!"}
```

### CORS

```python
from litestar import Litestar
from litestar.config.cors import CORSConfig

cors_config = CORSConfig(
    allow_origins=["https://example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app = Litestar(
    route_handlers=[...],
    cors_config=cors_config,
)
```

---

## Comparison with FastAPI

| Feature | Litestar | FastAPI |
|---------|----------|---------|
| **Serialization** | msgspec (faster) | Pydantic |
| **Class-based views** | First-class support | Limited |
| **DTOs** | Built-in | Manual |
| **Dependency Injection** | More flexible | Simple |
| **OpenAPI** | 3.1 | 3.0 |
| **Performance** | Slightly faster | Fast |
| **Ecosystem** | Growing | Large |

### When to Choose Litestar

- Need class-based controllers
- Want built-in DTO support
- Need maximum performance
- Prefer msgspec over Pydantic

### When to Choose FastAPI

- Want larger ecosystem/community
- Need more tutorials/examples
- Team already knows Pydantic
- Need specific FastAPI extensions

---

## Quick Reference

### Decorators

```python
@get("/path")
@post("/path")
@put("/path")
@patch("/path")
@delete("/path")
```

### Common Parameters

```python
@get(
    "/path",
    status_code=200,
    summary="...",
    description="...",
    tags=["tag1"],
    guards=[guard_fn],
    dependencies={"key": Provide(fn)},
)
```

### CLI Commands

```bash
litestar run              # Run dev server
litestar run --reload     # With auto-reload
litestar routes           # List routes
litestar openapi          # Generate OpenAPI spec
```

---

## See Also

- [Litestar Documentation](https://docs.litestar.dev/)
- [SQLModel Tutorial](../sqlmodel/README.md) - Type-safe ORM
- [Prefect Tutorial](../prefect/README.md) - Workflow orchestration

---

[← Back to Modules Index](../README.md)
