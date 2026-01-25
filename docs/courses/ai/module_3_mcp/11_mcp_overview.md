# Chapter 11: Model Context Protocol (MCP) overview

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-3_MCP-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain what MCP is and why it was created
2. Describe the MCP architecture and its components
3. Identify use cases where MCP adds value
4. Understand the relationship between MCP servers and clients

## Table of contents

- [Introduction](#introduction)
- [What is MCP?](#what-is-mcp)
- [Why MCP matters](#why-mcp-matters)
- [MCP architecture](#mcp-architecture)
- [MCP components](#mcp-components)
- [Real-world use cases](#real-world-use-cases)
- [MCP ecosystem](#mcp-ecosystem)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Large Language Models are powerful, but they have a fundamental limitation: they can only work with the information in their training data and the context you provide. They cannot access your databases, read your documentation, or execute actions in your systems—unless you give them tools.

**Model Context Protocol (MCP)** solves this problem by providing a standardized way to connect AI models with external tools and data sources. Think of it as "USB-C for AI"—a universal connector that works with any compatible system.

[↑ Back to Table of Contents](#table-of-contents)

## What is MCP?

MCP is an **open protocol** developed by Anthropic and released in November 2024. In December 2025, Anthropic donated MCP to the Linux Foundation's Agentic AI Foundation, making it a true industry standard.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MODEL CONTEXT PROTOCOL (MCP)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   BEFORE MCP                           AFTER MCP                            │
│   ──────────                           ─────────                            │
│                                                                             │
│   ┌─────────┐                          ┌─────────┐                          │
│   │   AI    │  Custom                  │   AI    │  Standardized            │
│   │  Model  │  Integration             │  Model  │  MCP Protocol            │
│   └────┬────┘  for each tool           └────┬────┘                          │
│        │                                    │                               │
│   ┌────┴────┐                          ┌────┴────┐                          │
│   │ Custom  │                          │   MCP   │                          │
│   │  Code   │                          │ Client  │                          │
│   └────┬────┘                          └────┬────┘                          │
│        │                                    │                               │
│   ┌────┼────┬────┐                    ┌─────┼─────┐                         │
│   │    │    │    │                    │     │     │                         │
│   ▼    ▼    ▼    ▼                    ▼     ▼     ▼                         │
│  DB   Git  API  File              ┌───────────────────┐                     │
│                                   │ Any MCP Server    │                     │
│   Each integration                │ (DB, Git, API...) │                     │
│   requires custom code            │                   │                     │
│                                   │ One protocol,     │                     │
│                                   │ infinite tools    │                     │
│                                   └───────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core concept

MCP defines a standard way for:

1. **AI applications** (clients) to discover available tools
2. **Tool providers** (servers) to expose their capabilities
3. **Both sides** to communicate using a common protocol

This means you can build an MCP server once, and it works with any MCP-compatible client—Claude, Cline, OpenCode, or your own custom application.

[↑ Back to Table of Contents](#table-of-contents)

## Why MCP matters

### The problem MCP solves

Without MCP, every AI integration requires custom code:

```python
# Without MCP: Custom integration for each tool
def call_database(query):
    # Custom database code
    pass

def call_git(command):
    # Custom git code
    pass

def call_api(endpoint):
    # Custom API code
    pass

# Your AI code must know about each tool specifically
if tool == "database":
    call_database(query)
elif tool == "git":
    call_git(command)
# ... endless if/else for each tool
```

With MCP, one protocol handles everything:

```python
# With MCP: Standardized interface
async def call_tool(name: str, arguments: dict):
    return await mcp_client.call_tool(name, arguments)

# AI discovers available tools dynamically
tools = await mcp_client.list_tools()
# Tools might include: analyze_log, query_database, git_commit, etc.
```

### Benefits of MCP

| Benefit | Description |
|:--------|:------------|
| **Standardization** | One protocol for all integrations—learn once, use everywhere |
| **Portability** | MCP servers work with any MCP client |
| **Community** | Thousands of pre-built MCP servers available |
| **Privacy** | Run everything locally with Ollama—data never leaves your network |
| **Extensibility** | Easy to add new tools and capabilities |
| **Separation of concerns** | Tool logic lives in servers; AI logic lives in clients |

### Industry adoption

MCP has become the de-facto standard for AI tool integration:

- **Anthropic** - Created MCP, uses it in Claude Desktop
- **Google** - Adopted MCP alongside their Agent-to-Agent (A2A) protocol
- **OpenAI** - Compatible with MCP through function calling bridges
- **Thousands of community servers** - Databases, APIs, file systems, and more

[↑ Back to Table of Contents](#table-of-contents)

## MCP architecture

MCP uses a client-server architecture with JSON-RPC communication.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP ARCHITECTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                         MCP HOST                                  │     │
│   │   (Claude Desktop, Cline, OpenCode, Your Application)             │     │
│   │                                                                   │     │
│   │   ┌─────────────┐                                                │     │
│   │   │  MCP Client │                                                │     │
│   │   └──────┬──────┘                                                │     │
│   │          │                                                        │     │
│   └──────────┼────────────────────────────────────────────────────────┘     │
│              │                                                              │
│              │ JSON-RPC over stdio or SSE                                   │
│              │                                                              │
│   ┌──────────┼────────────────────────────────────────────────────────┐     │
│   │          │                                                        │     │
│   │   ┌──────▼──────┐  ┌──────────────┐  ┌──────────────┐            │     │
│   │   │ MCP Server  │  │ MCP Server   │  │ MCP Server   │            │     │
│   │   │ (Database)  │  │ (Filesystem) │  │ (Git)        │            │     │
│   │   └──────┬──────┘  └──────┬───────┘  └──────┬───────┘            │     │
│   │          │                │                 │                     │     │
│   │          ▼                ▼                 ▼                     │     │
│   │   ┌──────────┐     ┌──────────┐      ┌──────────┐                │     │
│   │   │ PostgreSQL│    │ Local FS │      │ Git Repo │                │     │
│   │   └──────────┘     └──────────┘      └──────────┘                │     │
│   │                                                                   │     │
│   │                      MCP SERVERS                                  │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Communication flow

1. **Host** starts MCP servers as subprocesses
2. **Client** connects to servers and requests available capabilities
3. **Server** responds with its tools, resources, and prompts
4. **Client** calls tools when the AI model requests them
5. **Server** executes the tool and returns results

### Transport options

| Transport | Description | Use Case |
|:----------|:------------|:---------|
| **stdio** | Standard input/output streams | Local servers, most common |
| **SSE** | Server-Sent Events over HTTP | Remote servers, web-based |

[↑ Back to Table of Contents](#table-of-contents)

## MCP components

MCP defines three core primitives that servers can expose:

### 1. Tools (model-controlled)

Tools are functions the AI can call to perform actions. The model decides when to use them.

```python
# Example: Database log analyzer tool
Tool(
    name="analyze_database_log",
    description="Analyze database error logs and identify issues",
    inputSchema={
        "type": "object",
        "properties": {
            "log_content": {"type": "string", "description": "The log to analyze"},
            "database_type": {"type": "string", "enum": ["postgresql", "sqlserver"]}
        },
        "required": ["log_content"]
    }
)
```

**Use tools for:** Actions, computations, external API calls, database queries.

### 2. Resources (application-controlled)

Resources are data the application can fetch and provide as context. The application decides when to use them.

```python
# Example: Configuration file resource
Resource(
    uri="file:///etc/postgresql/postgresql.conf",
    name="PostgreSQL Configuration",
    description="Current PostgreSQL server configuration",
    mimeType="text/plain"
)
```

**Use resources for:** Configuration files, documentation, reference data.

### 3. Prompts (user-controlled)

Prompts are pre-defined prompt templates the user can invoke. The user explicitly selects them.

```python
# Example: Log analysis prompt template
Prompt(
    name="analyze-logs",
    description="Analyze database logs for errors and performance issues",
    arguments=[
        PromptArgument(name="log_path", description="Path to log file", required=True)
    ]
)
```

**Use prompts for:** Reusable workflows, guided interactions, slash commands.

### When to use each primitive

| Primitive | Controlled By | Example | Use When |
|:----------|:--------------|:--------|:---------|
| **Tool** | AI Model | `analyze_log()` | AI needs to take an action |
| **Resource** | Application | `postgresql.conf` | Providing context data |
| **Prompt** | User | `/analyze-logs` | User-initiated workflows |

[↑ Back to Table of Contents](#table-of-contents)

## Real-world use cases

### Use case 1: Database operations assistant

```text
User: "Analyze today's PostgreSQL error logs and suggest fixes"

MCP Flow:
1. AI calls `read_log_file` tool to fetch today's logs
2. AI calls `analyze_database_log` tool to identify issues
3. AI calls `query_database` tool to check current settings
4. AI responds with analysis and recommendations
```

### Use case 2: Documentation search

```text
User: "How do I configure connection pooling for our setup?"

MCP Flow:
1. Application loads `internal-docs` resource as context
2. AI searches through documentation
3. AI provides answer with links to relevant docs
```

### Use case 3: Code review workflow

```text
User: "/review-pr 1234"

MCP Flow:
1. User invokes `review-pr` prompt
2. Prompt template expands with PR context
3. AI calls `get_pr_diff` tool
4. AI calls `get_pr_comments` tool
5. AI provides structured review feedback
```

[↑ Back to Table of Contents](#table-of-contents)

## MCP ecosystem

### Popular MCP clients

| Client | Type | Best For |
|:-------|:-----|:---------|
| **Claude Desktop** | Desktop app | General use with Claude |
| **Cline** | VS Code extension | IDE-integrated coding |
| **OpenCode** | Terminal TUI | CLI-first developers |
| **Continue** | IDE extension | Code completion |

### Popular MCP servers

| Server | Purpose |
|:-------|:--------|
| **@modelcontextprotocol/server-filesystem** | Local file operations |
| **@modelcontextprotocol/server-postgres** | PostgreSQL database access |
| **@modelcontextprotocol/server-github** | GitHub API integration |
| **@modelcontextprotocol/server-memory** | Persistent memory for conversations |

### Building custom servers

You will build your own MCP server in **[Project 3: Database MCP Server](./project_3_mcp_server.md)** using the Python SDK.

```python
# Preview: Simple MCP server structure
from mcp.server import Server

server = Server("my-database-tools")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="analyze_log", description="Analyze database logs", ...)
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_log":
        return await analyze_log(arguments["content"])
```

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **MCP** | Model Context Protocol - open standard for AI-tool integration |
| **MCP Host** | Application that runs MCP clients (Claude Desktop, Cline) |
| **MCP Client** | Component that communicates with MCP servers |
| **MCP Server** | Process that exposes tools, resources, or prompts |
| **Tool** | Function the AI can call to perform actions |
| **Resource** | Data the application can fetch for context |
| **Prompt** | Pre-defined template the user can invoke |
| **JSON-RPC** | Protocol used for client-server communication |
| **stdio** | Transport using standard input/output streams |
| **SSE** | Server-Sent Events transport for HTTP-based servers |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- MCP is an open protocol for connecting AI models with external tools and data
- It uses a client-server architecture with JSON-RPC communication
- Three primitives: tools (AI-controlled), resources (app-controlled), prompts (user-controlled)
- MCP enables portable, reusable integrations across different AI clients
- Thousands of pre-built servers exist, and you can build custom ones

## Next steps

Continue to **[Chapter 12: MCP Primitives](./12_mcp_primitives.md)** to learn when and how to use tools, resources, and prompts effectively.

## Additional resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [local-ai-hub MCP Integration Guide](../../../projects/local-ai-hub/mcp-integration.md)

[↑ Back to Table of Contents](#table-of-contents)
