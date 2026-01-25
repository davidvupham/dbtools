# Chapter 13: Building MCP servers

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-3_MCP-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Set up an MCP server project with the Python SDK
2. Implement tools, resources, and prompts
3. Handle tool execution and error cases
4. Test your MCP server locally

## Table of contents

- [Introduction](#introduction)
- [Project setup](#project-setup)
- [Basic server structure](#basic-server-structure)
- [Implementing tools](#implementing-tools)
- [Implementing resources](#implementing-resources)
- [Implementing prompts](#implementing-prompts)
- [Error handling](#error-handling)
- [Testing your server](#testing-your-server)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

This chapter walks through building an MCP server from scratch using the Python SDK. You'll create a server that provides database-related tools for log analysis and query optimization.

[↑ Back to Table of Contents](#table-of-contents)

## Project setup

### Prerequisites

- Python 3.10+
- UV package manager (recommended)

### Create the project

```bash
# Create project directory
mkdir dbtool-mcp-server
cd dbtool-mcp-server

# Initialize with UV
uv init

# Add MCP SDK
uv add mcp

# Optional: Add other dependencies
uv add httpx  # For API calls if needed
```

### Project structure

```text
dbtool-mcp-server/
├── pyproject.toml
├── src/
│   └── dbtool_mcp/
│       ├── __init__.py
│       ├── server.py      # Main server
│       ├── tools.py       # Tool implementations
│       ├── resources.py   # Resource implementations
│       └── prompts.py     # Prompt templates
└── tests/
    └── test_server.py
```

### pyproject.toml

```toml
[project]
name = "dbtool-mcp-server"
version = "0.1.0"
description = "MCP server for database operations"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
]

[project.scripts]
dbtool-mcp = "dbtool_mcp.server:main"
```

[↑ Back to Table of Contents](#table-of-contents)

## Basic server structure

### Minimal server

```python
# src/dbtool_mcp/server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Create server instance
server = Server("dbtool-mcp")


@server.list_tools()
async def list_tools():
    """Return list of available tools."""
    return []


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool execution."""
    return []


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### Running the server

```bash
# Run directly
python -m dbtool_mcp.server

# Or via entry point (after installing)
uv pip install -e .
dbtool-mcp
```

[↑ Back to Table of Contents](#table-of-contents)

## Implementing tools

### Tool definitions

```python
# src/dbtool_mcp/tools.py
from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Return all tool definitions."""
    return [
        Tool(
            name="analyze_log",
            description="Analyze database log entries and identify issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_content": {
                        "type": "string",
                        "description": "The log content to analyze"
                    },
                    "database_type": {
                        "type": "string",
                        "enum": ["postgresql", "mysql", "mongodb"],
                        "default": "postgresql",
                        "description": "Type of database"
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["all", "error", "warning"],
                        "default": "all",
                        "description": "Minimum severity to include"
                    }
                },
                "required": ["log_content"]
            }
        ),
        Tool(
            name="explain_query",
            description="Explain a SQL query and suggest optimizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to explain"
                    },
                    "include_optimization": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include optimization suggestions"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="suggest_index",
            description="Suggest indexes based on query patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Target table name"
                    },
                    "query_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Common query patterns for this table"
                    }
                },
                "required": ["table_name", "query_patterns"]
            }
        )
    ]
```

### Tool execution

```python
# src/dbtool_mcp/server.py (updated)
import asyncio
import re
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .tools import get_tool_definitions

server = Server("dbtool-mcp")


@server.list_tools()
async def list_tools():
    """Return list of available tools."""
    return get_tool_definitions()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution."""
    if name == "analyze_log":
        result = await analyze_log(
            arguments["log_content"],
            arguments.get("database_type", "postgresql"),
            arguments.get("severity_filter", "all")
        )
        return [TextContent(type="text", text=result)]

    elif name == "explain_query":
        result = await explain_query(
            arguments["query"],
            arguments.get("include_optimization", True)
        )
        return [TextContent(type="text", text=result)]

    elif name == "suggest_index":
        result = await suggest_index(
            arguments["table_name"],
            arguments["query_patterns"]
        )
        return [TextContent(type="text", text=result)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def analyze_log(log_content: str, db_type: str, severity: str) -> str:
    """Analyze database logs."""
    # Parse log entries
    lines = log_content.strip().split('\n')
    errors = []
    warnings = []

    for line in lines:
        if 'ERROR' in line or 'FATAL' in line:
            errors.append(line)
        elif 'WARNING' in line:
            warnings.append(line)

    # Build response
    result = f"## Log Analysis ({db_type})\n\n"
    result += f"Total lines: {len(lines)}\n"
    result += f"Errors found: {len(errors)}\n"
    result += f"Warnings found: {len(warnings)}\n\n"

    if errors:
        result += "### Errors\n"
        for err in errors[:5]:  # Limit to first 5
            result += f"- {err}\n"

    if warnings and severity in ["all", "warning"]:
        result += "\n### Warnings\n"
        for warn in warnings[:5]:
            result += f"- {warn}\n"

    return result


async def explain_query(query: str, include_optimization: bool) -> str:
    """Explain a SQL query."""
    result = "## Query Analysis\n\n"
    result += f"```sql\n{query}\n```\n\n"

    # Simple pattern analysis
    issues = []

    if 'SELECT *' in query.upper():
        issues.append("Using SELECT * - consider specifying columns")

    if 'WHERE' not in query.upper() and ('UPDATE' in query.upper() or 'DELETE' in query.upper()):
        issues.append("UPDATE/DELETE without WHERE clause - dangerous!")

    if re.search(r'LIKE\s+[\'"]%', query, re.IGNORECASE):
        issues.append("Leading wildcard in LIKE - cannot use index")

    result += "### Issues Found\n"
    if issues:
        for issue in issues:
            result += f"- {issue}\n"
    else:
        result += "- No obvious issues detected\n"

    if include_optimization:
        result += "\n### Optimization Suggestions\n"
        result += "- Consider adding appropriate indexes\n"
        result += "- Review execution plan with EXPLAIN ANALYZE\n"

    return result


async def suggest_index(table_name: str, query_patterns: list[str]) -> str:
    """Suggest indexes based on query patterns."""
    result = f"## Index Suggestions for `{table_name}`\n\n"

    for i, pattern in enumerate(query_patterns, 1):
        result += f"### Pattern {i}\n"
        result += f"```sql\n{pattern}\n```\n"

        # Extract columns from WHERE clause (simplified)
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', pattern, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            # Extract column names (simplified)
            columns = re.findall(r'(\w+)\s*[=<>]', where_clause)
            if columns:
                result += f"Suggested index: `CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name} ({', '.join(columns)});`\n"

        result += "\n"

    return result


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

[↑ Back to Table of Contents](#table-of-contents)

## Implementing resources

```python
# src/dbtool_mcp/resources.py
from mcp.types import Resource, ResourceTemplate


def get_resource_definitions() -> list[Resource]:
    """Return static resource definitions."""
    return [
        Resource(
            uri="docs://runbooks/connection-issues",
            name="Connection Troubleshooting",
            description="Runbook for diagnosing database connection issues",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://best-practices/indexing",
            name="Indexing Best Practices",
            description="Guide to database indexing strategies",
            mimeType="text/markdown"
        )
    ]


def get_resource_templates() -> list[ResourceTemplate]:
    """Return resource templates for dynamic resources."""
    return [
        ResourceTemplate(
            uriTemplate="config://{database_type}/default",
            name="Default Configuration",
            description="Default configuration for a database type"
        )
    ]


RUNBOOK_CONNECTION = """
# Connection Troubleshooting Runbook

## Symptoms
- Connection refused errors
- Connection timeout
- Too many connections

## Diagnostic Steps

1. **Check if database is running**
   ```bash
   systemctl status postgresql
   ```

2. **Check connection limits**
   ```sql
   SHOW max_connections;
   SELECT count(*) FROM pg_stat_activity;
   ```

3. **Check for blocked connections**
   ```sql
   SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';
   ```

## Common Solutions

- Increase max_connections if consistently near limit
- Configure connection pooling (PgBouncer)
- Kill idle transactions over threshold
"""

BEST_PRACTICES_INDEXING = """
# Indexing Best Practices

## When to Create Indexes

- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY (if returning many rows)

## When NOT to Create Indexes

- Tables with very few rows
- Columns with low cardinality
- Frequently updated columns (high write cost)

## Index Types

| Type | Use Case |
|------|----------|
| B-tree | Default, most queries |
| Hash | Equality comparisons only |
| GiST | Geometric, full-text |
| GIN | Arrays, JSONB, full-text |
"""


def get_resource_content(uri: str) -> str:
    """Get content for a resource URI."""
    if uri == "docs://runbooks/connection-issues":
        return RUNBOOK_CONNECTION
    elif uri == "docs://best-practices/indexing":
        return BEST_PRACTICES_INDEXING
    elif uri.startswith("config://"):
        # Parse config://postgresql/default
        parts = uri.replace("config://", "").split("/")
        if len(parts) >= 2:
            db_type = parts[0]
            return get_default_config(db_type)
    return f"Resource not found: {uri}"


def get_default_config(db_type: str) -> str:
    """Get default configuration for a database type."""
    configs = {
        "postgresql": """
# PostgreSQL Recommended Configuration

# Memory
shared_buffers = '256MB'           # 25% of RAM
effective_cache_size = '768MB'      # 75% of RAM
work_mem = '4MB'
maintenance_work_mem = '64MB'

# Connections
max_connections = 100

# Write-Ahead Log
wal_level = 'replica'
max_wal_size = '1GB'
""",
        "mysql": """
# MySQL Recommended Configuration

[mysqld]
innodb_buffer_pool_size = 256M
max_connections = 100
query_cache_size = 64M
"""
    }
    return configs.get(db_type, f"No default config for {db_type}")
```

### Adding resources to server

```python
# Update server.py to include resources

from .resources import get_resource_definitions, get_resource_templates, get_resource_content
from mcp.types import TextContent, BlobContent

@server.list_resources()
async def list_resources():
    """Return list of available resources."""
    return get_resource_definitions()


@server.list_resource_templates()
async def list_resource_templates():
    """Return resource templates."""
    return get_resource_templates()


@server.read_resource()
async def read_resource(uri: str):
    """Read a resource by URI."""
    content = get_resource_content(uri)
    return [TextContent(type="text", text=content)]
```

[↑ Back to Table of Contents](#table-of-contents)

## Implementing prompts

```python
# src/dbtool_mcp/prompts.py
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent


def get_prompt_definitions() -> list[Prompt]:
    """Return available prompts."""
    return [
        Prompt(
            name="analyze-slow-query",
            description="Analyze a SQL query for performance issues",
            arguments=[
                PromptArgument(
                    name="query",
                    description="The SQL query to analyze",
                    required=True
                ),
                PromptArgument(
                    name="context",
                    description="Additional context (table sizes, indexes)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="diagnose-issue",
            description="Diagnose a database issue step by step",
            arguments=[
                PromptArgument(
                    name="symptoms",
                    description="What symptoms are you observing?",
                    required=True
                ),
                PromptArgument(
                    name="database",
                    description="Database type (postgresql, mysql)",
                    required=True
                )
            ]
        )
    ]


def get_prompt_messages(name: str, arguments: dict) -> list[PromptMessage]:
    """Generate prompt messages for a given prompt."""
    if name == "analyze-slow-query":
        query = arguments.get("query", "")
        context = arguments.get("context", "No additional context provided")

        return [
            PromptMessage(
                role="system",
                content=TextContent(
                    type="text",
                    text="""You are a database performance analyst.
Analyze SQL queries for performance issues and suggest optimizations.
Be specific about:
1. What makes the query slow
2. Index recommendations
3. Query rewrites if applicable
4. Estimated impact of changes"""
                )
            ),
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Analyze this SQL query for performance issues:

```sql
{query}
```

Additional context:
{context}

Provide a detailed analysis with specific recommendations."""
                )
            )
        ]

    elif name == "diagnose-issue":
        symptoms = arguments.get("symptoms", "")
        database = arguments.get("database", "postgresql")

        return [
            PromptMessage(
                role="system",
                content=TextContent(
                    type="text",
                    text=f"""You are a {database} database reliability engineer.
Diagnose issues systematically:
1. Clarify the symptoms
2. List possible causes
3. Provide diagnostic queries/commands
4. Suggest solutions in order of likelihood"""
                )
            ),
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""I'm experiencing the following issue with our {database} database:

{symptoms}

Please help me diagnose this issue step by step."""
                )
            )
        ]

    return []
```

### Adding prompts to server

```python
# Update server.py

from .prompts import get_prompt_definitions, get_prompt_messages

@server.list_prompts()
async def list_prompts():
    """Return available prompts."""
    return get_prompt_definitions()


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None):
    """Get a prompt by name with arguments."""
    messages = get_prompt_messages(name, arguments or {})
    return {"messages": messages}
```

[↑ Back to Table of Contents](#table-of-contents)

## Error handling

```python
# Robust error handling in server.py

from mcp.types import TextContent, ErrorData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution with error handling."""
    try:
        if name == "analyze_log":
            # Validate required arguments
            if "log_content" not in arguments:
                raise ValueError("Missing required argument: log_content")

            result = await analyze_log(
                arguments["log_content"],
                arguments.get("database_type", "postgresql"),
                arguments.get("severity_filter", "all")
            )
            return [TextContent(type="text", text=result)]

        elif name == "explain_query":
            if "query" not in arguments:
                raise ValueError("Missing required argument: query")

            result = await explain_query(
                arguments["query"],
                arguments.get("include_optimization", True)
            )
            return [TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except ValueError as e:
        logger.warning(f"Validation error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]

    except Exception as e:
        logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Internal error: {type(e).__name__}")]
```

[↑ Back to Table of Contents](#table-of-contents)

## Testing your server

### Manual testing with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Run your server through inspector
npx @modelcontextprotocol/inspector python -m dbtool_mcp.server
```

### Unit tests

```python
# tests/test_server.py
import pytest
from dbtool_mcp.server import analyze_log, explain_query, suggest_index


@pytest.mark.asyncio
async def test_analyze_log_finds_errors():
    log = """
    2026-01-24 10:00:00 ERROR connection refused
    2026-01-24 10:01:00 INFO checkpoint complete
    2026-01-24 10:02:00 WARNING disk space low
    """
    result = await analyze_log(log, "postgresql", "all")

    assert "Errors found: 1" in result
    assert "Warnings found: 1" in result


@pytest.mark.asyncio
async def test_explain_query_detects_select_star():
    query = "SELECT * FROM users WHERE id = 1"
    result = await explain_query(query, True)

    assert "SELECT *" in result
    assert "specifying columns" in result


@pytest.mark.asyncio
async def test_suggest_index_extracts_columns():
    result = await suggest_index(
        "orders",
        ["SELECT * FROM orders WHERE customer_id = 1"]
    )

    assert "customer_id" in result
    assert "CREATE INDEX" in result
```

Run tests:
```bash
uv run pytest tests/ -v
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Set up an MCP server project with the Python SDK
- Implement tools with proper schemas and execution handlers
- Create resources for static and dynamic data
- Build prompts for reusable workflows
- Handle errors gracefully
- Test your server with MCP Inspector and unit tests

## Next steps

Continue to **[Chapter 14: MCP Clients](./14_mcp_clients.md)** to learn how to connect your server to Cline, OpenCode, and custom clients.

[↑ Back to Table of Contents](#table-of-contents)
