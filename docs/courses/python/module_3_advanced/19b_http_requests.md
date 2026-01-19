# HTTP and Web Requests

Making HTTP requests is fundamental to modern Python development. Whether you're consuming APIs, scraping websites, or building integrations, you need to understand how to make reliable, efficient HTTP calls.

## The requests library

The `requests` library is the standard for HTTP in Python—simple, elegant, and powerful.

### Installation

```bash
uv add requests
```

### Basic requests

```python
import requests

# GET request
response = requests.get("https://api.github.com/users/python")
print(response.status_code)  # 200
print(response.json())       # Parse JSON response

# POST request with JSON body
response = requests.post(
    "https://httpbin.org/post",
    json={"name": "Alice", "email": "alice@example.com"}
)

# POST with form data
response = requests.post(
    "https://httpbin.org/post",
    data={"username": "alice", "password": "secret"}
)

# Other HTTP methods
requests.put(url, json=data)
requests.patch(url, json=data)
requests.delete(url)
requests.head(url)
requests.options(url)
```

### Response handling

```python
response = requests.get("https://api.github.com/users/python")

# Status code
response.status_code      # 200
response.ok               # True (status < 400)
response.raise_for_status()  # Raises HTTPError if status >= 400

# Response content
response.text             # Response body as string
response.content          # Response body as bytes
response.json()           # Parse JSON (raises if invalid)

# Headers
response.headers          # Response headers (case-insensitive dict)
response.headers['Content-Type']  # 'application/json; charset=utf-8'

# Metadata
response.url              # Final URL (after redirects)
response.elapsed          # Time taken for request
response.encoding         # Detected encoding
```

### Query parameters

```python
# URL parameters
response = requests.get(
    "https://api.github.com/search/repositories",
    params={
        "q": "python",
        "sort": "stars",
        "order": "desc",
        "per_page": 10
    }
)
# Sends: https://api.github.com/search/repositories?q=python&sort=stars&order=desc&per_page=10

# List parameters
response = requests.get(
    "https://example.com/api",
    params={"tags": ["python", "web", "api"]}
)
# Sends: ?tags=python&tags=web&tags=api
```

### Headers

```python
# Custom headers
response = requests.get(
    "https://api.github.com/user",
    headers={
        "Authorization": "Bearer ghp_xxx",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MyApp/1.0"
    }
)

# Common headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {token}",
    "X-API-Key": api_key,
}
```

## Error handling

Always handle errors gracefully when making HTTP requests.

### HTTP errors

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def fetch_user(user_id: int) -> dict:
    """Fetch user data with comprehensive error handling."""
    try:
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
            timeout=10
        )
        response.raise_for_status()  # Raise for 4xx/5xx status
        return response.json()

    except HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"User {user_id} not found")
        elif e.response.status_code == 401:
            raise PermissionError("Authentication required")
        elif e.response.status_code == 429:
            raise RuntimeError("Rate limit exceeded")
        else:
            raise RuntimeError(f"HTTP error: {e.response.status_code}")

    except ConnectionError:
        raise RuntimeError("Could not connect to API")

    except Timeout:
        raise RuntimeError("Request timed out")

    except RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
```

### Status code patterns

```python
response = requests.get(url)

# Check specific status codes
if response.status_code == 200:
    return response.json()
elif response.status_code == 201:
    print("Resource created")
    return response.json()
elif response.status_code == 204:
    print("Success, no content")
    return None
elif response.status_code == 400:
    error = response.json()
    raise ValueError(f"Bad request: {error.get('message')}")
elif response.status_code == 401:
    raise PermissionError("Not authenticated")
elif response.status_code == 403:
    raise PermissionError("Not authorized")
elif response.status_code == 404:
    raise FileNotFoundError("Resource not found")
elif response.status_code == 429:
    retry_after = response.headers.get("Retry-After", 60)
    raise RuntimeError(f"Rate limited. Retry after {retry_after}s")
elif response.status_code >= 500:
    raise RuntimeError(f"Server error: {response.status_code}")
```

## Timeouts

Always set timeouts to prevent hanging requests.

```python
# Connection timeout: 5s, Read timeout: 30s
response = requests.get(url, timeout=(5, 30))

# Single timeout for both
response = requests.get(url, timeout=10)

# Never do this in production
response = requests.get(url)  # No timeout = can hang forever!
```

## Sessions

Use sessions for connection pooling and persistent settings.

```python
import requests

# Without session - new connection each request
for user_id in range(100):
    response = requests.get(f"https://api.example.com/users/{user_id}")

# With session - reuses connections (faster)
with requests.Session() as session:
    # Set default headers for all requests
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "User-Agent": "MyApp/1.0"
    })

    for user_id in range(100):
        response = session.get(f"https://api.example.com/users/{user_id}")
```

### Session with retry logic

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """Create a session with automatic retry logic."""
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# Usage
session = create_session_with_retries()
response = session.get("https://api.example.com/data")
```

## Authentication

### Basic authentication

```python
from requests.auth import HTTPBasicAuth

response = requests.get(
    "https://api.example.com/resource",
    auth=HTTPBasicAuth("username", "password")
)

# Shorthand
response = requests.get(url, auth=("username", "password"))
```

### Bearer token

```python
token = "your_access_token"
response = requests.get(
    "https://api.example.com/resource",
    headers={"Authorization": f"Bearer {token}"}
)
```

### API key

```python
# In header
response = requests.get(
    "https://api.example.com/resource",
    headers={"X-API-Key": "your_api_key"}
)

# In query parameter
response = requests.get(
    "https://api.example.com/resource",
    params={"api_key": "your_api_key"}
)
```

### OAuth 2.0

```python
from requests_oauthlib import OAuth2Session

client_id = "your_client_id"
client_secret = "your_client_secret"
token_url = "https://provider.com/oauth/token"

# Client credentials flow
from oauthlib.oauth2 import BackendApplicationClient

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=client_id,
    client_secret=client_secret
)

# Use the session for authenticated requests
response = oauth.get("https://api.example.com/resource")
```

## File uploads and downloads

### Uploading files

```python
# Single file
with open("document.pdf", "rb") as f:
    response = requests.post(
        "https://api.example.com/upload",
        files={"file": f}
    )

# With filename and content type
with open("image.png", "rb") as f:
    response = requests.post(
        "https://api.example.com/upload",
        files={"file": ("custom_name.png", f, "image/png")}
    )

# Multiple files
response = requests.post(
    "https://api.example.com/upload",
    files=[
        ("files", ("file1.txt", open("file1.txt", "rb"))),
        ("files", ("file2.txt", open("file2.txt", "rb"))),
    ]
)

# File with additional form data
response = requests.post(
    "https://api.example.com/upload",
    files={"file": open("doc.pdf", "rb")},
    data={"description": "My document", "public": "true"}
)
```

### Downloading files

```python
# Small files
response = requests.get("https://example.com/file.pdf")
with open("downloaded.pdf", "wb") as f:
    f.write(response.content)

# Large files - stream to avoid memory issues
response = requests.get("https://example.com/large_file.zip", stream=True)
with open("large_file.zip", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# With progress indicator
from tqdm import tqdm

response = requests.get(url, stream=True)
total_size = int(response.headers.get('content-length', 0))

with open("file.zip", "wb") as f:
    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
```

## Async HTTP with httpx

For async applications or high concurrency, use `httpx`.

### Installation

```bash
uv add httpx
```

### Basic async usage

```python
import httpx
import asyncio

async def fetch_user(client: httpx.AsyncClient, user_id: int) -> dict:
    response = await client.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

async def main():
    async with httpx.AsyncClient() as client:
        # Sequential
        user1 = await fetch_user(client, 1)
        user2 = await fetch_user(client, 2)

        # Concurrent (much faster)
        users = await asyncio.gather(
            fetch_user(client, 1),
            fetch_user(client, 2),
            fetch_user(client, 3),
        )

asyncio.run(main())
```

### Async with rate limiting

```python
import httpx
import asyncio
from asyncio import Semaphore

async def fetch_with_rate_limit(
    client: httpx.AsyncClient,
    semaphore: Semaphore,
    url: str
) -> dict:
    async with semaphore:  # Limits concurrent requests
        response = await client.get(url)
        return response.json()

async def main():
    urls = [f"https://api.example.com/items/{i}" for i in range(100)]

    # Limit to 10 concurrent requests
    semaphore = Semaphore(10)

    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_rate_limit(client, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

## API client pattern

Create reusable API clients for cleaner code.

```python
import requests
from typing import Any
from dataclasses import dataclass

@dataclass
class APIError(Exception):
    status_code: int
    message: str
    details: dict | None = None

class GitHubClient:
    """GitHub API client with proper error handling."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MyApp/1.0",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make a request with error handling."""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()

            if response.status_code == 204:
                return None
            return response.json()

        except requests.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except ValueError:
                pass

            raise APIError(
                status_code=e.response.status_code,
                message=error_data.get("message", str(e)),
                details=error_data
            )

    def get_user(self, username: str) -> dict:
        """Get a GitHub user by username."""
        return self._request("GET", f"/users/{username}")

    def get_repos(self, username: str, page: int = 1) -> list[dict]:
        """Get repositories for a user."""
        return self._request(
            "GET",
            f"/users/{username}/repos",
            params={"page": page, "per_page": 30}
        )

    def create_issue(self, owner: str, repo: str, title: str, body: str) -> dict:
        """Create an issue in a repository."""
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues",
            json={"title": title, "body": body}
        )

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

# Usage
with GitHubClient(token="ghp_xxx") as client:
    user = client.get_user("python")
    repos = client.get_repos("python")
```

## Best practices

### Request configuration

```python
import requests

# Good defaults for production
DEFAULT_TIMEOUT = (5, 30)  # (connect, read)
DEFAULT_HEADERS = {
    "User-Agent": "MyApp/1.0 (contact@example.com)",
    "Accept": "application/json",
}

def make_request(url: str, **kwargs) -> requests.Response:
    """Make a request with sensible defaults."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    kwargs.setdefault("headers", {}).update(DEFAULT_HEADERS)

    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response
```

### Logging requests

```python
import logging
import requests

logging.basicConfig(level=logging.DEBUG)

# Enable HTTP request logging
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# Or use hooks for custom logging
def log_request(response, *args, **kwargs):
    logging.info(
        f"{response.request.method} {response.url} "
        f"-> {response.status_code} ({response.elapsed.total_seconds():.2f}s)"
    )

session = requests.Session()
session.hooks["response"].append(log_request)
```

### Testing with responses

```python
import responses
import requests

@responses.activate
def test_get_user():
    # Mock the API response
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status=200
    )

    # Make the request (goes to mock)
    response = requests.get("https://api.example.com/users/1")

    assert response.json()["name"] == "Alice"
    assert len(responses.calls) == 1
```

## Common patterns

### Pagination

```python
def fetch_all_pages(base_url: str, params: dict = None) -> list:
    """Fetch all pages of a paginated API."""
    params = params or {}
    all_results = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        if not data:  # Empty page = done
            break

        all_results.extend(data)
        page += 1

        # Or check for next link in headers
        if "next" not in response.links:
            break

    return all_results
```

### Retry with exponential backoff

```python
import time
import requests
from functools import wraps

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for retrying with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

## Best practices summary

1. **Always set timeouts**: Prevent hanging requests with `timeout=(connect, read)`
2. **Use sessions**: For multiple requests to the same host (connection pooling)
3. **Handle errors**: Check status codes, catch exceptions, provide meaningful errors
4. **Retry transient failures**: Use exponential backoff for 5xx errors and timeouts
5. **Stream large files**: Use `stream=True` and `iter_content()` for large downloads
6. **Set User-Agent**: Identify your application in requests
7. **Use async for concurrency**: httpx for many concurrent requests
8. **Create API clients**: Encapsulate API logic in reusable classes
9. **Log requests**: For debugging and monitoring
10. **Test with mocks**: Use `responses` or `httpx.MockTransport` for testing

---

[← Back to Module 3](./README.md) | [← Security](./19a_security.md)
