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

## 3. gRPC vs REST

**The Concept:**

- **REST:** JSON over HTTP/1.1. Human readable.
- **gRPC:** Binary (Protobuf) over HTTP/2. Strictly typed contracts.

### The Tradeoff

- **gRPC Wins:**
  - **Performance:** Smaller payloads, strictly typed, faster parsing.
  - **Internal Traffic:** Great for Service-to-Service chatter where you control both sides.
- **REST Wins:**
  - **Ubiquity:** Every browser, curl, and language speaks JSON/HTTP.
  - **Debugging:** You can read the payload on the wire.

### 🛑 When NOT to use gRPC

- **Public APIs:** Browsers do not support gRPC natively (requires gRPC-Web proxy). Force external users to update their SDKs? Hard sell. Use REST/GraphQL for public facing APIs.

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
