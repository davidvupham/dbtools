# Chapter 12: MCP primitives

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-3_MCP-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Distinguish between tools, resources, and prompts
2. Design tools for model-controlled actions
3. Create resources for application-controlled data
4. Implement prompts for user-controlled workflows

## Table of contents

- [Introduction](#introduction)
- [The three primitives](#the-three-primitives)
- [Tools: Model-controlled actions](#tools-model-controlled-actions)
- [Resources: Application-controlled data](#resources-application-controlled-data)
- [Prompts: User-controlled workflows](#prompts-user-controlled-workflows)
- [Choosing the right primitive](#choosing-the-right-primitive)
- [Combining primitives](#combining-primitives)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

MCP defines three primitives—tools, resources, and prompts—each with different control semantics. Understanding when to use each is crucial for designing effective MCP integrations.

[↑ Back to Table of Contents](#table-of-contents)

## The three primitives

```text
MCP PRIMITIVES OVERVIEW
═══════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   TOOLS                    RESOURCES                 PROMPTS                │
│   ══════                   ═════════                 ═══════                │
│                                                                             │
│   Controlled by:           Controlled by:            Controlled by:         │
│   AI MODEL                 APPLICATION               USER                   │
│                                                                             │
│   Purpose:                 Purpose:                  Purpose:               │
│   Take actions             Provide context           Guide workflows        │
│                                                                             │
│   Example:                 Example:                  Example:               │
│   query_database()         postgresql.conf           /analyze-logs          │
│   send_alert()             runbook.md                /create-report         │
│   execute_command()        metrics.json              /review-config         │
│                                                                             │
│   When invoked:            When invoked:             When invoked:          │
│   Model decides            App loads as context      User explicitly calls  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Quick comparison

| Aspect | Tools | Resources | Prompts |
|:-------|:------|:----------|:--------|
| **Control** | Model decides when to use | App decides when to load | User explicitly invokes |
| **Purpose** | Perform actions | Provide data | Template workflows |
| **Execution** | Active (does something) | Passive (data only) | Generates prompt text |
| **Examples** | API calls, queries, commands | Configs, docs, files | Slash commands, wizards |

[↑ Back to Table of Contents](#table-of-contents)

## Tools: Model-controlled actions

**Tools** are functions the AI model can call to perform actions. The model decides when and how to use them based on the user's request.

### Tool anatomy

```python
Tool(
    name="query_database",
    description="Execute a read-only SQL query against the database",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SQL query to execute"
            },
            "database": {
                "type": "string",
                "enum": ["production", "staging", "development"],
                "description": "Target database environment"
            }
        },
        "required": ["query", "database"]
    }
)
```

### Good tool design

**Clear, action-oriented names:**
```text
✅ analyze_log_file
✅ get_database_metrics
✅ suggest_index
✅ validate_configuration

❌ data (too vague)
❌ helper (not descriptive)
❌ process (what does it process?)
```

**Precise descriptions:**
```text
✅ "Analyze PostgreSQL error logs and return structured findings including
    severity, category, and recommended actions."

❌ "Analyzes logs." (too vague)
❌ "This tool is used for log analysis and can help identify errors."
    (verbose but not specific)
```

**Well-defined schemas:**
```python
# Good: Specific, constrained inputs
inputSchema={
    "type": "object",
    "properties": {
        "severity": {
            "type": "string",
            "enum": ["critical", "error", "warning", "info"],
            "description": "Minimum severity level to include"
        },
        "hours": {
            "type": "integer",
            "minimum": 1,
            "maximum": 168,
            "default": 24,
            "description": "How many hours of logs to analyze"
        }
    }
}

# Bad: Unconstrained, ambiguous
inputSchema={
    "type": "object",
    "properties": {
        "options": {
            "type": "string",
            "description": "Various options"
        }
    }
}
```

### Tool patterns

**Query tools:**
```python
Tool(
    name="get_table_stats",
    description="Get statistics for a database table including row count, size, and index usage",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {"type": "string"},
            "include_indexes": {"type": "boolean", "default": True}
        },
        "required": ["table_name"]
    }
)
```

**Analysis tools:**
```python
Tool(
    name="explain_query",
    description="Analyze a SQL query's execution plan and explain performance characteristics",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "format": {"type": "string", "enum": ["text", "json"], "default": "text"}
        },
        "required": ["query"]
    }
)
```

**Action tools:**
```python
Tool(
    name="create_alert",
    description="Create a monitoring alert for a database metric threshold",
    inputSchema={
        "type": "object",
        "properties": {
            "metric": {"type": "string"},
            "threshold": {"type": "number"},
            "severity": {"type": "string", "enum": ["info", "warning", "critical"]}
        },
        "required": ["metric", "threshold", "severity"]
    }
)
```

[↑ Back to Table of Contents](#table-of-contents)

## Resources: Application-controlled data

**Resources** are data sources the application can load and provide as context. Unlike tools, the AI doesn't call resources—the application decides when to include them.

### Resource anatomy

```python
Resource(
    uri="file:///etc/postgresql/postgresql.conf",
    name="PostgreSQL Configuration",
    description="Current PostgreSQL server configuration file",
    mimeType="text/plain"
)
```

### Resource types

**File resources:**
```python
Resource(
    uri="file:///var/log/postgresql/postgresql-15-main.log",
    name="PostgreSQL Log",
    description="Recent PostgreSQL server log entries",
    mimeType="text/plain"
)
```

**Dynamic resources:**
```python
Resource(
    uri="metrics://database/current",
    name="Current Database Metrics",
    description="Real-time database performance metrics",
    mimeType="application/json"
)
```

**Documentation resources:**
```python
Resource(
    uri="docs://runbooks/connection-issues",
    name="Connection Troubleshooting Runbook",
    description="Standard procedures for diagnosing connection problems",
    mimeType="text/markdown"
)
```

### Resource templates

Use templates for parameterized resources:

```python
ResourceTemplate(
    uriTemplate="logs://database/{database}/{date}",
    name="Database Logs",
    description="Logs for a specific database and date"
)

# Client can request:
# logs://database/production/2026-01-24
# logs://database/staging/2026-01-23
```

### When to use resources vs tools

| Use Resource When | Use Tool When |
|:------------------|:--------------|
| Data is context/background | Action is needed |
| App decides what's relevant | Model decides what's needed |
| Passive data loading | Active computation |
| Configuration, docs, logs | Queries, analysis, commands |

[↑ Back to Table of Contents](#table-of-contents)

## Prompts: User-controlled workflows

**Prompts** are pre-defined templates that users explicitly invoke. They're ideal for reusable workflows and "slash commands."

### Prompt anatomy

```python
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
            name="table_sizes",
            description="Approximate table sizes (optional)",
            required=False
        )
    ]
)
```

### How prompts work

When a user invokes a prompt, the server returns expanded prompt content:

```text
USER INVOKES: /analyze-slow-query

Server returns prompt messages:
┌─────────────────────────────────────────────────────────────────────────────┐
│ {                                                                           │
│   "messages": [                                                             │
│     {                                                                       │
│       "role": "system",                                                     │
│       "content": "You are a SQL performance analyst. Analyze queries..."   │
│     },                                                                      │
│     {                                                                       │
│       "role": "user",                                                       │
│       "content": "Analyze this query:\n{query}\n\nTable sizes: {sizes}"    │
│     }                                                                       │
│   ]                                                                         │
│ }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prompt examples

**Diagnostic workflow:**
```python
Prompt(
    name="diagnose-connection",
    description="Diagnose database connection issues step by step",
    arguments=[
        PromptArgument(name="symptoms", description="What symptoms are you seeing?", required=True),
        PromptArgument(name="environment", description="production/staging/dev", required=True)
    ]
)

# Returns a structured diagnostic prompt with the symptoms and environment
# pre-filled, guiding the user through troubleshooting steps
```

**Report generation:**
```python
Prompt(
    name="weekly-report",
    description="Generate weekly database health report",
    arguments=[
        PromptArgument(name="week", description="Week to report on (YYYY-WW)", required=True),
        PromptArgument(name="focus_areas", description="Specific areas to highlight", required=False)
    ]
)
```

**Configuration review:**
```python
Prompt(
    name="review-config",
    description="Review database configuration against best practices",
    arguments=[
        PromptArgument(name="config_type", description="postgresql/mysql/mongodb", required=True),
        PromptArgument(name="workload", description="oltp/olap/mixed", required=True)
    ]
)
```

[↑ Back to Table of Contents](#table-of-contents)

## Choosing the right primitive

### Decision flowchart

```text
PRIMITIVE SELECTION
═══════════════════

Start: What do you need?
         │
         ├── Take an action (query, modify, call API)?
         │   └── Use TOOL
         │
         ├── Provide context/background data?
         │   └── Use RESOURCE
         │
         └── Reusable user-initiated workflow?
             └── Use PROMPT
```

### Examples by scenario

| Scenario | Primitive | Reasoning |
|:---------|:----------|:----------|
| Execute SQL query | Tool | Active action, model decides when |
| Load config file | Resource | Passive context, app decides |
| "Analyze my query" command | Prompt | User-initiated workflow |
| Get current metrics | Tool | Active data fetch |
| Include runbook in context | Resource | Background information |
| "/create-incident" slash command | Prompt | User-triggered template |
| Send alert notification | Tool | Active action |
| Load previous conversation | Resource | Context data |

[↑ Back to Table of Contents](#table-of-contents)

## Combining primitives

Real applications combine all three primitives:

```text
COMBINED EXAMPLE: Database Health Check
═══════════════════════════════════════

User: /health-check production

┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  PROMPT (user invokes)                                                       │
│  ─────────────────────                                                       │
│  /health-check expands to structured diagnostic workflow                     │
│                                                                              │
│           │                                                                  │
│           ▼                                                                  │
│                                                                              │
│  RESOURCES (app loads)                                                       │
│  ─────────────────────                                                       │
│  • postgresql.conf (current configuration)                                   │
│  • runbook://health-check (standard procedures)                              │
│  • baselines.json (normal metric ranges)                                     │
│                                                                              │
│           │                                                                  │
│           ▼                                                                  │
│                                                                              │
│  TOOLS (model calls as needed)                                               │
│  ─────────────────────────────                                               │
│  • get_metrics() - fetch current metrics                                     │
│  • query_database() - check active connections                               │
│  • analyze_logs() - check for recent errors                                  │
│  • compare_baseline() - compare against normal ranges                        │
│                                                                              │
│           │                                                                  │
│           ▼                                                                  │
│                                                                              │
│  AI generates comprehensive health report using all inputs                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- **Tools** are model-controlled actions—the AI decides when to call them
- **Resources** are app-controlled data—the application loads them as context
- **Prompts** are user-controlled templates—users explicitly invoke them
- Choose primitives based on who controls when they're used
- Combine primitives for powerful, flexible integrations

## Next steps

Continue to **[Chapter 13: Building MCP Servers](./13_building_mcp_servers.md)** to learn how to implement your own MCP server in Python.

[↑ Back to Table of Contents](#table-of-contents)
