# System Design: Communication & API Patterns

> "Microservices are a organizational scaling pattern, not a technical performance pattern."

How services talk to each other defines your system's complexity.

---

## 1. Microservices vs Monolith

**The decision:** One big app or many small ones?

### The Tradeoff

- **Monolith:**
  - *Good:* Zero network latency (function calls). ACID transactions are easy. Refactoring is easy (IDE does it).
  - *Bad:* Tight coupling. A memory leak in "Image Processing" crashes the "Checkout" page. Hard to scale teams (merge conflicts).
- **Microservices:**
  - *Good:* Independent deployment (Team A releases without blocking Team B). Failure isolation.
  - *Bad:* **Distributed Monolith.** If Service A needs Service B to do *anything*, you just added network latency to every function call and lost ACID transactions.

### 🛑 When NOT to use Microservices

- **Small Teams:** If you have 3 developers, manage a monolith. Microservices tax is high (DevOps, monitoring, versioning).
- **Undefined Domain:** If you don't know where the boundaries are yet, you will slice it wrong. "Refactoring a monolith is an annoyance; refactoring microservices is a migration."

---

## 2. API Gateway

**The Concept:** A single entry point for all clients. It routes requests to appropriate backend services.

### The Tradeoff

- **Problem Solved:**
  - **Cross-Cutting Concerns:** Auth, Rate Limiting, Logging, SSL termination happen in one place.
  - **Abstraction:** The frontend talks to `api.site.com`, not 50 different IP addresses.
- **Problem Created:**
  - **Single Point of Failure:** If the Gateway is misconfigured, no one gets in.
  - **Bottleneck:** All traffic passes through here.

### 🛑 When NOT to use

- **Serverless/PaaS:** Sometimes AWS API Gateway is expensive at scale.
- **Internal Service-to-Service:** Service A should usually call Service B directly (or via Mesh), not loop back out to the public Gateway.

---

## 3. REST vs GraphQL vs gRPC

**The Decision:** How should clients fetch data from your services?

### REST (Representational State Transfer)

- **Format:** JSON over HTTP/1.1
- **Paradigm:** Resource-based endpoints (`/users/123`, `/orders`)
- **Strengths:**
  - Universal: Every browser, curl, and language speaks JSON/HTTP
  - Cacheable: HTTP caching works out of the box (CDNs, browsers)
  - Debuggable: You can read the payload on the wire
  - Mature: Extensive tooling, OpenAPI specs, well-understood patterns

### GraphQL

- **Format:** JSON over HTTP (typically POST to single endpoint)
- **Paradigm:** Query language—client specifies exactly what data it needs
- **Strengths:**
  - **No over-fetching:** Client requests only the fields it needs
  - **No under-fetching:** Get related data in one request (no waterfall)
  - **Typed schema:** Self-documenting, client code generation
  - **Flexibility:** Multiple clients (web, mobile) with different data needs

**Example:**

```graphql
# One request gets user + their orders + order items
query {
  user(id: "123") {
    name
    email
    orders(limit: 5) {
      id
      total
      items { productName, quantity }
    }
  }
}
```

### gRPC (Google Remote Procedure Call)

- **Format:** Binary (Protobuf) over HTTP/2
- **Paradigm:** Strictly typed RPC contracts
- **Strengths:**
  - **Performance:** Smaller payloads, faster parsing than JSON
  - **Streaming:** Bi-directional streaming built-in
  - **Code generation:** Strong typing in multiple languages
  - **Internal traffic:** Great for Service-to-Service communication

### The Tradeoff Matrix

| Factor | REST | GraphQL | gRPC |
|--------|------|---------|------|
| **Learning curve** | Low | Medium | Medium-High |
| **Browser support** | Native | Native | Requires proxy |
| **Caching** | Built-in (HTTP) | Complex | Manual |
| **Debugging** | Easy (readable) | Medium | Hard (binary) |
| **Payload size** | Medium | Optimized | Smallest |
| **Schema evolution** | Versioned URLs | Single evolving schema | Proto versioning |
| **Real-time** | Polling/SSE | Subscriptions | Streaming |

### When to Use Each

**Choose REST when:**
- Building public APIs for external developers
- Simple CRUD operations
- You want HTTP caching (CDN, browser cache)
- Team is new to API development

**Choose GraphQL when:**
- Multiple clients with different data needs (web vs mobile)
- Complex, nested data structures
- Frontend team needs flexibility without backend changes
- Avoiding over-fetching is critical (mobile bandwidth)

**Choose gRPC when:**
- Internal service-to-service communication
- Performance is critical (high-throughput microservices)
- You need streaming (real-time data feeds)
- You control both client and server

### Hybrid Approaches

Most large systems use multiple protocols:

```text
┌─────────────┐     REST/GraphQL     ┌─────────────┐
│   Browser   │ ◄──────────────────► │ API Gateway │
│   Mobile    │                      └──────┬──────┘
└─────────────┘                             │
                                            │ gRPC
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
              ┌─────▼─────┐           ┌─────▼─────┐           ┌─────▼─────┐
              │ Service A │◄─────────►│ Service B │◄─────────►│ Service C │
              └───────────┘   gRPC    └───────────┘   gRPC    └───────────┘
```

**Common pattern:** REST or GraphQL for public APIs, gRPC for internal service mesh.

### 🛑 Common Pitfalls

**REST:**
- Under-fetching: Client calls 5 endpoints for one screen
- Rigid versioning: `/v1/`, `/v2/` proliferation
- N+1 problem: Fetching list then each item's details

**GraphQL:**
- N+1 query problem: Naive resolvers hit DB per item (use DataLoader)
- Complexity attacks: Malicious deeply-nested queries (implement depth limits)
- Caching difficulty: POST requests don't cache (use persisted queries)
- Security: Disable introspection in production

**gRPC:**
- Browser incompatibility: Requires gRPC-Web proxy
- Debugging difficulty: Binary payloads need special tooling
- Schema migration: Breaking proto changes affect all clients

---

## 4. WebSockets

**The Concept:** Full-duplex persistent connection. The server can push data to the client.

### The Tradeoff

- **Problem Solved:** Real-time chat, live sports scores, gaming.
- **Problem Created:**
  - **Statefulness:** The server *must* keep a connection open. A standard web server handles a request and forgets it. A WebSocket server holding 100k connections needs serious RAM and file descriptors.
  - **Load Balancing:** You can't just round-robin requests. If User A is connected to Server 1, sending a message to Server 2 won't reach them (requires a Pub/Sub backplane like Redis).

### 🛑 When NOT to use

- **"It needs to be fast":** HTTP/2 is also fast. Use WebSockets only if you need *Server Push*.
- **Low Frequency Updates:** If data changes once an hour, just poll. Keeping a TCP connection open for occasional updates is wasteful.

---

## 5. Service Mesh (Istio, Linkerd)

**The Concept:** Moving network logic (retries, timeouts, mTLS) out of your code and into a sidecar proxy.

### The Tradeoff

- **Problem Solved:** "Why does the Python service retry 3 times but the Go service retry 5 times?" Standardization of network behavior without touching code.
- **Problem Created:**
  - **Crucial Complexity:** You are doubling the number of containers (Sidecars). Debugging "Is it my code or the Envoy proxy config?" is painful.
  - **Latency:** Adds a small hop to every call.

### 🛑 When NOT to use

- **Startups / Simple Architectures:** You don't need mTLS and sophisticated traffic shifting for 5 services. It is a massive operational burden.
