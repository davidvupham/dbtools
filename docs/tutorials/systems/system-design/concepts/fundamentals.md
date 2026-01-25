# System Design: Foundational Concepts

**[← Back to System Design Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

> "If you can't explain scalability, latency, and throughput clearly, you're not ready for a system design interview."

This guide covers the foundational vocabulary of system design. Master these concepts before diving into specific patterns.

---

## Table of Contents

- [1. Scalability](#1-scalability)
- [2. Latency](#2-latency)
- [3. Throughput vs Bandwidth](#3-throughput-vs-bandwidth)
- [4. Concurrency vs Parallelism](#4-concurrency-vs-parallelism)
- [5. How These Concepts Interact](#5-how-these-concepts-interact)

---

## 1. Scalability

**Definition:** A system's ability to handle increased load while maintaining acceptable performance.

### Horizontal Scaling (Scale Out)

Adding more machines to distribute the workload.

```text
Before: [Server 1] handles 1000 RPS
After:  [Server 1] + [Server 2] + [Server 3] each handle 333 RPS
```

**Characteristics:**

- Theoretically unlimited scaling
- Requires load balancer to distribute traffic
- Adds complexity (distributed state, network calls)
- Better fault tolerance (one server dies, others continue)

**Good for:** Stateless web servers, microservices, read replicas

### Vertical Scaling (Scale Up)

Upgrading a single machine's resources (CPU, RAM, storage).

```text
Before: 4 CPU cores, 16GB RAM
After:  64 CPU cores, 512GB RAM
```

**Characteristics:**

- Simpler (no distributed systems complexity)
- Hard limit (you can't buy a 10,000 core server)
- Single point of failure
- Often requires downtime to upgrade

**Good for:** Databases (before sharding), monoliths, legacy systems

### The Decision Framework

| Factor | Horizontal Scaling | Vertical Scaling |
|--------|-------------------|------------------|
| **Complexity** | High (distributed systems) | Low (single machine) |
| **Cost curve** | Linear (add machines) | Exponential (premium hardware) |
| **Fault tolerance** | High (redundancy built-in) | Low (single point of failure) |
| **Upper limit** | Theoretically unlimited | Hardware ceiling |
| **Downtime** | Zero (rolling deploys) | Often required |

### 🛑 When NOT to scale

- **Premature optimization:** Don't add 10 servers for 100 users. Profile first.
- **Wrong bottleneck:** If your DB is the bottleneck, adding app servers does nothing.
- **Stateful apps:** If your app stores session in memory, horizontal scaling breaks without redesign.

[↑ Back to Table of Contents](#table-of-contents)

---

## 2. Latency

**Definition:** The time elapsed between sending a request and receiving a response.

```text
User clicks "Submit" → [50ms] → Server processes → [50ms] → User sees result
Total latency: 100ms
```

### Why Averages Lie

**The problem:** If 99 requests take 50ms and 1 request takes 5000ms, the average is ~100ms. But that average doesn't represent what most users experience OR the worst case.

**The solution:** Use percentiles.

### Percentile Metrics

| Metric | Meaning | Use Case |
|--------|---------|----------|
| **P50 (Median)** | 50% of requests are faster | "Typical" user experience |
| **P95** | 95% of requests are faster | Performance tuning target |
| **P99** | 99% of requests are faster | Tail latency / worst-case SLA |

**Example interpretation:**

```text
P50:  45ms   → Half your users see this or better
P95: 120ms   → 5% of users wait longer than this
P99: 850ms   → 1% of users have a bad experience
```

### Why P99 Matters

- High-value users often trigger complex queries (admins, power users)
- The 1% can represent thousands of requests at scale
- Tail latency compounds: if a request touches 10 services each with P99=100ms, your request P99 could be much worse

### Common Latency Sources

| Source | Typical Impact | Mitigation |
|--------|---------------|------------|
| **Network round-trip** | 1-100ms per hop | CDN, edge computing |
| **Database query** | 1-1000ms | Indexes, caching, read replicas |
| **Disk I/O** | 0.1-10ms (SSD) | In-memory caching |
| **Garbage collection** | 10-1000ms spikes | Tune GC, use GC-friendly languages |
| **Cold start** | 100ms-10s | Keep-warm strategies, provisioned concurrency |

### Techniques to Reduce Latency

1. **Caching:** Store computed results in memory (Redis, Memcached)
2. **CDN:** Serve static content from geographically closer servers
3. **Database optimization:** Proper indexes, connection pooling, read replicas
4. **Async processing:** Move non-critical work to background queues
5. **Compression:** Reduce payload size over the network

### Setting SLOs

A reasonable tiered approach:

```text
P50:  50ms   (typical experience)
P95: 200ms   (acceptable degradation)
P99: 500ms   (alerting threshold)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## 3. Throughput vs Bandwidth

These terms are often confused but represent different things.

### Definitions

| Term | Definition | Analogy |
|------|------------|---------|
| **Bandwidth** | Maximum theoretical data transfer capacity | How wide the highway is |
| **Throughput** | Actual data transferred per unit time | How many cars are currently on the highway |

### The Highway Analogy

```text
Bandwidth: 6-lane highway (can handle 6000 cars/hour max)
Throughput: Currently 2000 cars/hour are using it

Bandwidth ≥ Throughput (always)
```

### Why They Differ

Throughput is always less than or equal to bandwidth due to:

- **Network congestion:** Too many requests competing
- **Protocol overhead:** TCP headers, encryption, etc.
- **Processing limits:** Server can't process requests fast enough
- **Latency:** High latency means fewer complete requests per second

### Measuring Throughput

Common units:

- **RPS (Requests Per Second):** API throughput
- **QPS (Queries Per Second):** Database throughput
- **TPS (Transactions Per Second):** Payment/financial systems
- **Mbps/Gbps:** Network throughput

### Improving Throughput

| Strategy | How It Helps |
|----------|--------------|
| **Load balancing** | Distribute work across servers |
| **Caching** | Reduce repeated computation |
| **Connection pooling** | Reuse expensive connections |
| **Batching** | Process multiple items per request |
| **Async processing** | Don't block on slow operations |
| **Compression** | Fit more data in same bandwidth |

### 🛑 Common Mistakes

- **Confusing the two:** "We have 10 Gbps bandwidth, why is throughput only 100 Mbps?" (Likely a processing bottleneck)
- **Over-provisioning bandwidth:** If your server can only process 1000 RPS, 100 Gbps bandwidth is wasted
- **Ignoring latency:** High bandwidth + high latency = low throughput

[↑ Back to Table of Contents](#table-of-contents)

---

## 4. Concurrency vs Parallelism

As Rob Pike (co-creator of Go) said: "Concurrency is about *dealing* with lots of things at once. Parallelism is about *doing* lots of things at once."

### Definitions

| Term | Definition | Requires |
|------|------------|----------|
| **Concurrency** | Managing multiple tasks that can make progress independently | Good program structure |
| **Parallelism** | Executing multiple tasks at the exact same instant | Multiple CPU cores |

### The Kitchen Analogy

**Concurrency (One Chef):**

```text
1. Start boiling water for pasta
2. While waiting, chop vegetables
3. Check pasta, it's not ready
4. Start sautéing vegetables
5. Drain pasta (now ready)
6. Combine and serve
```

One chef handles multiple tasks by switching between them. Tasks overlap in time but aren't simultaneous.

**Parallelism (Two Chefs):**

```text
Chef A: Boil pasta, drain, plate
Chef B: Chop vegetables, sauté, add to plate
```

Two chefs literally work at the same time on different tasks.

### Technical Example

**Concurrency (Single Core, Multiple Threads):**

```text
Time →
Thread A: [====]      [====]      [====]
Thread B:       [====]      [====]
              ↑ Context switch
```

The CPU rapidly switches between threads, creating the *illusion* of simultaneity.

**Parallelism (Multi-Core):**

```text
Time →
Core 1: [====][====][====][====]
Core 2: [====][====][====][====]
```

Both cores execute instructions at the exact same time.

### Key Insight

**Parallelism is a subset of concurrency.** You can have concurrency without parallelism (single-core CPU running threads), but you cannot have parallelism without concurrency (you need multiple independent tasks to parallelize).

### When to Use Each

| Scenario | Best Approach | Why |
|----------|--------------|-----|
| **I/O-bound tasks** (API calls, file reads) | Concurrency (async/await) | CPU sits idle waiting; let it handle other tasks |
| **CPU-bound tasks** (image processing, ML) | Parallelism (multi-process) | Needs actual computational power |
| **Web servers** | Concurrency | Most time spent waiting for DB/network |
| **Video encoding** | Parallelism | Pure CPU computation |

### Language/Runtime Considerations

| Environment | Concurrency Model | True Parallelism? |
|-------------|-------------------|-------------------|
| **Python (CPython)** | Threads, asyncio | No (GIL blocks threads) |
| **Python multiprocessing** | Processes | Yes |
| **Node.js** | Event loop, async/await | No (single-threaded) |
| **Go** | Goroutines | Yes (maps to OS threads) |
| **Java** | Threads, Virtual Threads | Yes |
| **Rust** | async/await, threads | Yes |

### 🛑 Common Pitfalls

- **Race conditions:** Two tasks modify shared state simultaneously
- **Deadlocks:** Task A waits for B, B waits for A
- **Thread overhead:** Creating thousands of OS threads is expensive
- **Assuming parallelism:** Python threads don't give you parallelism due to the GIL

[↑ Back to Table of Contents](#table-of-contents)

---

## 5. How These Concepts Interact

These foundational concepts are deeply interconnected:

```text
                    ┌─────────────┐
                    │  Scalability │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Latency  │◄───│Throughput│───►│Bandwidth │
    └──────────┘    └──────────┘    └──────────┘
          ▲                ▲
          │                │
          └───────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │  Concurrency/Parallelism  │
    └───────────────────────────┘
```

### Relationship Map

| If you improve... | You might see... | But watch out for... |
|-------------------|------------------|----------------------|
| **Scalability** (add servers) | Higher throughput | Increased latency (network hops) |
| **Latency** (faster responses) | Higher throughput | Diminishing returns |
| **Throughput** (more RPS) | Better scalability | May need more servers |
| **Concurrency** (handle more tasks) | Better latency under load | Race conditions, complexity |
| **Parallelism** (multi-core) | Faster computation | Limited by Amdahl's Law |

### Amdahl's Law

Not everything can be parallelized. If 50% of your code is sequential:

```text
Max speedup = 1 / (0.5 + 0.5/N)

With infinite cores: Max speedup = 2x (not infinite!)
```

### Little's Law

Connects concurrency, throughput, and latency:

```text
L = λ × W

L = Average number of concurrent requests
λ = Throughput (requests per second)
W = Average latency (seconds)
```

**Example:** If your system handles 100 RPS with 200ms average latency:

```text
L = 100 × 0.2 = 20 concurrent requests
```

To handle 1000 RPS at the same latency, you need capacity for 200 concurrent requests.

[↑ Back to Table of Contents](#table-of-contents)

---

## Quick Reference

| Concept | One-Line Definition |
|---------|-------------------|
| **Scalability** | Ability to handle increased load |
| **Horizontal scaling** | Add more machines |
| **Vertical scaling** | Upgrade existing machine |
| **Latency** | Time from request to response |
| **P99** | 99% of requests are faster than this |
| **Throughput** | Actual work completed per unit time |
| **Bandwidth** | Maximum theoretical capacity |
| **Concurrency** | Managing multiple tasks (structure) |
| **Parallelism** | Executing tasks simultaneously (execution) |

---

## Related Topics

- [Load Balancers](scalability_reliability.md#1-load-balancers-l7-vs-l4) - Horizontal scaling implementation
- [Caching Strategies](caching-strategies.md) - Latency reduction techniques
- [CDNs](scalability_reliability.md#4-content-delivery-networks-cdns) - Geographic latency reduction
- [Database Patterns](data_patterns.md) - Throughput and consistency tradeoffs
