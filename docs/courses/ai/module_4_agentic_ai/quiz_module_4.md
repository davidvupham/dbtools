# Module 4 Quiz: Agentic AI

**[← Back to Course Index](../README.md)**

Test your understanding of agentic AI patterns. Choose the best answer for each question.

---

## Questions

### 1. What distinguishes an AI agent from a simple LLM call?

- A) Agents use larger models
- B) Agents can take autonomous actions in a loop based on observations
- C) Agents are always faster
- D) Agents don't need prompts

<details>
<summary>Show Answer</summary>

**B) Agents can take autonomous actions in a loop based on observations**

Agents iterate through perception-reasoning-action cycles, using tools and adapting based on results, rather than just generating text.
</details>

---

### 2. In the ReAct pattern, what does the cycle consist of?

- A) Read → Execute → Analyze → Complete → Terminate
- B) Thought → Action → Observation → (repeat)
- C) Request → Evaluate → Approve → Continue → Transfer
- D) Retrieve → Extract → Apply → Check → Test

<details>
<summary>Show Answer</summary>

**B) Thought → Action → Observation → (repeat)**

ReAct interleaves Reasoning (Thought) with Acting (tool use), then observing results before deciding the next step.
</details>

---

### 3. When is the plan-and-execute pattern most appropriate?

- A) Highly dynamic situations with unknown steps
- B) Tasks with clear sequential steps defined upfront
- C) Simple single-step tasks
- D) Real-time chat applications

<details>
<summary>Show Answer</summary>

**B) Tasks with clear sequential steps defined upfront**

Plan-and-execute works best when you can decompose a task into a sequence of steps before execution, providing predictability.
</details>

---

### 4. What is the purpose of the reflection pattern?

- A) To mirror user input
- B) To have the agent critique and improve its own outputs
- C) To reflect light in a UI
- D) To duplicate agent instances

<details>
<summary>Show Answer</summary>

**B) To have the agent critique and improve its own outputs**

Reflection has the agent evaluate its work, identify issues, and iterate to improve quality before finalizing output.
</details>

---

### 5. In a multi-agent system, what is the orchestrator's role?

- A) Execute all tasks directly
- B) Decompose tasks and delegate to specialist agents
- C) Store data for agents
- D) Handle user authentication

<details>
<summary>Show Answer</summary>

**B) Decompose tasks and delegate to specialist agents**

The orchestrator breaks down complex tasks, assigns subtasks to appropriate specialist agents, and synthesizes results.
</details>

---

### 6. Which framework is known for role-based "crews" of agents?

- A) LangGraph
- B) AutoGen
- C) CrewAI
- D) LangChain

<details>
<summary>Show Answer</summary>

**C) CrewAI**

CrewAI uses a metaphor of "crews" where agents have specific roles (like DBA, Analyst) working together on tasks.
</details>

---

### 7. What is a common pitfall in multi-agent systems?

- A) Too few agents
- B) Infinite delegation loops
- C) Agents working too fast
- D) Too much context

<details>
<summary>Show Answer</summary>

**B) Infinite delegation loops**

Without proper controls, agents can endlessly delegate tasks back and forth, never completing work.
</details>

---

### 8. What should require human approval in agent governance?

- A) All read-only operations
- B) Irreversible actions like delete or drop
- C) Every single action
- D) Only actions that fail

<details>
<summary>Show Answer</summary>

**B) Irreversible actions like delete or drop**

Human-in-the-loop is essential for high-risk, irreversible actions to prevent data loss or security incidents.
</details>

---

### 9. What is a "kill switch" in agent governance?

- A) A button to restart agents
- B) An emergency mechanism to stop all agent operations
- C) A way to delete agents
- D) A performance optimization

<details>
<summary>Show Answer</summary>

**B) An emergency mechanism to stop all agent operations**

A kill switch allows operators to immediately halt all agent activity in case of runaway behavior or incidents.
</details>

---

### 10. What is the benefit of using shared memory in multi-agent systems?

- A) Reduces the number of agents needed
- B) Allows agents to share context and findings
- C) Makes agents faster
- D) Eliminates the need for tools

<details>
<summary>Show Answer</summary>

**B) Allows agents to share context and findings**

Shared memory enables agents to access each other's findings, preventing context loss and enabling collaboration.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You're ready to build agent systems.
- **7-8 correct**: Good understanding. Review governance patterns.
- **5-6 correct**: Fair. Re-read the agent patterns chapters.
- **Below 5**: Review Module 4 before proceeding.

---

**[Continue to Module 5 →](../module_5_rag/21_rag_fundamentals.md)**
