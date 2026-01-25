# Project 4: Database Operations Agent

**[← Back to Course Index](../README.md)**

> **Difficulty:** Advanced
> **Estimated Time:** 6-8 hours
> **Prerequisites:** Modules 1-4 completed, MCP server from Project 3

## Overview

Build an AI agent that can investigate and diagnose database performance issues autonomously. The agent uses the ReAct pattern to gather information, analyze findings, and provide actionable recommendations.

## Learning objectives

By completing this project, you will:

1. Implement the ReAct agent pattern from scratch
2. Integrate with MCP tools for database operations
3. Add safety guardrails and human-in-the-loop approval
4. Build observability into agent execution

## Requirements

### Agent capabilities

The agent should be able to:

1. **Investigate slow queries**: Find and analyze slow-running queries
2. **Diagnose connection issues**: Check connection pools and limits
3. **Analyze resource usage**: Review CPU, memory, and I/O metrics
4. **Suggest optimizations**: Recommend indexes, configuration changes
5. **Generate reports**: Summarize findings with prioritized actions

### Safety requirements

- Read-only operations by default
- Human approval required for any configuration suggestions
- Maximum 20 iterations per investigation
- All actions logged to audit trail

## Architecture

```text
AGENT ARCHITECTURE
══════════════════

┌─────────────────────────────────────────────────────────────────┐
│                     Database Agent                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   ReAct     │───►│   Tools     │───►│  Guardrails │        │
│  │   Loop      │    │  Executor   │    │  Checker    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                  │                  │                │
│         ▼                  ▼                  ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Memory    │    │   MCP       │    │   Audit     │        │
│  │   Store     │    │   Client    │    │   Logger    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation guide

### Step 1: ReAct loop implementation

```python
# src/agent/react.py
from dataclasses import dataclass, field
from enum import Enum


class AgentState(Enum):
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETE = "complete"


@dataclass
class AgentStep:
    thought: str
    action: str | None = None
    action_input: dict | None = None
    observation: str | None = None


@dataclass
class AgentMemory:
    task: str
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str | None = None

    def to_prompt_context(self) -> str:
        """Format memory for inclusion in prompt."""
        lines = [f"Task: {self.task}\n"]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"Step {i}:")
            lines.append(f"Thought: {step.thought}")
            if step.action:
                lines.append(f"Action: {step.action}({step.action_input})")
            if step.observation:
                lines.append(f"Observation: {step.observation}")
            lines.append("")
        return "\n".join(lines)


class ReActAgent:
    """ReAct agent for database investigation."""

    SYSTEM_PROMPT = """You are a database operations agent. Investigate issues using available tools.

For each step, output:
Thought: [Your reasoning]
Action: [tool_name]
Action Input: [JSON arguments]

When you have enough information:
Thought: I have gathered enough information to answer.
Final Answer: [Your complete answer with recommendations]

Available tools:
{tools}
"""

    def __init__(self, llm, tools: list, max_iterations: int = 20):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations

    async def run(self, task: str) -> str:
        """Execute agent loop."""
        memory = AgentMemory(task=task)

        for i in range(self.max_iterations):
            # Get next action from LLM
            response = await self._think(memory)

            # Parse response
            step = self._parse_response(response)
            memory.steps.append(step)

            # Check for final answer
            if memory.final_answer:
                return memory.final_answer

            # Execute action
            if step.action:
                observation = await self._act(step.action, step.action_input)
                step.observation = observation

        return "Max iterations reached. Partial findings: " + memory.to_prompt_context()

    async def _think(self, memory: AgentMemory) -> str:
        """Get next thought/action from LLM."""
        prompt = self.SYSTEM_PROMPT.format(tools=self._format_tools())
        prompt += "\n" + memory.to_prompt_context()
        return await self.llm.generate(prompt)

    async def _act(self, action: str, action_input: dict) -> str:
        """Execute tool and return observation."""
        if action not in self.tools:
            return f"Unknown tool: {action}"

        tool = self.tools[action]
        return await tool.execute(action_input)
```

### Step 2: Guardrails

```python
# src/agent/guardrails.py
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    requires_approval: bool = False


class AgentGuardrails:
    """Safety guardrails for agent actions."""

    HIGH_RISK_ACTIONS = ["modify_config", "create_index", "drop_index"]

    def __init__(self):
        self.action_counts = {}

    def check(self, action: str, arguments: dict) -> GuardrailResult:
        """Check if action is allowed."""
        # Rate limiting
        self.action_counts[action] = self.action_counts.get(action, 0) + 1
        if self.action_counts[action] > 10:
            return GuardrailResult(
                allowed=False,
                reason=f"Rate limit exceeded for {action}"
            )

        # High-risk actions require approval
        if action in self.HIGH_RISK_ACTIONS:
            return GuardrailResult(
                allowed=False,
                reason=f"Action {action} requires human approval",
                requires_approval=True
            )

        return GuardrailResult(allowed=True, reason="Passed")
```

### Step 3: Investigation workflow

```python
# src/agent/investigator.py

class DatabaseInvestigator:
    """High-level investigation coordinator."""

    def __init__(self, agent: ReActAgent):
        self.agent = agent

    async def investigate_slow_queries(self) -> str:
        """Investigate slow query issues."""
        return await self.agent.run(
            """Investigate slow queries in the database:
            1. Find currently running slow queries
            2. Get execution plans for the slowest
            3. Check for missing indexes
            4. Analyze table statistics
            5. Provide optimization recommendations"""
        )

    async def investigate_connections(self) -> str:
        """Investigate connection issues."""
        return await self.agent.run(
            """Investigate connection pool issues:
            1. Check current connection count vs maximum
            2. Identify long-running connections
            3. Check for connection leaks
            4. Recommend pool configuration changes"""
        )

    async def health_check(self) -> str:
        """Comprehensive health check."""
        return await self.agent.run(
            """Perform a comprehensive database health check:
            1. Check key performance metrics
            2. Identify any slow queries
            3. Review connection status
            4. Check replication status (if applicable)
            5. Summarize overall health with any concerns"""
        )
```

## Implementation tasks

### Part 1: Core agent (35%)

- [ ] Implement `ReActAgent` class
- [ ] Response parsing (thought, action, observation)
- [ ] Memory management
- [ ] Iteration limiting

### Part 2: Tool integration (25%)

- [ ] Connect to MCP server from Project 3
- [ ] Wrap MCP tools for agent use
- [ ] Handle tool errors gracefully

### Part 3: Safety (25%)

- [ ] Implement guardrails checker
- [ ] Add human approval workflow
- [ ] Audit logging for all actions
- [ ] Rate limiting per action type

### Part 4: Testing (15%)

- [ ] Unit tests for ReAct parsing
- [ ] Mock tool execution tests
- [ ] Integration test with sample investigation

## Expected usage

```python
from agent import DatabaseInvestigator, ReActAgent
from mcp_client import MCPClient

# Initialize
mcp = MCPClient("stdio", command=["python", "-m", "db_mcp_server"])
tools = await mcp.list_tools()

agent = ReActAgent(llm=ollama_client, tools=tools)
investigator = DatabaseInvestigator(agent)

# Run investigation
result = await investigator.investigate_slow_queries()
print(result)
```

## Sample output

```text
Investigation: Slow Query Analysis
══════════════════════════════════

Step 1:
Thought: I need to find currently slow queries to understand the issue.
Action: get_slow_queries()
Observation: Found 3 queries running > 30 seconds

Step 2:
Thought: Let me get the execution plan for the slowest query.
Action: explain_query(query="SELECT * FROM orders WHERE...")
Observation: Seq Scan on orders, estimated 1.2M rows

Step 3:
Thought: A sequential scan on 1.2M rows indicates missing index.
Action: get_table_schema(table="orders")
Observation: Columns: id, customer_id, created_at, status...

Final Answer:
## Findings

1. **Slow Query Identified**: Query on `orders` table doing full table scan
2. **Root Cause**: Missing index on `customer_id` column
3. **Impact**: 1.2M rows scanned for each query

## Recommendations

1. Create index: `CREATE INDEX idx_orders_customer_id ON orders(customer_id)`
2. Consider partitioning orders table by date
3. Review application query patterns
```

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| ReAct loop correctly implemented | 30 |
| Tool integration working | 20 |
| Guardrails and safety | 20 |
| Quality of investigations | 15 |
| Testing and documentation | 15 |
| **Total** | **100** |

---

**[Next Module →](../module_5_rag/21_rag_fundamentals.md)**
