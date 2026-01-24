# REST API Concepts: Interview essentials for backend developers

**[← Back to Backend Module](../project_4_api.md)**

> **Document Version:** 1.0
> **Last Updated:** January 23, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Tutorial-blue)

> [!NOTE]
> **Time to complete:** 45-60 minutes
> **Difficulty:** Intermediate

## Introduction

This tutorial covers essential REST API concepts that frequently appear in backend developer interviews. These aren't just theoretical knowledge—they're practical patterns that separate production-ready APIs from hobby projects. Understanding these concepts demonstrates architectural maturity and helps you build more resilient systems.

## Prerequisites

Before starting this tutorial, you should have:

- [ ] Basic understanding of HTTP methods (GET, POST, PUT, DELETE)
- [ ] Familiarity with JSON and REST principles
- [ ] Python experience (examples use FastAPI/Litestar syntax)

## What you will learn

By the end of this tutorial, you will be able to:

1. Explain idempotency and implement idempotent endpoints
2. Choose the right pagination strategy for your use case
3. Evaluate API versioning tradeoffs
4. Implement rate limiting with token bucket algorithm
5. Design proper error contracts with correct HTTP status codes
6. Configure HTTP caching with ETag and Cache-Control
7. Apply JWT security best practices
8. Identify and fix N+1 query problems
9. Explain why OpenAPI documentation is essential
10. Decide when eventual consistency is acceptable

## Table of Contents

- [1. Idempotency](#1-idempotency)
- [2. Pagination](#2-pagination)
- [3. API versioning](#3-api-versioning)
- [4. Rate limiting](#4-rate-limiting)
- [5. Error contracts](#5-error-contracts)
- [6. HTTP caching](#6-http-caching)
- [7. JWT security](#7-jwt-security)
- [8. N+1 queries](#8-n1-queries)
- [9. API documentation](#9-api-documentation)
- [10. Consistency models](#10-consistency-models)
- [Interview quick reference](#interview-quick-reference)

---

## 1. Idempotency

**Interview question:** *"Why are PUT and DELETE idempotent but POST isn't?"*

### What is idempotency?

An operation is **idempotent** if performing it multiple times produces the same result as performing it once. This is critical in distributed systems where network failures can cause request retries.

### HTTP method idempotency

| Method | Idempotent | Safe | Explanation |
|:-------|:-----------|:-----|:------------|
| GET | Yes | Yes | Reading data doesn't change state |
| HEAD | Yes | Yes | Same as GET without response body |
| PUT | Yes | No | Replaces entire resource; same payload = same result |
| DELETE | Yes | No | Deleting twice leaves resource deleted |
| POST | **No** | No | Creates new resource each time |
| PATCH | **No** | No | Depends on implementation |

### Why this matters

```python
# Scenario: Client sends order, network times out
# Client retries - what happens?

# POST /orders (NOT idempotent)
# First request: Creates order #123
# Retry: Creates order #124  <- DUPLICATE ORDER!

# PUT /orders/123 (Idempotent)
# First request: Creates/updates order #123
# Retry: Updates order #123 <- Same result
```

### Implementing idempotency for POST

Use **idempotency keys** to make non-idempotent operations safe:

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import hashlib

app = FastAPI()

# Simple in-memory store (use Redis in production)
processed_requests: dict[str, dict] = {}


class OrderCreate(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
async def create_order(
    order: OrderCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    # Check if we've seen this key before
    if idempotency_key in processed_requests:
        # Return cached response instead of creating duplicate
        return processed_requests[idempotency_key]

    # Process the order
    result = {"order_id": 123, "status": "created", **order.model_dump()}

    # Cache the result (set TTL in production)
    processed_requests[idempotency_key] = result

    return result
```

**Client usage:**

```bash
# Client generates unique key per logical operation
curl -X POST /orders \
  -H "Idempotency-Key: order-abc-123-attempt-1" \
  -d '{"product_id": 1, "quantity": 2}'
```

> [!TIP]
> Major payment APIs (Stripe, PayPal) require idempotency keys for all mutating operations. This pattern prevents double charges.

[↑ Back to Table of Contents](#table-of-contents)

---

## 2. Pagination

**Interview question:** *"When would you use cursor pagination instead of offset pagination?"*

### Offset pagination

The simplest approach—skip N records, return M records:

```python
@app.get("/items")
async def list_items(offset: int = 0, limit: int = 20):
    # SQL: SELECT * FROM items LIMIT 20 OFFSET 100
    items = await db.execute(
        select(Item).offset(offset).limit(limit)
    )
    return {
        "items": items,
        "offset": offset,
        "limit": limit,
        "total": await db.scalar(select(func.count(Item.id))),
    }
```

**Problems at scale:**

1. **Performance degrades**: `OFFSET 1000000` must scan 1M rows first
2. **Inconsistent results**: If items are inserted/deleted during pagination, you get duplicates or missed items
3. **COUNT is expensive**: Counting millions of rows on every request

### Cursor/keyset pagination

Use a pointer to the last seen item instead of counting rows:

```python
from base64 import b64encode, b64decode
import json


def encode_cursor(created_at: str, id: int) -> str:
    """Create opaque cursor from sort fields."""
    return b64encode(json.dumps({"c": created_at, "i": id}).encode()).decode()


def decode_cursor(cursor: str) -> tuple[str, int]:
    """Extract sort fields from cursor."""
    data = json.loads(b64decode(cursor))
    return data["c"], data["i"]


@app.get("/items")
async def list_items(cursor: str | None = None, limit: int = 20):
    query = select(Item).order_by(Item.created_at.desc(), Item.id.desc())

    if cursor:
        created_at, item_id = decode_cursor(cursor)
        # WHERE (created_at, id) < (cursor_created_at, cursor_id)
        query = query.where(
            tuple_(Item.created_at, Item.id) < (created_at, item_id)
        )

    items = await db.execute(query.limit(limit + 1))  # Fetch one extra
    items = list(items)

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(last.created_at.isoformat(), last.id)

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
```

### When to use each

| Factor | Offset | Cursor |
|:-------|:-------|:-------|
| **Dataset size** | < 10,000 records | Any size |
| **Data volatility** | Static data | Frequently changing |
| **Jump to page N** | Supported | Not possible |
| **Performance** | Degrades with offset | Consistent |
| **Use case** | Admin dashboards | Infinite scroll, feeds |

> [!IMPORTANT]
> Cursor pagination requires indexed, unique, immutable sort fields. A common pattern is `(created_at, id)` where `id` breaks ties.

[↑ Back to Table of Contents](#table-of-contents)

---

## 3. API versioning

**Interview question:** *"How would you version your API? What are the tradeoffs?"*

### Three main strategies

#### URI path versioning

```text
GET /v1/users/123
GET /v2/users/123
```

**Pros:**
- Most visible and explicit
- Easy to route at load balancer level
- Cacheable (different URIs = different cache entries)
- Used by Twitter, Facebook, Stripe

**Cons:**
- Violates REST principle (URI should identify resource, not representation)
- Forces clients to update URLs on version change

#### Header versioning

```text
GET /users/123
Accept: application/vnd.myapi.v2+json
```

Or custom header:

```text
GET /users/123
API-Version: 2
```

**Pros:**
- Clean URIs that identify resources
- More RESTful approach
- Fine-grained: version individual resources

**Cons:**
- Harder to test in browser
- Some proxies/caches ignore custom headers
- Less discoverable

#### Query parameter versioning

```text
GET /users/123?version=2
```

**Pros:**
- Easy to test and switch versions
- Visible in URL but doesn't change path
- Optional parameter can default to latest

**Cons:**
- Query params typically mean filtering, not resource identification
- Can complicate caching

### Recommendation

```python
# For most APIs: URI versioning is pragmatic and widely understood
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")


@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Alice"}  # v1 format


@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    return {
        "id": user_id,
        "name": {"first": "Alice", "last": "Smith"},  # v2 format
    }
```

> [!TIP]
> The "right" answer in interviews: acknowledge tradeoffs and explain that URI versioning is most common because it's explicit and works well with caching and routing infrastructure.

[↑ Back to Table of Contents](#table-of-contents)

---

## 4. Rate limiting

**Interview question:** *"How would you implement rate limiting? Why is token bucket better than fixed window?"*

### Fixed window problem

```text
Limit: 100 requests/minute

Timeline:
11:00:59 - User sends 100 requests (allowed)
11:01:00 - New window starts
11:01:01 - User sends 100 requests (allowed)

Result: 200 requests in 2 seconds!
```

The "burst at window boundary" problem allows double the rate.

### Token bucket algorithm

```python
import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: int  # Maximum tokens
    refill_rate: float  # Tokens added per second
    tokens: float = 0
    last_refill: float = 0

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        now = time.time()

        # Refill tokens based on elapsed time
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


# Usage: 10 requests/second with burst of 20
bucket = TokenBucket(capacity=20, refill_rate=10)

if bucket.consume():
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    pass
```

### Algorithm comparison

| Algorithm | Burst handling | Memory | Accuracy | Best for |
|:----------|:---------------|:-------|:---------|:---------|
| Fixed window | Allows 2x at boundary | Low | Low | Simple cases |
| Sliding window | Smooth | Medium | Medium | Most APIs |
| Token bucket | Controlled bursts | Low | High | Production APIs |
| Leaky bucket | No bursts | Low | High | Steady rate needed |

### Response headers

Always communicate limits to clients:

```python
from fastapi import Response


@app.get("/api/resource")
async def get_resource(response: Response):
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "95"
    response.headers["X-RateLimit-Reset"] = "1706054400"  # Unix timestamp
    return {"data": "..."}
```

When rate limited:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=429,
    detail="Rate limit exceeded",
    headers={"Retry-After": "60"},  # Seconds until retry
)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## 5. Error contracts

**Interview question:** *"What's the difference between 400, 422, and 409?"*

### Status code decision tree

```text
Is the request malformed (bad JSON, missing headers)?
  → 400 Bad Request

Is the request syntactically correct but semantically invalid?
  → 422 Unprocessable Entity

Does the request conflict with current server state?
  → 409 Conflict

Is it a server-side problem?
  → 500 Internal Server Error
```

### Detailed breakdown

| Code | Name | When to use | Example |
|:-----|:-----|:------------|:--------|
| 400 | Bad Request | Malformed syntax | Invalid JSON, missing required header |
| 401 | Unauthorized | No/invalid credentials | Missing or expired token |
| 403 | Forbidden | Valid credentials, no permission | User can't access admin resource |
| 404 | Not Found | Resource doesn't exist | GET /users/99999 |
| 409 | Conflict | State conflict | Creating duplicate email |
| 422 | Unprocessable Entity | Validation failed | Email format invalid |
| 429 | Too Many Requests | Rate limited | Exceeded API quota |
| 500 | Internal Server Error | Server bug | Unhandled exception |

### Implementation pattern

```python
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, ValidationError


class UserCreate(BaseModel):
    email: EmailStr
    username: str


@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Check for conflict (duplicate)
    existing = await db.get_user_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "conflict",
                "message": "A user with this email already exists",
                "field": "email",
            },
        )

    # Business logic validation (422)
    if not is_valid_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "validation_error",
                "message": "Username must be alphanumeric",
                "field": "username",
            },
        )

    return await db.create_user(user)
```

### Consistent error response format

```python
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str  # Machine-readable error code
    message: str  # Human-readable message
    field: str | None = None  # Which field caused the error
    details: dict | None = None  # Additional context


# All error responses use same structure
{
    "error": "validation_error",
    "message": "Email format is invalid",
    "field": "email",
    "details": {"pattern": "user@domain.com"}
}
```

> [!WARNING]
> Never return 500 for client errors. A 500 means your server has a bug—it triggers alerts and on-call pages. Use 4xx for client mistakes.

[↑ Back to Table of Contents](#table-of-contents)

---

## 6. HTTP caching

**Interview question:** *"How do ETag and Cache-Control work together?"*

### Cache-Control header

Controls how responses are cached:

```python
from fastapi import Response


@app.get("/products/{product_id}")
async def get_product(product_id: int, response: Response):
    product = await db.get_product(product_id)

    # Cache for 5 minutes in browser, 1 hour in CDN
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=3600"

    return product


@app.get("/me")
async def get_current_user(response: Response):
    # Private data - only browser can cache, must revalidate
    response.headers["Cache-Control"] = "private, no-cache"
    return {"user": "..."}
```

**Key directives:**

| Directive | Meaning |
|:----------|:--------|
| `public` | CDNs and browsers can cache |
| `private` | Only browser can cache |
| `max-age=N` | Fresh for N seconds |
| `s-maxage=N` | CDN freshness (overrides max-age for shared caches) |
| `no-cache` | Must revalidate before using |
| `no-store` | Never store (sensitive data) |

### ETag for validation

ETag is a fingerprint of the resource:

```python
import hashlib
from fastapi import Request, Response


@app.get("/products/{product_id}")
async def get_product(
    product_id: int,
    request: Request,
    response: Response,
):
    product = await db.get_product(product_id)

    # Generate ETag from content
    content = json.dumps(product, sort_keys=True)
    etag = hashlib.md5(content.encode()).hexdigest()

    # Check if client has current version
    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304)  # Not Modified

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"

    return product
```

**Flow:**

```text
1. Client: GET /products/123
2. Server: 200 OK, ETag: "abc123", Cache-Control: max-age=60

   [60 seconds pass, cache expires]

3. Client: GET /products/123, If-None-Match: "abc123"
4. Server: 304 Not Modified (no body, saves bandwidth)

   [Product updated on server]

5. Client: GET /products/123, If-None-Match: "abc123"
6. Server: 200 OK, ETag: "def456" (new content)
```

> [!TIP]
> Use `Cache-Control` to avoid requests entirely (within max-age). Use `ETag` to avoid transferring unchanged data after expiry.

[↑ Back to Table of Contents](#table-of-contents)

---

## 7. JWT security

**Interview question:** *"Why shouldn't you store PII in JWTs?"*

### JWT structure

```text
header.payload.signature

eyJhbGciOiJIUzI1NiJ9.  <- Header (base64)
eyJzdWIiOiIxMjM0NTY3ODkwIn0.  <- Payload (base64, NOT encrypted)
dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U  <- Signature
```

### Why no PII in JWTs

```python
# BAD: Anyone can decode this
token_payload = {
    "sub": "user-123",
    "email": "alice@company.com",  # PII!
    "ssn": "123-45-6789",  # Definitely not!
    "role": "admin",
}

# The payload is NOT encrypted, only signed
# Anyone with the token can read: base64.decode(payload)
```

**Problems with PII in tokens:**

1. **Tokens are stored everywhere**: Browser storage, logs, URLs
2. **No way to update**: If email changes, old tokens have wrong data
3. **Regulatory issues**: GDPR/CCPA require ability to delete PII
4. **Token size**: Large tokens increase every request size

### Correct approach

```python
import jwt
from datetime import datetime, timedelta

# GOOD: Minimal claims, reference user by ID
def create_access_token(user_id: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": user_id,  # Only identifier, no PII
        "iat": now,
        "exp": now + timedelta(minutes=15),  # Short expiry!
        "iss": "myapp.com",
        "aud": "myapp.com",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# Fetch user details from database when needed
@app.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user = await db.get_user(payload["sub"])  # Lookup by ID
    return user
```

### Expiration best practices

| Token type | Recommended expiry | Reason |
|:-----------|:-------------------|:-------|
| Access token | 15 minutes | Limits damage if leaked |
| Refresh token | 7 days | Balance security and UX |
| API key | 90 days | Rotate regularly |

### Token validation checklist

```python
def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],  # Explicit algorithm
            audience="myapp.com",  # Verify audience
            issuer="myapp.com",  # Verify issuer
            options={
                "require": ["exp", "iat", "sub"],  # Required claims
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

> [!CAUTION]
> Never disable signature verification. Never accept `alg: none`. Always validate `exp`, `iss`, and `aud` claims.

[↑ Back to Table of Contents](#table-of-contents)

---

## 8. N+1 queries

**Interview question:** *"What's the N+1 problem and how do you solve it?"*

### The problem

```python
# Fetching 100 orders with their customers

# N+1 approach (BAD)
orders = db.query("SELECT * FROM orders LIMIT 100")  # 1 query
for order in orders:
    # This runs 100 times!
    customer = db.query(
        f"SELECT * FROM customers WHERE id = {order.customer_id}"
    )  # N queries

# Total: 101 queries for 100 orders
```

### Solution 1: Eager loading with JOINs

```python
# SQLAlchemy eager loading
from sqlalchemy.orm import joinedload

# Single query with JOIN
orders = (
    session.query(Order)
    .options(joinedload(Order.customer))
    .limit(100)
    .all()
)

# SQL: SELECT orders.*, customers.*
#      FROM orders JOIN customers ON orders.customer_id = customers.id
#      LIMIT 100
```

### Solution 2: Batch loading

```python
# Fetch all orders first
orders = db.query("SELECT * FROM orders LIMIT 100")

# Collect all customer IDs
customer_ids = {order.customer_id for order in orders}

# Single query for all customers
customers = db.query(
    "SELECT * FROM customers WHERE id IN :ids",
    {"ids": tuple(customer_ids)},
)

# Build lookup map
customer_map = {c.id: c for c in customers}

# Attach customers to orders
for order in orders:
    order.customer = customer_map[order.customer_id]

# Total: 2 queries regardless of order count
```

### Solution 3: DataLoader pattern (GraphQL)

```python
from aiodataloader import DataLoader


async def batch_load_customers(customer_ids: list[int]):
    """Load multiple customers in one query."""
    customers = await db.execute(
        select(Customer).where(Customer.id.in_(customer_ids))
    )
    customer_map = {c.id: c for c in customers}
    # Must return in same order as input IDs
    return [customer_map.get(id) for id in customer_ids]


# Create loader (one per request)
customer_loader = DataLoader(batch_load_customers)


# In resolver/handler - these get batched automatically
async def resolve_order(order):
    return {
        "id": order.id,
        "customer": await customer_loader.load(order.customer_id),
    }
```

### Detection

```python
# SQLAlchemy query logging
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Look for patterns like:
# SELECT * FROM customers WHERE id = 1
# SELECT * FROM customers WHERE id = 2
# SELECT * FROM customers WHERE id = 3
# ... (repeated N times)
```

> [!TIP]
> In interviews, mention that N+1 is especially problematic in GraphQL because the client controls query depth. DataLoader is the standard solution.

[↑ Back to Table of Contents](#table-of-contents)

---

## 9. API documentation

**Interview question:** *"Why is OpenAPI documentation important?"*

### Why it's not optional

1. **Developer experience**: Developers can't use what they don't understand
2. **Reduced support burden**: Good docs prevent support tickets
3. **API-first design**: OpenAPI spec enables design-before-implementation
4. **Code generation**: Clients, SDKs, and mock servers from spec
5. **Testing**: Automated contract testing against spec

### FastAPI/Litestar auto-documentation

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Orders API",
    description="API for managing customer orders",
    version="1.0.0",
)


class OrderResponse(BaseModel):
    """A customer order."""

    id: int = Field(..., description="Unique order identifier")
    status: str = Field(..., description="Order status", examples=["pending"])
    total: float = Field(..., description="Order total in USD")


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    responses={
        404: {"description": "Order not found"},
    },
)
async def get_order(
    order_id: int,
    include_items: bool = Query(
        False, description="Include line items in response"
    ),
):
    """
    Retrieve a specific order by its ID.

    - **order_id**: The unique identifier of the order
    - **include_items**: Whether to include line item details
    """
    ...
```

This generates:
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- OpenAPI JSON at `/openapi.json`

### Documentation checklist

| Element | Required | Example |
|:--------|:---------|:--------|
| Endpoint description | Yes | "Creates a new order" |
| All parameters | Yes | Path, query, body with types |
| Request examples | Yes | Sample JSON request body |
| Response examples | Yes | Success and error responses |
| Error codes | Yes | 400, 404, 422 with meanings |
| Authentication | Yes | "Requires Bearer token" |

### Keeping docs in sync

```yaml
# Use design-first approach: Write OpenAPI spec first

openapi: 3.0.3
info:
  title: Orders API
  version: 1.0.0

paths:
  /orders/{order_id}:
    get:
      summary: Get order by ID
      parameters:
        - name: order_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Order found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
```

> [!IMPORTANT]
> Treat documentation as code: version it, review it in PRs, and validate it in CI. Use tools like Spectral to lint OpenAPI specs.

[↑ Back to Table of Contents](#table-of-contents)

---

## 10. Consistency models

**Interview question:** *"When is eventual consistency acceptable?"*

### Strong vs eventual consistency

| Aspect | Strong consistency | Eventual consistency |
|:-------|:-------------------|:---------------------|
| **Guarantee** | Read always returns latest write | Read eventually returns latest write |
| **Latency** | Higher (must sync) | Lower |
| **Availability** | Lower (CAP theorem) | Higher |
| **Use case** | Banking, inventory | Social feeds, analytics |

### Decision framework

Ask: **"Would it be catastrophic if users briefly saw stale data?"**

```python
# STRONG CONSISTENCY REQUIRED
# User just changed password - must take effect immediately
@app.post("/auth/password")
async def change_password(new_password: str):
    await db.update_password(user_id, new_password)  # Sync write
    await invalidate_all_sessions(user_id)  # Must happen NOW
    return {"status": "password changed"}


# EVENTUAL CONSISTENCY ACCEPTABLE
# Like count can be slightly stale
@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await cache.get(f"post:{post_id}")  # Might be 30s stale
    if not post:
        post = await db.get_post(post_id)
        await cache.set(f"post:{post_id}", post, ttl=30)
    return post
```

### Real-world examples

| Feature | Consistency | Why |
|:--------|:------------|:----|
| Account balance | Strong | Money must be accurate |
| Shopping cart | Strong | Items shouldn't disappear |
| Like count | Eventual | ±5 likes doesn't matter |
| Profile photo | Eventual | Old photo for a minute is fine |
| Inventory count | Strong | Prevent overselling |
| Product reviews | Eventual | New reviews can appear with delay |
| Session/auth | Strong | Security critical |
| Search results | Eventual | Slight delay in indexing is acceptable |

### Implementation patterns

```python
# Read-your-own-writes consistency
# User always sees their own changes immediately

@app.post("/posts")
async def create_post(post: PostCreate):
    new_post = await db.create_post(post)

    # Write to cache immediately for this user's session
    await cache.set(
        f"user:{user_id}:posts",
        await db.get_user_posts(user_id),
        ttl=60,
    )

    return new_post


@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, current_user: User):
    if current_user.id == user_id:
        # User viewing own posts - read from DB for freshness
        return await db.get_user_posts(user_id)
    else:
        # Others viewing - cache is fine
        return await cache.get_or_set(
            f"user:{user_id}:posts",
            lambda: db.get_user_posts(user_id),
            ttl=60,
        )
```

> [!TIP]
> In interviews, mention the CAP theorem: in a distributed system, you can only have two of Consistency, Availability, and Partition tolerance. Since network partitions are inevitable, the real choice is between consistency and availability.

[↑ Back to Table of Contents](#table-of-contents)

---

## Interview quick reference

### One-liner answers

| Topic | Key point |
|:------|:----------|
| **Idempotency** | PUT/DELETE are idempotent; use idempotency keys for POST |
| **Pagination** | Offset for small/static data; cursor for scale |
| **Versioning** | URI path is most common; header is more RESTful |
| **Rate limiting** | Token bucket handles bursts fairly; return 429 with Retry-After |
| **Error codes** | 400=malformed, 422=validation, 409=conflict, 500=server bug |
| **Caching** | Cache-Control sets freshness; ETag validates staleness |
| **JWT security** | No PII in claims; short expiry; always validate |
| **N+1 queries** | Use JOINs, batch loading, or DataLoader |
| **Documentation** | OpenAPI is mandatory; enables code gen and testing |
| **Consistency** | Strong for money/auth; eventual for social/analytics |

### Common follow-up questions

1. **"How would you handle partial failures in a distributed system?"**
   → Idempotency keys, saga pattern, compensating transactions

2. **"How do you test API rate limiting?"**
   → Load testing tools (k6, locust), check 429 responses and headers

3. **"What's the difference between authentication and authorization?"**
   → 401 (who are you?) vs 403 (you can't do that)

4. **"How do you handle API versioning for breaking changes?"**
   → Deprecation headers, sunset dates, migration guides

---

## Summary

These ten concepts separate junior API developers from senior ones:

1. **Idempotency** prevents duplicate operations
2. **Pagination** scales with your data
3. **Versioning** enables evolution without breaking clients
4. **Rate limiting** protects your infrastructure
5. **Error contracts** help developers debug quickly
6. **Caching** reduces load and latency
7. **JWT security** protects user data
8. **N+1 prevention** keeps your database healthy
9. **Documentation** makes your API usable
10. **Consistency models** balance correctness and performance

## Next steps

- **[Build a REST API with Litestar](../litestar/README.md)** - Apply these concepts in practice
- **[SQLModel Database Integration](../sqlmodel/README.md)** - Handle N+1 queries with SQLAlchemy
- **[Project 4: Todo API](../project_4_api.md)** - Hands-on project

## Additional resources

- [REST API Tutorial](https://restfulapi.net/) - Comprehensive REST reference
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) - MDN reference
- [JWT.io](https://jwt.io/) - JWT debugger and library list
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) - Official spec

[↑ Back to Table of Contents](#table-of-contents)
