# Chapter 16: Agent fundamentals

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-4_Agentic_AI-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Define what an AI agent is and how it differs from a simple LLM
2. Identify the three core components of an agent (prompt, memory, tools)
3. Explain the agent execution loop
4. Recognize when to use agents vs simple prompts

## Table of contents

- [Introduction](#introduction)
- [What is an AI agent?](#what-is-an-ai-agent)
- [Agent components](#agent-components)
- [The agent execution loop](#the-agent-execution-loop)
- [Agents vs simple LLM calls](#agents-vs-simple-llm-calls)
- [Types of agents](#types-of-agents)
- [Agent capabilities and limitations](#agent-capabilities-and-limitations)
- [Enterprise adoption landscape](#enterprise-adoption-landscape)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

So far in this course, you have learned to interact with LLMs through prompts and extend their capabilities with tools via MCP. But what if you want an AI that can autonomously plan and execute multi-step tasks?

This is where **agentic AI** comes in. An agent is an AI system that can take initiative, make decisions, use tools, and adapt its approach based on results—all without constant human direction.

Gartner predicts that **40% of enterprise applications will embed AI agents by the end of 2026**, up from less than 5% in 2025. Understanding how agents work is essential for building modern AI systems.

[↑ Back to Table of Contents](#table-of-contents)

## What is an AI agent?

An **AI agent** is an autonomous system that uses an LLM as its reasoning engine to plan, execute, and adapt actions toward achieving a goal.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIMPLE LLM VS AGENT                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SIMPLE LLM                           AI AGENT                             │
│   ──────────                           ────────                             │
│                                                                             │
│   User ──► LLM ──► Response            User ──► Agent ──┐                   │
│                                                         │                   │
│   One input, one output                                 ▼                   │
│   No memory between calls              ┌──────────────────────┐             │
│   Cannot use tools                     │   Planning Layer     │             │
│   Cannot take actions                  │   "What steps are    │             │
│                                        │    needed?"          │             │
│                                        └──────────┬───────────┘             │
│                                                   │                         │
│                                                   ▼                         │
│                                        ┌──────────────────────┐             │
│                                        │   Execution Loop     │◄───┐        │
│                                        │   • Call tools       │    │        │
│                                        │   • Observe results  │    │        │
│                                        │   • Decide next step │────┘        │
│                                        └──────────┬───────────┘             │
│                                                   │                         │
│                                                   ▼                         │
│                                                Result                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key characteristics of agents

| Characteristic | Description |
|:---------------|:------------|
| **Autonomy** | Makes decisions without constant human input |
| **Goal-oriented** | Works toward a specific objective |
| **Tool use** | Calls external tools/APIs to take actions |
| **Memory** | Maintains context across multiple steps |
| **Adaptability** | Adjusts approach based on results |

[↑ Back to Table of Contents](#table-of-contents)

## Agent components

Every AI agent consists of three core components:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AGENT COMPONENTS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                          PROMPT                                   │     │
│   │   The agent's "blueprint" - defines goals, constraints, and       │     │
│   │   how it should reason about problems.                            │     │
│   │                                                                   │     │
│   │   • System instructions                                           │     │
│   │   • Role definition                                               │     │
│   │   • Output format requirements                                    │     │
│   │   • Safety constraints                                            │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                          MEMORY                                   │     │
│   │   The agent's knowledge store - enables continuity and learning.  │     │
│   │                                                                   │     │
│   │   • Conversation history (short-term)                             │     │
│   │   • Retrieved documents (RAG)                                     │     │
│   │   • Past actions and results                                      │     │
│   │   • Learned preferences (long-term)                               │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                          TOOLS                                    │     │
│   │   The agent's capabilities - actions it can take in the world.    │     │
│   │                                                                   │     │
│   │   • API calls (databases, services)                               │     │
│   │   • File operations (read, write)                                 │     │
│   │   • Code execution                                                │     │
│   │   • Web search and browsing                                       │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1. Prompt (the blueprint)

The prompt defines how the agent operates. Unlike a simple LLM prompt, an agent's prompt includes instructions for reasoning and decision-making.

```text
Example: Database Operations Agent Prompt
─────────────────────────────────────────

ROLE: You are a database operations agent specializing in PostgreSQL troubleshooting.

CAPABILITIES:
- Read error logs via the read_log tool
- Query database metrics via the query_metrics tool
- Execute diagnostic queries via the run_query tool
- Suggest configuration changes

WORKFLOW:
1. When given a problem, first gather information using your tools
2. Analyze the data to form hypotheses
3. Validate hypotheses by gathering more data if needed
4. Provide actionable recommendations with evidence

CONSTRAINTS:
- Never execute DDL or DML statements without explicit user approval
- Always explain your reasoning before taking actions
- If uncertain, ask for clarification rather than guessing
```

### 2. Memory (the knowledge store)

Memory enables agents to maintain context across multiple interactions and tool calls.

| Memory Type | Duration | Purpose | Example |
|:------------|:---------|:--------|:--------|
| **Working memory** | Current session | Track conversation and actions | "I already checked the error log" |
| **Short-term memory** | Recent history | Remember recent context | Last few conversations |
| **Long-term memory** | Persistent | Learn from past interactions | "User prefers JSON output" |
| **Retrieved memory** | On-demand | Access external knowledge (RAG) | Documentation, runbooks |

### 3. Tools (the capabilities)

Tools extend what the agent can do beyond text generation. This is where MCP connects to agentic AI.

```python
# Example: Tools available to a database agent
tools = [
    Tool(
        name="read_log",
        description="Read database error logs",
        parameters={"log_path": "string", "lines": "integer"}
    ),
    Tool(
        name="query_metrics",
        description="Get database performance metrics",
        parameters={"metric_name": "string", "time_range": "string"}
    ),
    Tool(
        name="run_query",
        description="Execute a read-only SQL query",
        parameters={"query": "string"}
    ),
    Tool(
        name="suggest_fix",
        description="Generate a fix recommendation",
        parameters={"issue_description": "string"}
    )
]
```

[↑ Back to Table of Contents](#table-of-contents)

## The agent execution loop

Agents operate in a continuous loop of reasoning and acting.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AGENT EXECUTION LOOP                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ START: User provides goal                                           │   │
│   │ "Diagnose why database connections are timing out"                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ THINK: Agent reasons about the task                                 │   │
│   │ "I need to check connection pool status and recent errors"          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ACT: Agent calls a tool                                             │   │
│   │ query_metrics(metric_name="pg_stat_activity", time_range="1h")      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ OBSERVE: Agent receives tool result                                 │   │
│   │ "150 active connections, 45 idle in transaction, max=200"           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ DECIDE: Is the goal achieved?                                       │   │
│   │ NO ──► Loop back to THINK with new information                      │   │
│   │ YES ──► Proceed to final response                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ RESPOND: Agent provides final answer                                │   │
│   │ "The connection timeouts are caused by 45 'idle in transaction'     │   │
│   │  sessions consuming pool slots. Recommend: SET idle_in_transaction_ │   │
│   │  session_timeout = '5min' and investigate application code."        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The ReAct pattern

The most common agent pattern is **ReAct (Reasoning + Acting)**:

1. **Reason**: Think about what to do next
2. **Act**: Execute a tool or action
3. **Observe**: Process the result
4. **Repeat**: Continue until goal is achieved

```text
Example ReAct trace:
────────────────────

Thought: I need to check the error logs to understand the timeout issue.
Action: read_log(log_path="/var/log/postgresql/postgresql-15-main.log", lines=100)
Observation: [Log shows "too many connections" errors at 09:15, 09:23, 09:31]

Thought: The logs show connection saturation. I should check current connection status.
Action: query_metrics(metric_name="pg_stat_activity")
Observation: [150 active, 45 idle_in_transaction, 5 idle, max_connections=200]

Thought: 45 idle_in_transaction connections are blocking the pool. This is likely the cause.
Action: run_query(query="SELECT pid, state, query_start FROM pg_stat_activity WHERE state = 'idle in transaction' ORDER BY query_start LIMIT 5")
Observation: [5 queries from app_service running for >30 minutes]

Thought: I have enough information to diagnose the issue.
Final Answer: Connection timeouts are caused by long-running 'idle in transaction' sessions from app_service. Recommend setting idle_in_transaction_session_timeout and investigating the application code.
```

[↑ Back to Table of Contents](#table-of-contents)

## Agents vs simple LLM calls

Not every task needs an agent. Use this guide to decide:

| Criteria | Simple LLM | Agent |
|:---------|:-----------|:------|
| **Steps** | Single step | Multiple steps |
| **Tools needed** | None | One or more |
| **Decisions** | User makes decisions | AI makes decisions |
| **Latency tolerance** | Need fast response | Can wait for quality |
| **Error tolerance** | Low stakes | Need verification loops |

### When to use a simple LLM call

- Answering questions from context
- Generating text (emails, documentation)
- Summarizing content
- Classifying or extracting information
- Single-turn conversations

### When to use an agent

- Multi-step troubleshooting
- Tasks requiring external data gathering
- Automated workflows with decision points
- Complex analysis requiring multiple tools
- Tasks that need verification and iteration

### Example: Same task, different approaches

**Task**: "Why is the database slow?"

**Simple LLM approach:**
```text
User provides: Query, execution plan, and relevant metrics
LLM analyzes: All information in one call
Output: Analysis based on provided data only
```

**Agent approach:**
```text
1. Agent reads error logs (tool call)
2. Agent queries current metrics (tool call)
3. Agent checks recent deployments (tool call)
4. Agent correlates findings
5. Agent asks clarifying questions if needed
6. Agent provides comprehensive diagnosis
```

[↑ Back to Table of Contents](#table-of-contents)

## Types of agents

### Single-purpose agents

Specialized for one domain or task type.

| Agent Type | Purpose | Example Tools |
|:-----------|:--------|:--------------|
| **Database agent** | Database operations | query, analyze_log, suggest_index |
| **Code review agent** | Code analysis | read_file, lint, test |
| **Documentation agent** | Doc management | search_docs, validate, convert |

### Multi-agent systems

Multiple specialized agents working together. This is a key trend for 2026.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌───────────────┐                                    │
│                        │  Orchestrator │                                    │
│                        │    Agent      │                                    │
│                        └───────┬───────┘                                    │
│                                │                                            │
│              ┌─────────────────┼─────────────────┐                          │
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│       ┌──────────┐      ┌──────────┐      ┌──────────┐                      │
│       │ Database │      │   Code   │      │   Docs   │                      │
│       │  Agent   │      │  Agent   │      │  Agent   │                      │
│       └──────────┘      └──────────┘      └──────────┘                      │
│                                                                             │
│   Example workflow:                                                         │
│   1. User: "Investigate slow API endpoint /users/search"                    │
│   2. Orchestrator delegates to Code Agent: "Find the endpoint code"         │
│   3. Orchestrator delegates to Database Agent: "Analyze the query"          │
│   4. Orchestrator delegates to Docs Agent: "Find related runbooks"          │
│   5. Orchestrator synthesizes findings into report                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Gartner reported a **1,445% surge** in multi-agent system inquiries from Q1 2024 to Q2 2025.

[↑ Back to Table of Contents](#table-of-contents)

## Agent capabilities and limitations

### What agents can do well

| Capability | Example |
|:-----------|:--------|
| **Information gathering** | Collect data from multiple sources before analysis |
| **Multi-step reasoning** | Break complex problems into smaller steps |
| **Tool orchestration** | Coordinate multiple tools toward a goal |
| **Error recovery** | Detect and retry failed operations |
| **Adaptive behavior** | Adjust approach based on intermediate results |

### Current limitations

| Limitation | Mitigation |
|:-----------|:-----------|
| **Reliability** | Agents can get stuck in loops or make poor decisions | Add guardrails, timeouts, human approval for critical actions |
| **Cost** | Multiple LLM calls per task increase API costs | Use smaller models for simple steps, cache common operations |
| **Latency** | Multi-step execution is slower than single calls | Parallelize independent steps, use streaming |
| **Observability** | Hard to understand why agents made decisions | Implement detailed logging, trace reasoning steps |

> [!WARNING]
> **Agents are not infallible.** Always implement human-in-the-loop for high-stakes operations like database modifications, deployments, or security changes.

[↑ Back to Table of Contents](#table-of-contents)

## Enterprise adoption landscape

Based on Deloitte's 2025 research:

| Stage | Percentage | Description |
|:------|:-----------|:------------|
| Exploring | 30% | Evaluating agentic options |
| Piloting | 38% | Running pilot projects |
| Ready to deploy | 14% | Solutions ready for production |
| In production | 11% | Actively using agents |
| No strategy | 35% | No formal agentic strategy |
| Developing strategy | 42% | Creating agentic roadmap |

### Key success factors

1. **Redesign workflows** - Don't just layer agents onto existing processes
2. **Build agent-compatible architectures** - Design systems for AI interaction
3. **Implement governance** - Establish oversight and audit capabilities
4. **Start small** - Begin with low-risk, high-value use cases

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **AI Agent** | Autonomous system using LLM for reasoning to achieve goals |
| **Agentic AI** | AI systems designed to take autonomous actions |
| **ReAct** | Reasoning + Acting pattern for agent execution |
| **Tool** | External capability an agent can invoke |
| **Memory** | Agent's ability to maintain context across steps |
| **Orchestrator** | Agent that coordinates other agents |
| **Human-in-the-loop** | Design pattern requiring human approval for critical actions |
| **Guardrails** | Constraints preventing harmful or unintended actions |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Agents are autonomous AI systems that plan, execute, and adapt toward goals
- Three core components: prompt (blueprint), memory (knowledge), tools (capabilities)
- Agents operate in a think-act-observe loop (ReAct pattern)
- Use agents for multi-step tasks requiring tools; use simple LLMs for single-turn tasks
- Multi-agent systems are becoming increasingly important for complex workflows
- Always implement guardrails and human oversight for production agents

## Next steps

Continue to **[Chapter 17: Agent Patterns](./17_agent_patterns.md)** to learn specific patterns like ReAct, plan-and-execute, and reflection.

## Additional resources

- [IBM Guide to AI Agents](https://www.ibm.com/think/ai-agents)
- [Deloitte Agentic AI Strategy](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)
- [Machine Learning Mastery: Agentic AI Roadmap](https://machinelearningmastery.com/the-roadmap-for-mastering-agentic-ai-in-2026/)
- [Aisera: Agentic AI Technical Overview](https://aisera.com/blog/agentic-ai/)

[↑ Back to Table of Contents](#table-of-contents)
