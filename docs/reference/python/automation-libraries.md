# Python Automation Libraries Reference

**[← Back to Python Reference](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Reference-purple)

> [!IMPORTANT]
> **Related Docs:** [Python Coding Standards](../../development/coding-standards/python-coding-standards.md) | [Dependency Management](../../best-practices/python/dependency-management.md)

## Overview

This reference documents Python libraries essential for building reliable automation, workflows, and infrastructure tooling. Each library is vetted for production use with accurate installation instructions, practical examples, and guidance on when to use alternatives.

## Table of Contents

- [Retry and resilience](#retry-and-resilience)
- [Workflow orchestration](#workflow-orchestration)
- [Task runners](#task-runners)
- [Scheduling](#scheduling)
- [File system](#file-system)
- [Caching](#caching)
- [Database](#database)
- [HTTP and networking](#http-and-networking)
- [Terminal interfaces](#terminal-interfaces)
- [Configuration and settings](#configuration-and-settings)
- [Logging](#logging)
- [Decision guide](#decision-guide)

---

## Retry and resilience

### Tenacity

The most feature-complete retry library for Python. Use when you need fine-grained control over retry behavior.

| Attribute | Value |
|:----------|:------|
| **Package** | `tenacity` |
| **Version** | 9.1.2+ |
| **Python** | >=3.9 |
| **License** | Apache 2.0 |
| **Repository** | [jd/tenacity](https://github.com/jd/tenacity) |

```bash
uv add tenacity
```

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_data(url: str) -> dict:
    """Fetch data with exponential backoff on network errors."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

**Key features:**
- Decorator and context manager APIs
- Configurable stop conditions (attempts, time, custom)
- Wait strategies (fixed, random, exponential, fibonacci)
- Retry on exceptions or return values
- Async support (asyncio, Tornado)
- Callback hooks for logging

**When to use:** Complex retry requirements, multiple exception types, custom stop/wait logic.

### Backoff

Simpler alternative focused on exponential backoff. Use for straightforward retry needs.

| Attribute | Value |
|:----------|:------|
| **Package** | `backoff` |
| **Version** | 2.2.1+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [litl/backoff](https://github.com/litl/backoff) |

```bash
uv add backoff
```

```python
import backoff
import requests

@backoff.on_exception(
    backoff.expo,
    requests.RequestException,
    max_tries=5,
    max_time=300,
)
def get_data(url: str) -> dict:
    """Fetch data with exponential backoff."""
    return requests.get(url, timeout=30).json()
```

**Key features:**
- `@on_exception()` - retry on exceptions
- `@on_predicate()` - retry on return values
- Exponential, constant, fibonacci strategies
- Full jitter algorithm (AWS best practice)
- Async support

**When to use:** Simple exponential backoff, fewer configuration options needed.

### Stamina

Opinionated wrapper around Tenacity with better defaults. Use for production systems.

| Attribute | Value |
|:----------|:------|
| **Package** | `stamina` |
| **Version** | 24.3.0+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [hynek/stamina](https://github.com/hynek/stamina) |

```bash
uv add stamina
```

```python
import stamina
import httpx

@stamina.retry(on=httpx.HTTPError, attempts=3)
def fetch_user(user_id: int) -> dict:
    """Fetch user with sensible retry defaults."""
    response = httpx.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

**Key features:**
- Sensible defaults out of the box
- Preserves type hints (unlike raw Tenacity)
- Structured logging integration
- Async support
- `stamina.is_active()` for testing

**When to use:** Production systems where you want good defaults without configuration overhead.

[↑ Back to Table of Contents](#table-of-contents)

---

## Workflow orchestration

### Prefect

Modern workflow orchestration with Python-native syntax. Use for data pipelines and complex automation.

| Attribute | Value |
|:----------|:------|
| **Package** | `prefect` |
| **Version** | 3.6.12+ |
| **Python** | >=3.10, <3.15 |
| **License** | Apache 2.0 |
| **Repository** | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) |

```bash
uv add prefect
```

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def extract(source: str) -> list[dict]:
    """Extract data from source with caching."""
    ...

@task(retries=3, retry_delay_seconds=10)
def transform(data: list[dict]) -> list[dict]:
    """Transform data with automatic retries."""
    ...

@task
def load(data: list[dict], target: str) -> int:
    """Load data to target."""
    ...

@flow(name="etl-pipeline", log_prints=True)
def etl_pipeline(source: str, target: str) -> int:
    """ETL pipeline with observability."""
    raw = extract(source)
    clean = transform(raw)
    return load(clean, target)

if __name__ == "__main__":
    etl_pipeline("s3://bucket/input", "postgres://db/table")
```

**Key features:**
- Python decorators (`@flow`, `@task`)
- Automatic retries and caching
- Real-time monitoring UI
- Scheduling and triggers
- Hybrid execution (local, Docker, Kubernetes)
- Over 200 integrations

**Alternatives:**
- **Apache Airflow** - More mature, better for complex static DAGs
- **Dagster** - Asset-centric, better for data lineage

**When to use:** Dynamic workflows, Python-native syntax, modern observability needs.

[↑ Back to Table of Contents](#table-of-contents)

---

## Task runners

### Invoke

Python-native task runner for shell commands. Use to replace complex Makefiles or bash scripts.

| Attribute | Value |
|:----------|:------|
| **Package** | `invoke` |
| **Version** | 2.2.1+ |
| **Python** | >=3.6 |
| **License** | BSD |
| **Repository** | [pyinvoke/invoke](https://github.com/pyinvoke/invoke) |

```bash
uv add invoke
```

```python
# tasks.py
from invoke import task, Context

@task
def clean(c: Context) -> None:
    """Remove build artifacts."""
    c.run("rm -rf build/ dist/ *.egg-info")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +")

@task
def lint(c: Context) -> None:
    """Run linter."""
    c.run("ruff check .")

@task
def test(c: Context, coverage: bool = False) -> None:
    """Run tests with optional coverage."""
    cmd = "pytest"
    if coverage:
        cmd += " --cov=src --cov-report=html"
    c.run(cmd)

@task(pre=[lint, test])
def ci(c: Context) -> None:
    """Run CI checks (lint + test)."""
    print("CI checks passed!")
```

```bash
# Usage
inv clean
inv test --coverage
inv ci
```

**Key features:**
- `@task` decorator for defining tasks
- Task dependencies (`pre=`, `post=`)
- Argument/flag handling
- Namespaces for organization
- `tasks.py` convention

**Alternatives:**
- **Just** - Rust-powered, simpler Make-like syntax
- **Nox** - Better for testing matrices
- **Makefile** - Universal but less Pythonic

**When to use:** Complex build tasks, Python-native tooling, task dependencies.

[↑ Back to Table of Contents](#table-of-contents)

---

## Scheduling

### Schedule

Simple human-readable job scheduling. Use for lightweight, in-process scheduling.

| Attribute | Value |
|:----------|:------|
| **Package** | `schedule` |
| **Version** | 1.2.2+ |
| **Python** | >=3.7 |
| **License** | MIT |
| **Repository** | [dbader/schedule](https://github.com/dbader/schedule) |

```bash
uv add schedule
```

```python
import schedule
import time

def backup_database() -> None:
    """Perform database backup."""
    print("Running backup...")

def health_check() -> None:
    """Check service health."""
    print("Health check OK")

# Human-readable scheduling
schedule.every(10).minutes.do(health_check)
schedule.every().hour.do(backup_database)
schedule.every().day.at("02:00").do(backup_database)
schedule.every().monday.at("09:00").do(backup_database)

while True:
    schedule.run_pending()
    time.sleep(1)
```

**Key features:**
- Human-readable syntax
- In-process (no external dependencies)
- Lightweight, zero dependencies

**Limitations:**
- No async support
- Single-threaded
- No persistence (jobs lost on restart)
- In-process only

**When to use:** Simple scripts, development, lightweight automation.

### APScheduler

Advanced scheduling with persistence and async support. Use for production scheduling needs.

| Attribute | Value |
|:----------|:------|
| **Package** | `APScheduler` |
| **Version** | 3.10.4+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [agronholm/apscheduler](https://github.com/agronholm/apscheduler) |

```bash
uv add APScheduler
```

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

def send_report() -> None:
    """Send daily report."""
    print("Sending report...")

# Configure with persistence
jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")
}

scheduler = BackgroundScheduler(jobstores=jobstores)

# Cron-style scheduling
scheduler.add_job(
    send_report,
    CronTrigger(hour=9, minute=0),
    id="daily_report",
    replace_existing=True,
)

scheduler.start()
```

**Key features:**
- Multiple schedulers (background, blocking, async)
- Job persistence (SQLite, PostgreSQL, MongoDB, Redis)
- Cron, interval, and date triggers
- Timezone support
- Async support

**When to use:** Production systems, persistent jobs, complex scheduling requirements.

[↑ Back to Table of Contents](#table-of-contents)

---

## File system

### Watchfiles

High-performance file watching written in Rust. Use for file-triggered automation.

| Attribute | Value |
|:----------|:------|
| **Package** | `watchfiles` |
| **Version** | 1.1.1+ |
| **Python** | 3.9 - 3.14 |
| **License** | MIT |
| **Repository** | [samuelcolvin/watchfiles](https://github.com/samuelcolvin/watchfiles) |

```bash
uv add watchfiles
```

```python
from watchfiles import watch, Change
from pathlib import Path

def process_file(path: Path) -> None:
    """Process a changed file."""
    print(f"Processing: {path}")

# Synchronous watching
for changes in watch("./input"):
    for change_type, path in changes:
        if change_type == Change.added:
            process_file(Path(path))
```

```python
# Async watching
from watchfiles import awatch

async def watch_directory() -> None:
    async for changes in awatch("./input"):
        for change_type, path in changes:
            print(f"{change_type}: {path}")
```

**Key features:**
- Rust core (uses Notify library)
- Sync and async APIs
- `run_process()` for auto-reloading
- Built-in CLI
- Cross-platform

**When to use:** File-triggered automation, development hot-reload, event-driven processing.

### Fsspec

Unified filesystem interface for local and remote storage. Use when working with multiple storage backends.

| Attribute | Value |
|:----------|:------|
| **Package** | `fsspec` |
| **Version** | 2025.12.0+ |
| **Python** | >=3.8 |
| **License** | BSD |
| **Repository** | [fsspec/filesystem_spec](https://github.com/fsspec/filesystem_spec) |

```bash
uv add "fsspec[s3,gcs]"  # Include needed backends
```

```python
import fsspec

# Local file
with fsspec.open("./data.txt") as f:
    content = f.read()

# S3 (requires s3fs)
with fsspec.open("s3://bucket/data.txt") as f:
    content = f.read()

# GCS (requires gcsfs)
with fsspec.open("gs://bucket/data.txt") as f:
    content = f.read()

# Generic filesystem operations
fs = fsspec.filesystem("s3")
files = fs.ls("bucket/path/")
fs.copy("bucket/src.txt", "bucket/dst.txt")
```

**Supported backends:**
- Local, memory, zip, tar
- S3, GCS, Azure Blob, HDFS
- SFTP, SSH, FTP, HTTP
- GitHub, GitLab, Dropbox

**When to use:** Multi-cloud storage, portable data pipelines, filesystem abstraction.

[↑ Back to Table of Contents](#table-of-contents)

---

## Caching

### DiskCache

SQLite-backed disk cache. Use for persistent caching without external services.

| Attribute | Value |
|:----------|:------|
| **Package** | `diskcache` |
| **Version** | 5.6.3+ |
| **Python** | >=3.6 |
| **License** | Apache 2.0 |
| **Repository** | [grantjenks/python-diskcache](https://github.com/grantjenks/python-diskcache) |

```bash
uv add diskcache
```

```python
from diskcache import Cache, memoize_stampede

cache = Cache("./cache")

# Simple key-value storage
cache.set("key", {"data": "value"}, expire=3600)
data = cache.get("key")

# Function memoization with stampede protection
@memoize_stampede(cache, expire=300)
def expensive_query(user_id: int) -> dict:
    """Query with cache stampede protection."""
    # Expensive database query
    ...
```

**Key features:**
- SQLite-based (thread/process safe)
- Django cache backend compatible
- `@memoize_stampede` for cache stampede protection
- `@throttle` and `@barrier` decorators
- Eviction policies (LRU, LFU)

**Limitations:**
- Single-node only (not distributed)
- Not recommended for NFS mounts

**When to use:** Local caching, development, single-node applications.

[↑ Back to Table of Contents](#table-of-contents)

---

## Database

### SQLModel

Combines SQLAlchemy and Pydantic. Use with FastAPI for type-safe database models.

| Attribute | Value |
|:----------|:------|
| **Package** | `sqlmodel` |
| **Version** | 0.0.31+ |
| **Python** | >=3.7 |
| **License** | MIT |
| **Repository** | [fastapi/sqlmodel](https://github.com/fastapi/sqlmodel) |
| **Author** | tiangolo (Sebastian Ramirez) |

```bash
uv add sqlmodel
```

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    """User model - works as both ORM and Pydantic model."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    is_active: bool = Field(default=True)

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

# Create
with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)

# Query
with Session(engine) as session:
    statement = select(User).where(User.is_active == True)
    users = session.exec(statement).all()
```

**Key features:**
- Single model for ORM and validation
- Type hints throughout
- Full SQLAlchemy compatibility
- Full Pydantic compatibility
- FastAPI optimized

**When to use:** FastAPI applications, type-safe database access, reducing model duplication.

### APSW

Complete SQLite wrapper exposing full C API. Use for advanced SQLite features.

| Attribute | Value |
|:----------|:------|
| **Package** | `apsw` |
| **Version** | 3.51.2.0+ |
| **Python** | >=3.10 |
| **License** | OSI Approved |
| **Repository** | [rogerbinns/apsw](https://github.com/rogerbinns/apsw) |

```bash
uv add apsw
```

```python
import apsw
import apsw.bestpractice

# Apply recommended settings
apsw.bestpractice.apply(apsw.bestpractice.recommended)

conn = apsw.Connection("data.db")

# Full SQLite feature access
with conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            data JSON,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Use JSON functions
    conn.execute(
        "INSERT INTO events (data) VALUES (?)",
        ('{"type": "click", "target": "button"}',)
    )
```

**Key features:**
- Complete SQLite API access
- FTS5, JSON, Virtual Tables
- VFS (Virtual File System) support
- `apsw.bestpractice` module
- Free-threaded Python support

**When to use:** Advanced SQLite features, VFS, extensions, performance tuning.

[↑ Back to Table of Contents](#table-of-contents)

---

## HTTP and networking

### HTTPX

Modern HTTP client with async support. Use as the default HTTP client for new projects.

| Attribute | Value |
|:----------|:------|
| **Package** | `httpx` |
| **Version** | 0.28.0+ |
| **Python** | >=3.8 |
| **License** | BSD |
| **Repository** | [encode/httpx](https://github.com/encode/httpx) |

```bash
uv add httpx
```

```python
import httpx

# Sync client
response = httpx.get("https://api.example.com/users")
data = response.json()

# Async client
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
    data = response.json()

# With connection pooling and timeouts
client = httpx.Client(
    base_url="https://api.example.com",
    timeout=30.0,
    headers={"Authorization": "Bearer token"},
)
```

**Key features:**
- Sync and async APIs
- HTTP/1.1 and HTTP/2 support
- Connection pooling
- Requests-compatible API
- Streaming responses

**When to use:** All HTTP client needs, especially async applications.

### Respx

Mock HTTPX requests in tests. Use for testing HTTP client code.

| Attribute | Value |
|:----------|:------|
| **Package** | `respx` |
| **Version** | 0.22.0+ |
| **Python** | >=3.8 |
| **License** | BSD-3-Clause |
| **Repository** | [lundberg/respx](https://github.com/lundberg/respx) |

```bash
uv add --group dev respx
```

```python
import httpx
import respx
from httpx import Response

@respx.mock
def test_fetch_user():
    """Test user fetching with mocked HTTP."""
    respx.get("https://api.example.com/users/1").mock(
        return_value=Response(200, json={"id": 1, "name": "Alice"})
    )

    response = httpx.get("https://api.example.com/users/1")
    assert response.json()["name"] == "Alice"

# Pytest fixture
def test_with_fixture(respx_mock):
    """Test using pytest fixture."""
    respx_mock.get("https://api.example.com/health").mock(
        return_value=Response(200, json={"status": "ok"})
    )

    response = httpx.get("https://api.example.com/health")
    assert response.status_code == 200
```

**Key features:**
- Context manager and decorator APIs
- Pytest fixture (`respx_mock`)
- Pattern matching for routes
- Side effects support
- Async support

**When to use:** Testing code that uses HTTPX.

[↑ Back to Table of Contents](#table-of-contents)

---

## Terminal interfaces

### Rich

Beautiful terminal output. Use for progress bars, tables, and formatted output.

| Attribute | Value |
|:----------|:------|
| **Package** | `rich` |
| **Version** | 13.9.4+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [Textualize/rich](https://github.com/Textualize/rich) |
| **Author** | Will McGugan |

```bash
uv add rich
```

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print

console = Console()

# Rich print
print("[bold green]Success![/bold green] Operation completed.")

# Tables
table = Table(title="Users")
table.add_column("ID", style="cyan")
table.add_column("Name", style="magenta")
table.add_row("1", "Alice")
table.add_row("2", "Bob")
console.print(table)

# Progress bar
for item in track(range(100), description="Processing..."):
    process(item)
```

**Key features:**
- Syntax highlighting
- Tables, trees, panels
- Progress bars
- Markdown rendering
- Tracebacks with locals

**When to use:** CLI tools, scripts with user-facing output.

### Textual

Terminal user interfaces (TUI). Use for interactive terminal applications.

| Attribute | Value |
|:----------|:------|
| **Package** | `textual` |
| **Version** | 7.4.0+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [Textualize/textual](https://github.com/Textualize/textual) |
| **Author** | Will McGugan |

```bash
uv add textual
```

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static

class StatusApp(App):
    """A simple status dashboard."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #status {
        text-align: center;
        padding: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("System Status: OK", id="status")
        yield Button("Refresh", id="refresh")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh":
            self.query_one("#status", Static).update("Refreshing...")

if __name__ == "__main__":
    StatusApp().run()
```

**Key features:**
- CSS-based styling
- 24+ built-in widgets
- Event-driven architecture
- Web deployment (`textual serve`)
- Async support

**When to use:** Interactive terminal dashboards, admin tools, TUI applications.

### Typer

CLI framework with type hints. Use for building command-line applications.

| Attribute | Value |
|:----------|:------|
| **Package** | `typer` |
| **Version** | 0.15.1+ |
| **Python** | >=3.7 |
| **License** | MIT |
| **Repository** | [fastapi/typer](https://github.com/fastapi/typer) |
| **Author** | tiangolo (Sebastian Ramirez) |

```bash
uv add typer
```

```python
import typer
from typing import Annotated

app = typer.Typer(help="Database management CLI")

@app.command()
def migrate(
    target: Annotated[str, typer.Argument(help="Target version")],
    dry_run: Annotated[bool, typer.Option(help="Show changes without applying")] = False,
) -> None:
    """Run database migrations."""
    if dry_run:
        typer.echo(f"Would migrate to: {target}")
    else:
        typer.echo(f"Migrating to: {target}")

@app.command()
def backup(
    output: Annotated[str, typer.Option("-o", "--output", help="Output path")],
) -> None:
    """Create database backup."""
    typer.echo(f"Backing up to: {output}")

if __name__ == "__main__":
    app()
```

**Key features:**
- Type hint based arguments
- Auto-completion generation
- Rich output integration
- Subcommands and groups
- Testing utilities

**When to use:** All CLI applications, especially FastAPI projects.

[↑ Back to Table of Contents](#table-of-contents)

---

## Configuration and settings

### Pydantic Settings

Type-safe configuration from environment variables. Use for application settings.

| Attribute | Value |
|:----------|:------|
| **Package** | `pydantic-settings` |
| **Version** | 2.7.1+ |
| **Python** | >=3.8 |
| **License** | MIT |
| **Repository** | [pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) |

```bash
uv add pydantic-settings
```

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = Field(alias="DATABASE_URL")
    api_key: SecretStr = Field(alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")
    max_connections: int = Field(default=10, ge=1, le=100)

# Usage
settings = Settings()
print(settings.database_url)
print(settings.api_key.get_secret_value())  # Explicit reveal
```

**Key features:**
- Environment variable parsing
- `.env` file support
- Type validation
- Secret handling
- Nested settings

**When to use:** All application configuration, twelve-factor apps.

[↑ Back to Table of Contents](#table-of-contents)

---

## Logging

### Structlog

Structured logging for Python. Use for production logging with JSON output.

| Attribute | Value |
|:----------|:------|
| **Package** | `structlog` |
| **Version** | 24.4.0+ |
| **Python** | >=3.8 |
| **License** | Apache 2.0 |
| **Repository** | [hynek/structlog](https://github.com/hynek/structlog) |

```bash
uv add structlog
```

```python
import structlog

# Configure for production (JSON output)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# Structured logging with context
log.info("user_login", user_id=123, ip_address="192.168.1.1")
# Output: {"event": "user_login", "user_id": 123, "ip_address": "192.168.1.1", "timestamp": "2026-01-26T10:30:00Z", "level": "info"}

# Bind context for request lifecycle
request_log = log.bind(request_id="abc-123")
request_log.info("processing_started")
request_log.info("processing_completed", duration_ms=45)
```

**Key features:**
- JSON and logfmt output
- Context binding
- Processor pipeline
- stdlib logging integration
- Async support

**When to use:** Production systems, log aggregation, observability.

[↑ Back to Table of Contents](#table-of-contents)

---

## Decision guide

### Retry libraries

| Need | Recommendation |
|:-----|:---------------|
| Simple exponential backoff | `backoff` |
| Complex retry logic | `tenacity` |
| Production with good defaults | `stamina` |

### Scheduling

| Need | Recommendation |
|:-----|:---------------|
| Simple in-process jobs | `schedule` |
| Persistent jobs | `APScheduler` |
| Distributed workflows | `prefect` or `celery` |

### HTTP clients

| Need | Recommendation |
|:-----|:---------------|
| New projects | `httpx` |
| Legacy compatibility | `requests` |
| Testing HTTPX | `respx` |
| Testing requests | `responses` |

### Terminal output

| Need | Recommendation |
|:-----|:---------------|
| Formatted output | `rich` |
| Interactive TUI | `textual` |
| CLI framework | `typer` |

### Database

| Need | Recommendation |
|:-----|:---------------|
| FastAPI + Pydantic | `sqlmodel` |
| Advanced SQLite | `apsw` |
| Full ORM | `sqlalchemy` |

### Configuration

| Need | Recommendation |
|:-----|:---------------|
| Environment variables | `pydantic-settings` |
| Complex configs | `pydantic-settings` + YAML |
| Simple scripts | `python-dotenv` |

[↑ Back to Table of Contents](#table-of-contents)

---

## Changelog

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | January 26, 2026 | Initial release with 18 libraries |

[↑ Back to Table of Contents](#table-of-contents)
