# Chapter 17: Agent patterns

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-4_Agentic_AI-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Implement the ReAct pattern for reasoning and acting
2. Apply plan-and-execute for complex multi-step tasks
3. Use reflection for self-improvement
4. Choose the right pattern for different scenarios

## Table of contents

- [Introduction](#introduction)
- [ReAct pattern](#react-pattern)
- [Plan-and-execute pattern](#plan-and-execute-pattern)
- [Reflection pattern](#reflection-pattern)
- [Tool-use patterns](#tool-use-patterns)
- [Choosing patterns](#choosing-patterns)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Agent patterns are proven approaches to structuring how agents think and act. Each pattern has strengths for different types of tasks. This chapter covers the most important patterns for building effective agents.

[↑ Back to Table of Contents](#table-of-contents)

## ReAct pattern

**ReAct (Reasoning + Acting)** interleaves thinking with tool use, allowing the agent to reason about observations before taking the next action.

### Structure

```text
REACT LOOP
══════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Thought: [Reason about the current state and what to do next]             │
│      │                                                                      │
│      ▼                                                                      │
│   Action: [Call a tool with specific arguments]                             │
│      │                                                                      │
│      ▼                                                                      │
│   Observation: [Result from the tool]                                       │
│      │                                                                      │
│      ▼                                                                      │
│   Thought: [Reason about the observation]                                   │
│      │                                                                      │
│      ├── Need more info? → Action → Observation → ...                       │
│      │                                                                      │
│      └── Ready to answer? → Final Answer                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
REACT_PROMPT = """
You are a database operations agent. Answer the user's question using the available tools.

For each step, use this format:
Thought: [Your reasoning about what to do next]
Action: [tool_name(param1="value1", param2="value2")]
Observation: [Result will appear here]
... (repeat as needed)
Thought: I now have enough information to answer.
Final Answer: [Your complete answer]

Available tools:
- get_metrics(database: str) - Get current database metrics
- query_database(query: str) - Execute a read-only SQL query
- analyze_log(log_path: str) - Analyze database logs

User question: {question}
"""


async def react_loop(question: str, max_iterations: int = 10) -> str:
    """Execute ReAct loop."""
    prompt = REACT_PROMPT.format(question=question)
    conversation = prompt

    for i in range(max_iterations):
        # Get model response
        response = await model.generate(conversation)

        # Check for final answer
        if "Final Answer:" in response:
            return extract_final_answer(response)

        # Parse and execute action
        action = parse_action(response)
        if action:
            result = await execute_tool(action.name, action.args)
            observation = f"\nObservation: {result}\n"
            conversation += response + observation
        else:
            # No action, continue reasoning
            conversation += response

    return "Max iterations reached without conclusion"
```

### Example trace

```text
User: "Why is the production database slow?"

Thought: I need to check the current database metrics to understand the performance issue.
Action: get_metrics(database="production")
Observation: {"connections": 195, "max_connections": 200, "cpu": 85, "cache_hit_ratio": 0.72}

Thought: Connections are near max (195/200) and cache hit ratio is low (72%). Let me check for long-running queries.
Action: query_database(query="SELECT pid, query, state, query_start FROM pg_stat_activity WHERE state != 'idle' ORDER BY query_start LIMIT 5")
Observation: [3 queries running for >10 minutes, all doing full table scans]

Thought: I found long-running queries doing table scans. Let me check the logs for more context.
Action: analyze_log(log_path="/var/log/postgresql/postgresql-15-main.log")
Observation: {"errors": 0, "warnings": 15, "pattern": "sequential scan on large table 'orders'"}

Thought: I now have enough information to answer.
Final Answer: The production database is slow due to:
1. Connection pool near saturation (195/200)
2. Low cache hit ratio (72%, should be >95%)
3. Long-running queries doing full table scans on 'orders' table

Recommendations:
- Add index on 'orders' table for the problematic queries
- Increase shared_buffers to improve cache hit ratio
- Consider connection pooling to manage connections
```

[↑ Back to Table of Contents](#table-of-contents)

## Plan-and-execute pattern

**Plan-and-execute** creates a complete plan upfront, then executes each step. Good for complex, multi-step tasks.

### Structure

```text
PLAN-AND-EXECUTE
════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   PLANNING PHASE                                                            │
│   ──────────────                                                            │
│   Input: User task                                                          │
│      ▼                                                                      │
│   Plan: [Step 1] → [Step 2] → [Step 3] → [Step 4]                           │
│                                                                             │
│   EXECUTION PHASE                                                           │
│   ───────────────                                                           │
│                                                                             │
│   Execute Step 1 → Result 1                                                 │
│        ▼                                                                    │
│   Replan if needed?                                                         │
│        ▼                                                                    │
│   Execute Step 2 → Result 2                                                 │
│        ▼                                                                    │
│   ... continue until complete                                               │
│        ▼                                                                    │
│   Final synthesis of all results                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
PLANNER_PROMPT = """
Create a step-by-step plan to accomplish this task.
Each step should be a single tool call.

Task: {task}

Available tools:
{tools}

Respond with a numbered list of steps:
1. [tool_name]: [what this step accomplishes]
2. [tool_name]: [what this step accomplishes]
...
"""

EXECUTOR_PROMPT = """
Execute step {step_num} of the plan.

Plan: {plan}

Previous results:
{previous_results}

Current step: {current_step}

Execute this step and report the result.
"""


async def plan_and_execute(task: str) -> str:
    """Execute plan-and-execute pattern."""
    # Phase 1: Planning
    plan_prompt = PLANNER_PROMPT.format(task=task, tools=get_tool_descriptions())
    plan = await model.generate(plan_prompt)
    steps = parse_plan(plan)

    # Phase 2: Execution
    results = []
    for i, step in enumerate(steps):
        exec_prompt = EXECUTOR_PROMPT.format(
            step_num=i + 1,
            plan=plan,
            previous_results=format_results(results),
            current_step=step
        )
        result = await execute_step(exec_prompt)
        results.append({"step": step, "result": result})

        # Optional: Check if replanning is needed
        if should_replan(results):
            steps = await replan(task, results)

    # Phase 3: Synthesize
    return synthesize_results(task, results)
```

### When to use plan-and-execute

| Use When | Avoid When |
|:---------|:-----------|
| Tasks have clear sequential steps | Highly dynamic situations |
| Upfront planning is valuable | Simple, single-step tasks |
| Steps are somewhat independent | Heavy interdependencies |
| Want visibility into the plan | Need maximum flexibility |

[↑ Back to Table of Contents](#table-of-contents)

## Reflection pattern

**Reflection** has the agent critique and improve its own output through self-evaluation.

### Structure

```text
REFLECTION PATTERN
══════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Step 1: GENERATE                                                          │
│   ────────────────                                                          │
│   Produce initial output                                                    │
│                                                                             │
│   Step 2: REFLECT                                                           │
│   ───────────────                                                           │
│   Critique the output:                                                      │
│   - What could be improved?                                                 │
│   - What's missing?                                                         │
│   - What's incorrect?                                                       │
│                                                                             │
│   Step 3: REFINE                                                            │
│   ──────────────                                                            │
│   Improve based on reflection                                               │
│                                                                             │
│   Step 4: ITERATE (optional)                                                │
│   ─────────────────────────                                                 │
│   Repeat until quality threshold met                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
REFLECTION_PROMPT = """
Review your previous output and identify:
1. Errors or inaccuracies
2. Missing information
3. Areas that could be clearer
4. Potential improvements

Previous output:
{output}

Provide specific critique points.
"""

REFINEMENT_PROMPT = """
Improve your output based on this critique:

Original output:
{output}

Critique:
{critique}

Provide an improved version that addresses all critique points.
"""


async def generate_with_reflection(task: str, max_iterations: int = 3) -> str:
    """Generate output with reflection loop."""
    # Initial generation
    output = await model.generate(task)

    for i in range(max_iterations):
        # Reflect
        reflection_prompt = REFLECTION_PROMPT.format(output=output)
        critique = await model.generate(reflection_prompt)

        # Check if satisfied
        if "no improvements needed" in critique.lower():
            break

        # Refine
        refinement_prompt = REFINEMENT_PROMPT.format(
            output=output,
            critique=critique
        )
        output = await model.generate(refinement_prompt)

    return output
```

### Reflection use cases

| Use Case | Benefit |
|:---------|:--------|
| Code generation | Catch bugs before execution |
| Documentation | Improve clarity and completeness |
| Analysis | Verify conclusions |
| Recommendations | Challenge assumptions |

[↑ Back to Table of Contents](#table-of-contents)

## Tool-use patterns

### Sequential tool use

Call tools one after another, each building on previous results:

```text
get_connection_count() → 195 connections
    │
    ▼
get_query_stats() → 3 slow queries identified
    │
    ▼
explain_query(slow_query_1) → Full table scan detected
    │
    ▼
suggest_index(table, columns) → CREATE INDEX recommendation
```

### Parallel tool use

Call independent tools simultaneously:

```python
async def parallel_diagnostics(database: str) -> dict:
    """Run multiple diagnostics in parallel."""
    tasks = [
        get_metrics(database),
        get_connection_stats(database),
        get_slow_queries(database),
        get_lock_info(database),
    ]

    results = await asyncio.gather(*tasks)

    return {
        "metrics": results[0],
        "connections": results[1],
        "slow_queries": results[2],
        "locks": results[3]
    }
```

### Conditional tool use

Choose tools based on conditions:

```python
async def diagnose_issue(symptoms: str) -> str:
    """Diagnose based on symptoms."""
    if "connection" in symptoms.lower():
        return await analyze_connections()
    elif "slow" in symptoms.lower():
        return await analyze_performance()
    elif "error" in symptoms.lower():
        return await analyze_logs()
    else:
        # Comprehensive check
        return await full_health_check()
```

[↑ Back to Table of Contents](#table-of-contents)

## Choosing patterns

### Decision matrix

| Pattern | Best For | Complexity | Latency |
|:--------|:---------|:-----------|:--------|
| **ReAct** | Exploratory tasks, unknown steps | Medium | Variable |
| **Plan-Execute** | Known multi-step workflows | Medium | Predictable |
| **Reflection** | Quality-critical outputs | Low | Higher |
| **Sequential** | Dependent operations | Low | Linear |
| **Parallel** | Independent operations | Low | Fastest |

### Pattern selection flowchart

```text
Is the task well-defined with clear steps?
├── YES → Plan-and-Execute
│
└── NO → Is quality more important than speed?
         ├── YES → ReAct + Reflection
         │
         └── NO → ReAct (simple)
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- ReAct interleaves reasoning with tool use for flexible problem-solving
- Plan-and-execute creates upfront plans for predictable multi-step tasks
- Reflection enables self-improvement through critique and refinement
- Tool-use patterns (sequential, parallel, conditional) optimize execution
- Choose patterns based on task predictability and quality requirements

## Next steps

Continue to **[Chapter 18: Multi-Agent Systems](./18_multi_agent_systems.md)** to learn how to coordinate multiple specialized agents.

[↑ Back to Table of Contents](#table-of-contents)
