# Module 3 Quiz: Model Context Protocol

**[← Back to Course Index](../README.md)**

Test your understanding of MCP. Choose the best answer for each question.

---

## Questions

### 1. What are the three main primitives in MCP?

- A) Read, Write, Execute
- B) Tools, Resources, Prompts
- C) Input, Output, Error
- D) Request, Response, Stream

<details>
<summary>Show Answer</summary>

**B) Tools, Resources, Prompts**

MCP defines three primitives: Tools (functions the model can call), Resources (data the model can read), and Prompts (reusable prompt templates).
</details>

---

### 2. When should you use a Resource instead of a Tool?

- A) When you need to modify data
- B) When providing static or read-only data for context
- C) When the operation might fail
- D) When you need streaming

<details>
<summary>Show Answer</summary>

**B) When providing static or read-only data for context**

Resources are for data that provides context (files, configs, logs). Tools are for actions that do something or compute results.
</details>

---

### 3. What transport protocols does MCP support?

- A) HTTP only
- B) Stdio and SSE (Server-Sent Events)
- C) WebSocket only
- D) gRPC only

<details>
<summary>Show Answer</summary>

**B) Stdio and SSE (Server-Sent Events)**

MCP supports stdio (for local processes) and SSE (for HTTP-based remote connections).
</details>

---

### 4. What is the purpose of input validation in MCP servers?

- A) To improve performance
- B) To prevent prompt injection and ensure safe execution
- C) To reduce token usage
- D) To format output

<details>
<summary>Show Answer</summary>

**B) To prevent prompt injection and ensure safe execution**

Input validation is critical security practice—never trust inputs from the AI model as they could be influenced by malicious prompts.
</details>

---

### 5. Which is the correct way to define an MCP tool schema?

- A) XML schema
- B) JSON Schema
- C) YAML
- D) Plain text description

<details>
<summary>Show Answer</summary>

**B) JSON Schema**

MCP tools use JSON Schema to define their input parameters, providing type information and validation.
</details>

---

### 6. What is the recommended pattern for handling database queries in MCP?

- A) Allow any SQL query
- B) Allow only SELECT queries with input sanitization
- C) Require admin credentials for all queries
- D) Cache all results indefinitely

<details>
<summary>Show Answer</summary>

**B) Allow only SELECT queries with input sanitization**

For safety, MCP tools should typically only allow read operations (SELECT) and validate/sanitize all inputs to prevent SQL injection.
</details>

---

### 7. What is the purpose of the `@server.list_tools()` decorator?

- A) Execute a tool
- B) Define a handler that returns available tools
- C) Delete a tool
- D) Update a tool

<details>
<summary>Show Answer</summary>

**B) Define a handler that returns available tools**

The `list_tools` decorator defines a handler that returns the list of tools the server provides, along with their schemas.
</details>

---

### 8. How should MCP servers handle errors?

- A) Crash immediately
- B) Return structured error responses that the model can understand
- C) Ignore errors silently
- D) Retry infinitely

<details>
<summary>Show Answer</summary>

**B) Return structured error responses that the model can understand**

MCP servers should return clear, structured error messages so the model can understand what went wrong and potentially try alternatives.
</details>

---

### 9. What is the benefit of MCP over custom API integrations?

- A) Faster execution
- B) Standardized protocol that works across different AI clients
- C) Lower cost
- D) Better security by default

<details>
<summary>Show Answer</summary>

**B) Standardized protocol that works across different AI clients**

MCP provides a standard way to extend AI capabilities that works with any MCP-compatible client (Claude Desktop, Cline, etc.) without custom integration.
</details>

---

### 10. When should audit logging be implemented in MCP servers?

- A) Only for production
- B) For all tool calls in any environment
- C) Only for failed requests
- D) Never, it's optional

<details>
<summary>Show Answer</summary>

**B) For all tool calls in any environment**

Audit logging should be implemented for all tool calls to maintain security visibility and enable debugging, regardless of environment.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You understand MCP well.
- **7-8 correct**: Good foundation. Review security patterns.
- **5-6 correct**: Fair. Re-read the MCP patterns chapter.
- **Below 5**: Review Module 3 before proceeding.

---

**[Continue to Module 4 →](../module_4_agentic_ai/16_agent_fundamentals.md)**
