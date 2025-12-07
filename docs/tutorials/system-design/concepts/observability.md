# System Design: Observability Patterns

> "Observability is not about big data charts. It's about asking questions about your system that you didn't know you needed to ask."

In a distributed system, "Logging" is no longer enough because a single request hops through 5 different servers.

---

## 1. Distributed Tracing (OpenTelemetry, Jaeger, Zipkin)

**The Concept:** Assigning a unique `Trace ID` to an incoming request and ensuring every service passes this ID along to the next service.

**The Flow:**

1. Frontend calls API: `x-trace-id: 123`
2. API calls Auth Service: `x-trace-id: 123`
3. API calls Database: `/* trace-id: 123 */ SELECT ...`

### The Tradeoff

- **Problem Solved:** **"Where is the latency?"** You can see a waterfall graph:
  - Auth: 5ms
  - Business Logic: 10ms
  - **Database: 900ms (Here is the problem)**
- **Problem Created:**
  - **Instrumentation Tax:** Every single library, HTTP client, and database driver must support it. If *one* middle service drops the header, the trace breaks.
  - **Data Volume:** Storing 100% of traces is expensive. You often need "Sampling" (only store 1% of success requests, 100% of error requests).

### 🛑 When NOT to use

- **Monoliths:** If everything is in one log file on one server, `grep` is infinite times faster and cheaper than setting up a Jaeger cluster.
- **Batched Jobs:** Tracing assumes a "Request/Response" flow. It doesn't model "Process 1M records in a loop" very well.

---

## 2. Metrics vs Logs vs Traces (The Three Pillars)

- **metrics:** "Is it slow?" (Aggregates, Counts). Cheap.
- **logs:** "What went wrong?" (Detailed text). Expensive.
- **traces:** "Where did it go wrong?" (Context & Causality). Complex.

### The Decision

- Start with **Metrics**. (CPU, Memory, Request Count).
- Then **Logs**. (Stack traces).
- Add **Tracing** only when you split into microservices and lose the ability to follow a request.
