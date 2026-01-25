# Chapter 15: MCP patterns

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-3_MCP-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Implement security best practices for MCP servers
2. Handle errors gracefully across the MCP pipeline
3. Optimize performance for production workloads
4. Apply common design patterns for robust integrations

## Table of contents

- [Introduction](#introduction)
- [Security patterns](#security-patterns)
- [Error handling patterns](#error-handling-patterns)
- [Performance patterns](#performance-patterns)
- [Design patterns](#design-patterns)
- [Production checklist](#production-checklist)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Building a working MCP server is one thing; building a production-ready one requires attention to security, error handling, and performance. This chapter covers essential patterns for robust MCP integrations.

[↑ Back to Table of Contents](#table-of-contents)

## Security patterns

### Input sanitization

Never trust input from the AI model—it could be influenced by prompt injection.

```python
import re
from typing import Any


class InputSanitizer:
    """Sanitize tool inputs before processing."""

    # Patterns that could indicate malicious input
    DANGEROUS_PATTERNS = [
        r";\s*DROP\s+TABLE",
        r";\s*DELETE\s+FROM",
        r"--\s*$",
        r"/\*.*\*/",
        r"UNION\s+SELECT",
    ]

    @classmethod
    def sanitize_sql(cls, query: str) -> str:
        """Sanitize SQL input."""
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous SQL pattern detected")

        # Only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")

        return query

    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize file path input."""
        # Prevent path traversal
        if ".." in path:
            raise ValueError("Path traversal not allowed")

        # Only allow specific directories
        allowed_prefixes = ["/var/log/", "/tmp/", "/home/user/projects/"]
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(f"Path not in allowed directories")

        return path


# Usage in tool handler
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_database":
        query = InputSanitizer.sanitize_sql(arguments["query"])
        # ... execute safe query

    elif name == "read_log":
        path = InputSanitizer.sanitize_path(arguments["path"])
        # ... read from safe path
```

### Least privilege

Limit what each tool can do:

```python
from enum import Enum, auto


class Permission(Enum):
    READ_LOGS = auto()
    READ_METRICS = auto()
    EXECUTE_QUERY = auto()
    MODIFY_CONFIG = auto()  # High privilege


class ToolPermissions:
    """Define tool permissions."""

    TOOL_PERMISSIONS = {
        "analyze_log": [Permission.READ_LOGS],
        "get_metrics": [Permission.READ_METRICS],
        "query_database": [Permission.READ_LOGS, Permission.EXECUTE_QUERY],
        "update_config": [Permission.MODIFY_CONFIG],  # Requires approval
    }

    HIGH_PRIVILEGE = [Permission.MODIFY_CONFIG]

    @classmethod
    def requires_approval(cls, tool_name: str) -> bool:
        """Check if tool requires human approval."""
        permissions = cls.TOOL_PERMISSIONS.get(tool_name, [])
        return any(p in cls.HIGH_PRIVILEGE for p in permissions)
```

### Audit logging

Log all tool calls for security review:

```python
import logging
import json
from datetime import datetime


class AuditLogger:
    """Audit log for MCP tool calls."""

    def __init__(self, log_path: str = "/var/log/mcp-audit.log"):
        self.logger = logging.getLogger("mcp-audit")
        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_tool_call(
        self,
        tool_name: str,
        arguments: dict,
        result: str,
        success: bool,
        duration_ms: float
    ):
        """Log a tool call."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "arguments": self._redact_sensitive(arguments),
            "success": success,
            "duration_ms": duration_ms,
            "result_length": len(result)
        }
        self.logger.info(json.dumps(entry))

    def _redact_sensitive(self, args: dict) -> dict:
        """Redact sensitive values."""
        sensitive_keys = ["password", "token", "secret", "key"]
        return {
            k: "[REDACTED]" if any(s in k.lower() for s in sensitive_keys) else v
            for k, v in args.items()
        }


# Usage
audit = AuditLogger()

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    start = time.time()
    try:
        result = await execute_tool(name, arguments)
        audit.log_tool_call(name, arguments, result, True, (time.time() - start) * 1000)
        return result
    except Exception as e:
        audit.log_tool_call(name, arguments, str(e), False, (time.time() - start) * 1000)
        raise
```

[↑ Back to Table of Contents](#table-of-contents)

## Error handling patterns

### Structured error responses

```python
from dataclasses import dataclass
from enum import Enum


class ErrorCode(Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class ToolError:
    code: ErrorCode
    message: str
    details: dict | None = None

    def to_response(self) -> str:
        """Format error for MCP response."""
        return f"Error [{self.code.value}]: {self.message}"


def handle_tool_error(e: Exception) -> ToolError:
    """Convert exception to structured error."""
    if isinstance(e, ValueError):
        return ToolError(ErrorCode.VALIDATION_ERROR, str(e))
    elif isinstance(e, FileNotFoundError):
        return ToolError(ErrorCode.NOT_FOUND, str(e))
    elif isinstance(e, PermissionError):
        return ToolError(ErrorCode.PERMISSION_DENIED, str(e))
    elif isinstance(e, asyncio.TimeoutError):
        return ToolError(ErrorCode.TIMEOUT, "Operation timed out")
    else:
        return ToolError(ErrorCode.INTERNAL_ERROR, "An unexpected error occurred")
```

### Retry with backoff

```python
import asyncio
from functools import wraps


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


@retry_with_backoff(max_retries=3, base_delay=0.5)
async def query_database(query: str) -> str:
    """Query with automatic retry."""
    # ... implementation
```

### Timeout handling

```python
async def call_tool_with_timeout(
    name: str,
    arguments: dict,
    timeout_seconds: int = 30
) -> list[TextContent]:
    """Execute tool with timeout."""
    try:
        async with asyncio.timeout(timeout_seconds):
            return await execute_tool(name, arguments)
    except asyncio.TimeoutError:
        return [TextContent(
            type="text",
            text=f"Tool '{name}' timed out after {timeout_seconds} seconds"
        )]
```

[↑ Back to Table of Contents](#table-of-contents)

## Performance patterns

### Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta


class TTLCache:
    """Simple TTL cache for tool results."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> str | None:
        """Get cached value if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: str):
        """Cache a value."""
        self.cache[key] = (value, datetime.now())


# Usage
metrics_cache = TTLCache(ttl_seconds=60)


async def get_metrics(metric_name: str) -> str:
    """Get metrics with caching."""
    cache_key = f"metrics:{metric_name}"

    # Check cache
    cached = metrics_cache.get(cache_key)
    if cached:
        return cached

    # Fetch fresh data
    result = await fetch_metrics_from_db(metric_name)

    # Cache result
    metrics_cache.set(cache_key, result)

    return result
```

### Connection pooling

```python
import asyncpg
from contextlib import asynccontextmanager


class DatabasePool:
    """Manage database connection pool."""

    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool: asyncpg.Pool | None = None

    async def initialize(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size
        )

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool."""
        async with self.pool.acquire() as conn:
            yield conn


# Global pool instance
db_pool = DatabasePool("postgresql://user:pass@localhost/db")


async def query_database(query: str) -> str:
    """Execute query using pooled connection."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query)
        return format_results(rows)
```

### Async batch processing

```python
async def analyze_logs_batch(log_paths: list[str]) -> list[str]:
    """Analyze multiple logs concurrently."""
    tasks = [analyze_single_log(path) for path in log_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    formatted = []
    for path, result in zip(log_paths, results):
        if isinstance(result, Exception):
            formatted.append(f"{path}: Error - {result}")
        else:
            formatted.append(f"{path}: {result}")

    return formatted
```

[↑ Back to Table of Contents](#table-of-contents)

## Design patterns

### Tool composition

Build complex tools from simpler ones:

```python
class CompositeToolHandler:
    """Compose multiple tool operations."""

    def __init__(self):
        self.handlers = {
            "analyze_log": self.analyze_log,
            "get_metrics": self.get_metrics,
            "suggest_fix": self.suggest_fix,
        }

    async def health_check(self, database: str) -> str:
        """Composite tool: full health check."""
        results = []

        # Step 1: Check logs
        log_analysis = await self.analyze_log(
            f"/var/log/{database}/error.log"
        )
        results.append(f"## Log Analysis\n{log_analysis}")

        # Step 2: Get metrics
        metrics = await self.get_metrics(database)
        results.append(f"## Metrics\n{metrics}")

        # Step 3: Generate suggestions based on findings
        suggestions = await self.suggest_fix(
            f"Based on: {log_analysis}\n{metrics}"
        )
        results.append(f"## Recommendations\n{suggestions}")

        return "\n\n".join(results)
```

### Plugin architecture

```python
from abc import ABC, abstractmethod


class ToolPlugin(ABC):
    """Base class for tool plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def schema(self) -> dict:
        """Input schema."""
        pass

    @abstractmethod
    async def execute(self, arguments: dict) -> str:
        """Execute the tool."""
        pass


class PluginRegistry:
    """Registry for tool plugins."""

    def __init__(self):
        self.plugins: dict[str, ToolPlugin] = {}

    def register(self, plugin: ToolPlugin):
        """Register a plugin."""
        self.plugins[plugin.name] = plugin

    def get_tools(self) -> list[Tool]:
        """Get all registered tools."""
        return [
            Tool(
                name=p.name,
                description=p.description,
                inputSchema=p.schema
            )
            for p in self.plugins.values()
        ]

    async def execute(self, name: str, arguments: dict) -> str:
        """Execute a tool by name."""
        if name not in self.plugins:
            raise ValueError(f"Unknown tool: {name}")
        return await self.plugins[name].execute(arguments)


# Usage
registry = PluginRegistry()
registry.register(LogAnalyzerPlugin())
registry.register(QueryExplainerPlugin())
```

[↑ Back to Table of Contents](#table-of-contents)

## Production checklist

### Before deployment

```text
PRODUCTION READINESS CHECKLIST
══════════════════════════════

Security:
□ Input sanitization for all tool arguments
□ Least privilege permissions
□ Audit logging enabled
□ Sensitive data redaction
□ Rate limiting configured

Error Handling:
□ All exceptions caught and handled
□ Structured error responses
□ Timeout handling
□ Retry logic for transient failures
□ Graceful degradation

Performance:
□ Connection pooling configured
□ Caching for frequent operations
□ Async operations where possible
□ Resource limits set

Monitoring:
□ Health check endpoint
□ Metrics collection
□ Log aggregation
□ Alerting configured

Documentation:
□ All tools documented
□ Schema descriptions complete
□ Error codes documented
□ Deployment guide written
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Implement security with input sanitization, least privilege, and audit logging
- Handle errors gracefully with structured responses and retries
- Optimize performance with caching, connection pools, and async processing
- Apply design patterns like composition and plugins for maintainable code
- Use a production checklist to ensure deployment readiness

## Next steps

You have completed Module 3! Continue to **[Module 4: Agentic AI](../module_4_agentic_ai/16_agent_fundamentals.md)** to learn how to build autonomous AI agents.

Before continuing, complete:
- 📝 **[Module 3 Exercises](./exercises/)**
- 📋 **[Module 3 Quiz](./quiz_module_3.md)**
- 🛠️ **[Project 3: Database MCP Server](./project_3_mcp_server.md)**

[↑ Back to Table of Contents](#table-of-contents)
