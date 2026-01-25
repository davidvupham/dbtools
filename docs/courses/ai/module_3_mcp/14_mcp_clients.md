# Chapter 14: MCP clients

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-3_MCP-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Configure Cline to use your MCP server
2. Set up OpenCode with MCP integration
3. Build a custom MCP client for Ollama
4. Choose the right client for your workflow

## Table of contents

- [Introduction](#introduction)
- [MCP client landscape](#mcp-client-landscape)
- [Cline configuration](#cline-configuration)
- [OpenCode configuration](#opencode-configuration)
- [Custom client with Ollama](#custom-client-with-ollama)
- [Client comparison](#client-comparison)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

MCP servers are only useful when connected to clients. This chapter covers the most popular MCP-compatible clients and how to configure them with your custom servers and local LLMs.

[↑ Back to Table of Contents](#table-of-contents)

## MCP client landscape

```text
MCP CLIENT OPTIONS
══════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                          COMMERCIAL                                         │
│                                                                             │
│   ┌─────────────────┐   ┌─────────────────┐                                 │
│   │ Claude Desktop  │   │    Cursor       │                                 │
│   │                 │   │                 │                                 │
│   │ • Anthropic API │   │ • Multiple LLMs │                                 │
│   │ • Full MCP      │   │ • IDE-based     │                                 │
│   │ • Desktop app   │   │ • Code-focused  │                                 │
│   └─────────────────┘   └─────────────────┘                                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          OPEN SOURCE                                        │
│                                                                             │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐           │
│   │     Cline       │   │    OpenCode     │   │     Aider       │           │
│   │                 │   │                 │   │                 │           │
│   │ • VS Code ext   │   │ • Terminal TUI  │   │ • Terminal      │           │
│   │ • Full MCP      │   │ • Full MCP      │   │ • Limited MCP   │           │
│   │ • Ollama ready  │   │ • Ollama ready  │   │ • Git-focused   │           │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Cline configuration

Cline is a VS Code extension that provides full MCP support with Ollama integration.

### Install Cline

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search "Cline"
4. Click Install

### Configure for Ollama

```json
// VS Code settings.json
{
    "cline.apiProvider": "ollama",
    "cline.ollamaBaseUrl": "http://localhost:11434",
    "cline.ollamaModel": "qwen2.5:7b"
}
```

### Add MCP servers

Create or edit the MCP settings file:

**Linux/macOS:**
```
~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Windows:**
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

```json
{
    "mcpServers": {
        "dbtool": {
            "command": "python",
            "args": ["-m", "dbtool_mcp.server"],
            "cwd": "/path/to/dbtool-mcp-server",
            "env": {
                "PYTHONPATH": "/path/to/dbtool-mcp-server/src"
            }
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/home/user/projects"
            ]
        }
    }
}
```

### Using Cline with your server

Once configured, Cline automatically discovers your tools:

```text
User: "Analyze the PostgreSQL logs from today"

Cline:
1. [Calls dbtool:analyze_log tool]
2. Receives analysis results
3. Presents findings to user
```

### Cline best practices

| Practice | Reason |
|:---------|:-------|
| Use absolute paths | Avoids working directory issues |
| Set PYTHONPATH explicitly | Ensures module imports work |
| Test server independently first | Isolate MCP vs server issues |
| Check Cline output panel | See MCP communication logs |

[↑ Back to Table of Contents](#table-of-contents)

## OpenCode configuration

OpenCode is a terminal-based AI coding assistant with excellent MCP support.

### Install OpenCode

```bash
# Using pipx (recommended)
pipx install opencode-ai

# Or with pip
pip install opencode-ai
```

### Configure for Ollama + MCP

Create config file at `~/.config/opencode/config.yaml`:

```yaml
# LLM Configuration
llm:
    provider: ollama
    model: qwen2.5:7b
    base_url: http://localhost:11434
    temperature: 0.3
    max_tokens: 4096

# MCP Servers
mcp:
    servers:
        dbtool:
            command: python
            args:
                - -m
                - dbtool_mcp.server
            cwd: /path/to/dbtool-mcp-server
            env:
                PYTHONPATH: /path/to/dbtool-mcp-server/src

        filesystem:
            command: npx
            args:
                - -y
                - "@modelcontextprotocol/server-filesystem"
                - /home/user/projects

# Tool settings
tools:
    auto_approve: false  # Require confirmation for tool calls
    timeout: 30          # Seconds before timeout
```

### Using OpenCode

```bash
# Start OpenCode in your project
cd /path/to/project
opencode

# In the TUI
> Analyze the PostgreSQL error logs in /var/log/postgresql/

# OpenCode will:
# 1. Connect to your MCP servers
# 2. Call appropriate tools
# 3. Display results
```

### OpenCode keyboard shortcuts

| Key | Action |
|:----|:-------|
| `Enter` | Send message |
| `Ctrl+C` | Cancel current operation |
| `Ctrl+L` | Clear screen |
| `/tools` | List available tools |
| `/help` | Show help |

[↑ Back to Table of Contents](#table-of-contents)

## Custom client with Ollama

For full control, build a custom MCP client that uses Ollama directly.

### Basic client structure

```python
# custom_mcp_client.py
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx


class OllamaMCPClient:
    """MCP client using Ollama for inference."""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "qwen2.5:7b"
    ):
        self.ollama_host = ollama_host
        self.model = model
        self.sessions: dict[str, ClientSession] = {}
        self.available_tools: list = []

    async def connect_server(self, name: str, command: str, args: list[str]):
        """Connect to an MCP server."""
        server_params = StdioServerParameters(command=command, args=args)

        read, write = await stdio_client(server_params).__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()

        # Get available tools
        tools_result = await session.list_tools()
        for tool in tools_result.tools:
            self.available_tools.append({
                "name": f"{name}:{tool.name}",
                "server": name,
                "tool": tool
            })

        self.sessions[name] = session
        return session

    async def chat(self, message: str) -> str:
        """Send message and handle tool calls."""
        # Format tools for Ollama
        tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["tool"].description,
                    "parameters": t["tool"].inputSchema
                }
            }
            for t in self.available_tools
        ]

        # Initial request to Ollama
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": message}],
                    "tools": tools,
                    "stream": False
                }
            )
            result = response.json()

        message_content = result.get("message", {})
        tool_calls = message_content.get("tool_calls", [])

        # Handle tool calls
        if tool_calls:
            tool_results = []
            for call in tool_calls:
                func = call.get("function", {})
                full_name = func.get("name", "")
                arguments = json.loads(func.get("arguments", "{}"))

                # Parse server:tool_name
                if ":" in full_name:
                    server_name, tool_name = full_name.split(":", 1)
                else:
                    # Fallback: find server
                    for t in self.available_tools:
                        if t["tool"].name == full_name:
                            server_name = t["server"]
                            tool_name = full_name
                            break

                # Call the tool via MCP
                session = self.sessions.get(server_name)
                if session:
                    result = await session.call_tool(tool_name, arguments)
                    tool_results.append({
                        "tool": full_name,
                        "result": str(result)
                    })

            # Return combined results
            return "\n\n".join(
                f"**{r['tool']}:**\n{r['result']}"
                for r in tool_results
            )

        # No tool calls - return direct response
        return message_content.get("content", "")

    async def close(self):
        """Close all sessions."""
        for session in self.sessions.values():
            await session.__aexit__(None, None, None)


async def main():
    """Example usage."""
    client = OllamaMCPClient()

    # Connect to your MCP server
    await client.connect_server(
        "dbtool",
        "python",
        ["-m", "dbtool_mcp.server"]
    )

    print(f"Connected! Available tools: {[t['name'] for t in client.available_tools]}")

    # Interactive loop
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        response = await client.chat(user_input)
        print(f"\nAssistant: {response}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Running the custom client

```bash
# Install dependencies
pip install mcp httpx

# Run
python custom_mcp_client.py
```

### Example session

```text
Connected! Available tools: ['dbtool:analyze_log', 'dbtool:explain_query', 'dbtool:suggest_index']

You: Analyze this log: "2026-01-24 ERROR: connection refused to host 10.0.0.5"

**dbtool:analyze_log:**
Log analysis complete.
- Error type: Connection refused
- Target host: 10.0.0.5
- Likely cause: Firewall blocking connection or service not running on target
- Recommendation: Check network connectivity and service status on 10.0.0.5
```

[↑ Back to Table of Contents](#table-of-contents)

## Client comparison

### Feature comparison

| Feature | Claude Desktop | Cline | OpenCode | Custom |
|:--------|:---------------|:------|:---------|:-------|
| MCP support | Full | Full | Full | Full |
| Ollama support | No | Yes | Yes | Yes |
| Local models | No | Yes | Yes | Yes |
| GUI | Yes | Yes (VS Code) | TUI | Custom |
| Extensibility | Limited | Medium | Medium | Full |
| Setup complexity | Low | Low | Low | High |

### When to use each client

| Scenario | Recommended Client |
|:---------|:-------------------|
| VS Code workflow | Cline |
| Terminal preference | OpenCode |
| Maximum control | Custom client |
| Non-technical users | Claude Desktop |
| Enterprise deployment | Custom client |
| Quick prototyping | Cline or OpenCode |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- MCP clients connect to servers via stdio or SSE transport
- Cline provides VS Code integration with full MCP and Ollama support
- OpenCode offers terminal-based MCP with excellent keyboard navigation
- Building a custom client gives maximum flexibility for specialized needs
- Choose clients based on your workflow (IDE, terminal, or custom app)

## Next steps

Continue to **[Chapter 15: MCP Patterns](./15_mcp_patterns.md)** to learn about security, error handling, and performance patterns.

[↑ Back to Table of Contents](#table-of-contents)