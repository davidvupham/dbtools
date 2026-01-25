# Chapter 19: Agent frameworks

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-4_Agentic_AI-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Compare major agent frameworks (CrewAI, LangGraph, AutoGen)
2. Choose the right framework for your use case
3. Implement basic agents using CrewAI and LangGraph
4. Integrate frameworks with local LLMs via Ollama

## Table of contents

- [Introduction](#introduction)
- [Framework comparison](#framework-comparison)
- [CrewAI](#crewai)
- [LangGraph](#langgraph)
- [AutoGen](#autogen)
- [Framework selection guide](#framework-selection-guide)
- [Local LLM integration](#local-llm-integration)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Building agents from scratch is educational but time-consuming. Frameworks provide abstractions for common patterns, letting you focus on your specific use case. This chapter covers the leading frameworks and when to use each.

[↑ Back to Table of Contents](#table-of-contents)

## Framework comparison

| Framework | Style | Best For | Complexity |
|:----------|:------|:---------|:-----------|
| **CrewAI** | Role-based crews | Multi-agent collaboration | Low-Medium |
| **LangGraph** | Graph-based flows | Complex, stateful workflows | Medium-High |
| **AutoGen** | Conversational | Multi-turn agent conversations | Medium |
| **LangChain** | Chains & tools | General-purpose, broad ecosystem | Medium |

```text
FRAMEWORK POSITIONING
═════════════════════

                    Simplicity
                        ▲
                   High │  CrewAI
                        │       ●
                        │
                        │           AutoGen
                        │              ●
                        │
                        │                   LangChain
                        │                      ●
                   Low  │                           LangGraph
                        │                              ●
                        └─────────────────────────────────────►
                            Low                        High
                                     Flexibility
```

[↑ Back to Table of Contents](#table-of-contents)

## CrewAI

CrewAI uses a metaphor of "crews" with agents playing specific roles.

### Core concepts

| Concept | Description |
|:--------|:------------|
| **Agent** | A persona with role, goal, and backstory |
| **Task** | A specific job for an agent |
| **Crew** | A team of agents working together |
| **Tool** | Functions agents can use |

### Basic example

```python
from crewai import Agent, Task, Crew
from crewai_tools import tool


# Define a tool
@tool("query_database")
def query_database(query: str) -> str:
    """Execute a SQL query and return results."""
    # Implementation here
    return "Query results..."


# Define agents
dba_agent = Agent(
    role="Database Administrator",
    goal="Analyze database performance and suggest optimizations",
    backstory="""You are an experienced PostgreSQL DBA with 15 years of
    experience optimizing high-traffic databases.""",
    tools=[query_database],
    verbose=True
)

analyst_agent = Agent(
    role="Performance Analyst",
    goal="Identify performance bottlenecks and prioritize fixes",
    backstory="""You specialize in translating technical findings into
    actionable recommendations for development teams.""",
    verbose=True
)


# Define tasks
analyze_task = Task(
    description="Analyze the current database performance metrics and identify issues",
    expected_output="List of performance issues with severity ratings",
    agent=dba_agent
)

report_task = Task(
    description="Create a prioritized report of findings with recommendations",
    expected_output="Executive summary with prioritized action items",
    agent=analyst_agent
)


# Create and run crew
crew = Crew(
    agents=[dba_agent, analyst_agent],
    tasks=[analyze_task, report_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

### CrewAI with Ollama

```python
from crewai import Agent, LLM

# Configure Ollama LLM
ollama_llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434"
)

# Use in agent
agent = Agent(
    role="Database Expert",
    goal="Analyze database issues",
    backstory="You are a database expert.",
    llm=ollama_llm
)
```

[↑ Back to Table of Contents](#table-of-contents)

## LangGraph

LangGraph models agents as state machines with explicit control flow.

### Core concepts

| Concept | Description |
|:--------|:------------|
| **State** | Data passed between nodes |
| **Node** | A function that processes state |
| **Edge** | Connection between nodes |
| **Graph** | The complete workflow |

### Basic example

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator


# Define state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    findings: str
    final_report: str


# Define nodes
async def analyze_database(state: AgentState) -> AgentState:
    """Analyze database and add findings."""
    # Your analysis logic here
    findings = "Found 3 slow queries, connection pool at 95%"
    return {"findings": findings, "messages": [f"Analysis: {findings}"]}


async def generate_report(state: AgentState) -> AgentState:
    """Generate report from findings."""
    findings = state["findings"]
    report = f"## Performance Report\n\n{findings}\n\n### Recommendations\n- Optimize slow queries"
    return {"final_report": report, "messages": [f"Report: {report}"]}


async def should_continue(state: AgentState) -> str:
    """Decide next step."""
    if state.get("findings"):
        return "generate_report"
    return END


# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze", analyze_database)
workflow.add_node("generate_report", generate_report)

# Add edges
workflow.set_entry_point("analyze")
workflow.add_conditional_edges("analyze", should_continue)
workflow.add_edge("generate_report", END)

# Compile
app = workflow.compile()

# Run
result = await app.ainvoke({
    "task": "Analyze database performance",
    "messages": []
})
```

### LangGraph with Ollama

```python
from langchain_ollama import ChatOllama

# Create Ollama-backed LLM
llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434"
)


async def llm_node(state: AgentState) -> AgentState:
    """Node that uses LLM."""
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}
```

### When LangGraph shines

- Complex conditional flows
- Long-running workflows with checkpoints
- Human-in-the-loop requirements
- Debugging and visualization needs

[↑ Back to Table of Contents](#table-of-contents)

## AutoGen

AutoGen focuses on multi-agent conversations.

### Core concepts

| Concept | Description |
|:--------|:------------|
| **ConversableAgent** | Agent that can converse |
| **AssistantAgent** | AI-powered agent |
| **UserProxyAgent** | Represents human user |
| **GroupChat** | Multi-agent conversation |

### Basic example

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Define agents
dba_agent = AssistantAgent(
    name="DBA",
    system_message="""You are a database administrator.
    Analyze performance issues and suggest fixes.""",
    llm_config={"model": "gpt-4"}  # or configure for Ollama
)

developer_agent = AssistantAgent(
    name="Developer",
    system_message="""You are a software developer.
    Implement fixes suggested by the DBA.""",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",  # Auto-respond
    max_consecutive_auto_reply=10
)

# Create group chat
group_chat = GroupChat(
    agents=[user_proxy, dba_agent, developer_agent],
    messages=[],
    max_round=10
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"model": "gpt-4"}
)

# Start conversation
user_proxy.initiate_chat(
    manager,
    message="Our database queries are slow. Can you investigate and fix?"
)
```

[↑ Back to Table of Contents](#table-of-contents)

## Framework selection guide

### Decision tree

```text
Which framework should I use?
│
├── Need multi-agent role-playing with minimal code?
│   └── CrewAI
│
├── Need complex conditional workflows with state?
│   └── LangGraph
│
├── Need conversational multi-agent interactions?
│   └── AutoGen
│
├── Need maximum flexibility and ecosystem?
│   └── LangChain + build custom
│
└── Learning or simple use case?
    └── Start with CrewAI, graduate to LangGraph
```

### Feature comparison

| Feature | CrewAI | LangGraph | AutoGen |
|:--------|:-------|:----------|:--------|
| Learning curve | Low | Medium-High | Medium |
| Multi-agent | ✅ Built-in | ✅ Manual | ✅ Built-in |
| State management | Basic | Advanced | Conversation |
| Checkpointing | Limited | ✅ Full | Limited |
| Visualization | Limited | ✅ Full | Limited |
| Ollama support | ✅ Yes | ✅ Yes | Requires config |
| MCP integration | Via tools | Via tools | Via tools |

[↑ Back to Table of Contents](#table-of-contents)

## Local LLM integration

### Ollama configuration patterns

```python
# CrewAI
from crewai import LLM
llm = LLM(model="ollama/qwen2.5:7b", base_url="http://localhost:11434")

# LangGraph (via LangChain)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

# AutoGen
llm_config = {
    "config_list": [{
        "model": "qwen2.5:7b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama"  # Placeholder
    }]
}
```

### Model recommendations for agents

| Task | Recommended Model | Notes |
|:-----|:------------------|:------|
| Simple agents | Llama 3.1 8B | Good balance |
| Tool calling | Qwen 2.5 7B | Best tool support |
| Code tasks | Qwen 2.5 Coder 7B | Code-optimized |
| Complex reasoning | Llama 3.1 70B | Higher quality |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- CrewAI: Role-based crews for quick multi-agent setup
- LangGraph: Graph-based workflows for complex state management
- AutoGen: Conversational multi-agent interactions
- All frameworks can integrate with Ollama for local LLMs
- Choose based on complexity needs and learning curve tolerance

## Next steps

Continue to **[Chapter 20: Agent Governance](./20_agent_governance.md)** to learn about safety, observability, and human-in-the-loop patterns.

[↑ Back to Table of Contents](#table-of-contents)
