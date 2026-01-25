# Project 3: Database MCP Server

**[← Back to Course Index](../README.md)**

> **Difficulty:** Intermediate
> **Estimated Time:** 4-6 hours
> **Prerequisites:** Module 3 chapters completed, PostgreSQL access

## Overview

Build a production-ready MCP server that provides database operations tools for AI assistants. The server will allow AI models to query databases, analyze performance, and retrieve metrics.

## Learning objectives

By completing this project, you will:

1. Implement a complete MCP server with multiple tools
2. Apply security best practices (input validation, least privilege)
3. Add observability (logging, metrics)
4. Test MCP tools thoroughly

## Requirements

### Tools to implement

| Tool | Description | Risk Level |
|:-----|:------------|:-----------|
| `query_database` | Execute read-only SQL queries | Medium |
| `get_table_schema` | Get table structure information | Low |
| `get_slow_queries` | List currently slow queries | Low |
| `get_metrics` | Get database performance metrics | Low |
| `explain_query` | Get query execution plan | Low |

### Resources to implement

| Resource | Description |
|:---------|:------------|
| `database://config` | Current database configuration |
| `database://stats` | Database statistics summary |

### Security requirements

- Read-only operations only (no INSERT, UPDATE, DELETE)
- Query timeout limits
- Input sanitization for all parameters
- Audit logging for all operations
- Connection pooling

## Getting started

### Step 1: Project setup

```bash
mkdir db-mcp-server && cd db-mcp-server
python -m venv .venv
source .venv/bin/activate
pip install mcp asyncpg python-dotenv
```

### Step 2: Server structure

```python
# src/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncpg

server = Server("db-mcp-server")

# Connection pool (initialize in main)
pool: asyncpg.Pool = None


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return available database tools."""
    return [
        Tool(
            name="query_database",
            description="Execute a read-only SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum rows to return",
                        "default": 100
                    }
                },
                "required": ["query"]
            }
        ),
        # Add more tools...
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool call."""
    if name == "query_database":
        return await handle_query(arguments)
    elif name == "get_table_schema":
        return await handle_schema(arguments)
    # Add more handlers...
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
```

### Step 3: Implement tools

```python
# src/tools/query.py
import re
from typing import Tuple


class QueryValidator:
    """Validate SQL queries for safety."""

    BLOCKED_PATTERNS = [
        r";\s*DROP",
        r";\s*DELETE",
        r";\s*INSERT",
        r";\s*UPDATE",
        r";\s*TRUNCATE",
        r"--",
        r"/\*",
    ]

    @classmethod
    def validate(cls, query: str) -> Tuple[bool, str]:
        """Validate query is safe to execute."""
        query_upper = query.upper().strip()

        # Must start with SELECT
        if not query_upper.startswith("SELECT"):
            return False, "Only SELECT queries are allowed"

        # Check for dangerous patterns
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Query contains blocked pattern"

        return True, "Valid"


async def handle_query(arguments: dict) -> list[TextContent]:
    """Handle query_database tool call."""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 100)

    # Validate
    valid, message = QueryValidator.validate(query)
    if not valid:
        return [TextContent(type="text", text=f"Error: {message}")]

    # Add limit if not present
    if "LIMIT" not in query.upper():
        query = f"{query} LIMIT {limit}"

    try:
        async with pool.acquire() as conn:
            # Set statement timeout
            await conn.execute("SET statement_timeout = '30s'")
            rows = await conn.fetch(query)

            # Format results
            if not rows:
                return [TextContent(type="text", text="No results found")]

            result = format_results(rows)
            return [TextContent(type="text", text=result)]

    except asyncpg.PostgresError as e:
        return [TextContent(type="text", text=f"Database error: {e}")]
```

## Implementation tasks

### Part 1: Core tools (40%)

- [ ] Implement `query_database` with validation
- [ ] Implement `get_table_schema`
- [ ] Implement `get_slow_queries`
- [ ] Implement `get_metrics`
- [ ] Implement `explain_query`

### Part 2: Resources (20%)

- [ ] Implement `database://config` resource
- [ ] Implement `database://stats` resource
- [ ] Handle resource subscriptions

### Part 3: Security (25%)

- [ ] Input sanitization for all tools
- [ ] Query timeout handling
- [ ] Connection pool limits
- [ ] Audit logging implementation
- [ ] Error message sanitization (no internal details)

### Part 4: Testing (15%)

- [ ] Unit tests for validators
- [ ] Integration tests for tools
- [ ] Mock database for testing
- [ ] Error case coverage

## Configuration

```python
# src/config.py
from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    max_connections: int = 10
    query_timeout_seconds: int = 30
    max_rows: int = 1000
    log_path: str = "/var/log/db-mcp.log"

    class Config:
        env_file = ".env"
```

## Expected usage with Claude Desktop

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["-m", "db_mcp_server"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/db"
      }
    }
  }
}
```

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| All tools implemented and working | 30 |
| Security measures in place | 25 |
| Resources implemented | 15 |
| Audit logging | 10 |
| Test coverage | 10 |
| Code quality and documentation | 10 |
| **Total** | **100** |

---

**[Next Module →](../module_4_agentic_ai/16_agent_fundamentals.md)**
