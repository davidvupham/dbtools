# Chapter 18: Multi-agent systems

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-4_Agentic_AI-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Design multi-agent architectures for complex tasks
2. Implement orchestration patterns for agent coordination
3. Handle inter-agent communication effectively
4. Avoid common multi-agent pitfalls

## Table of contents

- [Introduction](#introduction)
- [Why multi-agent?](#why-multi-agent)
- [Architecture patterns](#architecture-patterns)
- [Orchestration strategies](#orchestration-strategies)
- [Communication patterns](#communication-patterns)
- [Implementation example](#implementation-example)
- [Common pitfalls](#common-pitfalls)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

As tasks become more complex, a single agent may struggle. Multi-agent systems divide work among specialized agents, each expert in a specific domain. Gartner reported a **1,445% surge** in multi-agent system inquiries from 2024 to 2025.

[↑ Back to Table of Contents](#table-of-contents)

## Why multi-agent?

### Single agent limitations

```text
SINGLE AGENT CHALLENGES
═══════════════════════

Complex task: "Investigate slow API endpoint /users/search"

Single agent must:
├── Understand the code (requires code expertise)
├── Analyze database queries (requires DBA expertise)
├── Check infrastructure metrics (requires SRE expertise)
├── Review recent deployments (requires DevOps expertise)
└── Synthesize findings (requires all expertise)

Problems:
- Context window fills up quickly
- Prompt becomes unwieldy
- Jack of all trades, master of none
```

### Multi-agent benefits

| Benefit | Description |
|:--------|:------------|
| **Specialization** | Each agent masters one domain |
| **Parallelization** | Independent tasks run concurrently |
| **Modularity** | Agents can be developed/updated independently |
| **Scalability** | Add agents for new domains |
| **Maintainability** | Smaller, focused prompts per agent |

[↑ Back to Table of Contents](#table-of-contents)

## Architecture patterns

### Hierarchical (orchestrator pattern)

```text
HIERARCHICAL ARCHITECTURE
═════════════════════════

                    ┌──────────────────┐
                    │   Orchestrator   │
                    │      Agent       │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Database      │ │     Code        │ │   Operations    │
│     Agent       │ │     Agent       │ │     Agent       │
└─────────────────┘ └─────────────────┘ └─────────────────┘

Orchestrator responsibilities:
- Decompose task into subtasks
- Delegate to specialist agents
- Synthesize results
- Handle failures
```

### Peer-to-peer (collaborative)

```text
PEER-TO-PEER ARCHITECTURE
═════════════════════════

┌─────────────────┐     ┌─────────────────┐
│   Database      │◄───►│     Code        │
│     Agent       │     │     Agent       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │    ┌─────────────┐    │
         └───►│   Shared    │◄───┘
              │   Memory    │
              └──────┬──────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐     ┌────────▼────────┐
│   Security      │     │   Operations    │
│     Agent       │     │     Agent       │
└─────────────────┘     └─────────────────┘

Agents communicate via shared memory or message passing.
No central coordinator.
```

### Pipeline (sequential)

```text
PIPELINE ARCHITECTURE
═════════════════════

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parser    │───►│  Analyzer   │───►│  Validator  │───►│  Reporter   │
│   Agent     │    │    Agent    │    │    Agent    │    │    Agent    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │                   │
     ▼                   ▼                   ▼                   ▼
  Raw Input         Structured          Validated           Final
                      Data              Findings            Report
```

[↑ Back to Table of Contents](#table-of-contents)

## Orchestration strategies

### Task decomposition

```python
ORCHESTRATOR_PROMPT = """
You are an orchestrator agent. Break down the user's request into subtasks
for specialist agents.

Available agents:
- database_agent: Database queries, performance, configuration
- code_agent: Code analysis, review, understanding
- ops_agent: Infrastructure, metrics, deployments
- docs_agent: Documentation, runbooks, procedures

User request: {request}

Respond with a JSON plan:
{{
    "steps": [
        {{"agent": "agent_name", "task": "specific task description"}},
        ...
    ]
}}
"""


async def orchestrate(request: str) -> str:
    """Orchestrate multi-agent task."""
    # Step 1: Decompose
    plan = await decompose_task(request)

    # Step 2: Execute (parallel where possible)
    independent_steps = group_independent_steps(plan["steps"])
    results = []

    for step_group in independent_steps:
        group_results = await asyncio.gather(*[
            execute_agent(step["agent"], step["task"])
            for step in step_group
        ])
        results.extend(group_results)

    # Step 3: Synthesize
    return await synthesize_results(request, results)
```

### Dynamic delegation

```python
async def delegate_to_specialist(task: str, context: dict) -> str:
    """Dynamically choose and delegate to specialist agent."""
    # Determine which agent should handle this
    agent_choice = await choose_agent(task, context)

    if agent_choice == "database":
        return await database_agent.execute(task, context)
    elif agent_choice == "code":
        return await code_agent.execute(task, context)
    elif agent_choice == "ops":
        return await ops_agent.execute(task, context)
    else:
        # Orchestrator handles directly
        return await handle_directly(task, context)
```

[↑ Back to Table of Contents](#table-of-contents)

## Communication patterns

### Message passing

```python
from dataclasses import dataclass
from typing import Any
from enum import Enum


class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    STATUS = "status"


@dataclass
class AgentMessage:
    sender: str
    receiver: str
    type: MessageType
    content: Any
    correlation_id: str


class MessageBus:
    """Central message bus for agent communication."""

    def __init__(self):
        self.subscribers: dict[str, list] = {}
        self.messages: list[AgentMessage] = []

    def subscribe(self, agent_id: str, callback):
        """Subscribe agent to receive messages."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    async def publish(self, message: AgentMessage):
        """Publish message to receiver."""
        self.messages.append(message)
        callbacks = self.subscribers.get(message.receiver, [])
        for callback in callbacks:
            await callback(message)
```

### Shared memory

```python
class SharedMemory:
    """Shared memory for agent collaboration."""

    def __init__(self):
        self.state: dict[str, Any] = {}
        self.history: list[dict] = []

    def write(self, agent_id: str, key: str, value: Any):
        """Write to shared memory."""
        self.state[key] = value
        self.history.append({
            "agent": agent_id,
            "action": "write",
            "key": key,
            "timestamp": datetime.now()
        })

    def read(self, key: str) -> Any:
        """Read from shared memory."""
        return self.state.get(key)

    def get_context(self) -> str:
        """Get formatted context for agents."""
        return "\n".join(
            f"{k}: {v}" for k, v in self.state.items()
        )
```

[↑ Back to Table of Contents](#table-of-contents)

## Implementation example

### Database investigation system

```python
from dataclasses import dataclass


@dataclass
class Agent:
    name: str
    system_prompt: str
    tools: list[str]


# Define specialist agents
database_agent = Agent(
    name="database_agent",
    system_prompt="""You are a database specialist. Analyze database
    performance, queries, and configuration. Use your tools to gather
    information and provide recommendations.""",
    tools=["query_database", "get_metrics", "analyze_logs"]
)

code_agent = Agent(
    name="code_agent",
    system_prompt="""You are a code analyst. Review code for issues,
    understand application behavior, and identify problematic patterns.""",
    tools=["read_file", "search_code", "get_git_history"]
)

ops_agent = Agent(
    name="ops_agent",
    system_prompt="""You are an operations specialist. Monitor system
    health, check deployments, and analyze infrastructure issues.""",
    tools=["get_system_metrics", "get_deployments", "check_alerts"]
)


class MultiAgentInvestigator:
    """Multi-agent system for investigating issues."""

    def __init__(self):
        self.agents = {
            "database": database_agent,
            "code": code_agent,
            "ops": ops_agent
        }
        self.memory = SharedMemory()

    async def investigate(self, issue: str) -> str:
        """Investigate an issue using multiple agents."""
        # Phase 1: Initial assessment (parallel)
        initial_findings = await asyncio.gather(
            self.run_agent("database", f"Check for database issues related to: {issue}"),
            self.run_agent("ops", f"Check for infrastructure issues related to: {issue}"),
        )

        self.memory.write("orchestrator", "initial_findings", initial_findings)

        # Phase 2: Deep dive based on initial findings
        if "query" in str(initial_findings).lower():
            code_analysis = await self.run_agent(
                "code",
                f"Find code that generates problematic queries. Context: {initial_findings[0]}"
            )
            self.memory.write("orchestrator", "code_analysis", code_analysis)

        # Phase 3: Synthesize
        return await self.synthesize(issue)

    async def run_agent(self, agent_type: str, task: str) -> str:
        """Run a specific agent."""
        agent = self.agents[agent_type]
        context = self.memory.get_context()

        prompt = f"""
        {agent.system_prompt}

        Shared context:
        {context}

        Task: {task}
        """

        return await execute_with_tools(prompt, agent.tools)

    async def synthesize(self, original_issue: str) -> str:
        """Synthesize findings from all agents."""
        context = self.memory.get_context()

        synthesis_prompt = f"""
        Synthesize the investigation findings into a coherent report.

        Original issue: {original_issue}

        Gathered information:
        {context}

        Provide:
        1. Root cause analysis
        2. Evidence from each investigation
        3. Recommended actions
        4. Prevention measures
        """

        return await model.generate(synthesis_prompt)
```

[↑ Back to Table of Contents](#table-of-contents)

## Common pitfalls

### Pitfall 1: Infinite delegation

```text
Problem:
Orchestrator → Agent A → "I need help" → Orchestrator → Agent A → ...

Solution:
- Set maximum delegation depth
- Require agents to attempt before escalating
- Track delegation history
```

### Pitfall 2: Context loss

```text
Problem:
Agent A gathers info → passes summary to Agent B → details lost

Solution:
- Shared memory for important findings
- Structured message formats
- Context preservation protocols
```

### Pitfall 3: Conflicting outputs

```text
Problem:
Agent A: "Increase shared_buffers"
Agent B: "Decrease shared_buffers"

Solution:
- Explicit conflict resolution
- Orchestrator arbitration
- Confidence scores
```

### Pitfall 4: Coordination overhead

```text
Problem:
More agents = more coordination = slower execution

Solution:
- Only use multi-agent when needed
- Minimize inter-agent communication
- Parallelize independent work
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Multi-agent systems divide complex tasks among specialist agents
- Architecture patterns: hierarchical, peer-to-peer, pipeline
- Orchestration involves task decomposition and result synthesis
- Communication via message passing or shared memory
- Common pitfalls: infinite delegation, context loss, conflicts, overhead

## Next steps

Continue to **[Chapter 19: Agent Frameworks](./19_agent_frameworks.md)** to learn about CrewAI, LangGraph, and other frameworks.

[↑ Back to Table of Contents](#table-of-contents)
