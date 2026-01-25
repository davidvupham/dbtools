# System Design Learning Path

**[← Back to Systems Tutorials](../README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

This directory contains resources for learning System Design, organized into the **4 Phases of Scalability** (based on [Shalini Goyal's framework](https://x.com/goyalshaliniuk/status/1998278941665276137)).

---

## Foundational Concepts

*Start here. Master the vocabulary before diving into patterns.*

- **[Fundamentals](concepts/fundamentals.md)**: Scalability (horizontal vs vertical), Latency (P50/P95/P99), Throughput vs Bandwidth, Concurrency vs Parallelism.

---

## Phase 1: Scaling the Foundation
*The core building blocks associated with handling load.*
- **[SQL vs NoSQL](concepts/sql_vs_nosql.md)**: ACID vs BASE, when to choose each, NoSQL types, polyglot persistence.
- **[Database Patterns](concepts/data_patterns.md)**: Sharding, CAP Theorem, PACELC, CQRS, Event Sourcing.
- **[Caching Strategies](concepts/caching-strategies.md)**: Cache-first design, key patterns, cold starts, cache stampede prevention.
- **[Caching Basics](concepts/data_patterns.md#4-redis-caching)**: Read-Through, Write-Behind, eviction policies.
- **[Load Balancers](concepts/scalability_reliability.md#1-load-balancers-l7-vs-l4)**: L4 vs L7, Horizontal Scaling.

## Phase 2: Architecting Your System
*Structuring the application logic.*
- **[Microservices](concepts/communication_patterns.md)**: Service Mesh, Sidecars, when to use (and not use).
- **[API Protocols](concepts/communication_patterns.md#3-rest-vs-graphql-vs-grpc)**: REST vs GraphQL vs gRPC, when to use each.
- **[Event-Driven Architecture](concepts/messaging_patterns.md)**: Kafka, Queues, Pub/Sub.
- **[API Gateways](concepts/communication_patterns.md#api-gateway)**: Rate Limiting basics, Routing.

## Phase 3: Enhancing Reach & Visibility
*Optimizing performance and understanding system health.*
- **[CDNs](concepts/scalability_reliability.md#4-content-delivery-networks-cdns)**: Edge caching for static content.
- **[Observability](concepts/observability.md)**: Metrics (Prometheus), Logging (ELK), Tracing.
- **[High Availability](concepts/scalability_reliability.md#5-high-availability-ha-strategies)**: Active-Active vs Active-Passive, Replication.

## Phase 4: Designing for Trust & Recovery
*Ensuring security and resilience.*
- **[Security](concepts/security.md)**: Authentication (OAuth/JWT), Encryption (TLS/At-Rest), Access Control (RBAC).
- **[Fault Tolerance](concepts/scalability_reliability.md#3-circuit-breakers)**: Circuit Breakers, Retry logic (Jitter).
- **[Consistency Models](concepts/distributed_algorithms.md)**: Strong vs Eventual Consistency, Consensus (Raft/Paxos).

---

## 🏗️ Real-World Designs
*Applying the concepts to build actual systems.*
- **[URL Shortener (TinyURL)](designs/design_url_shortener.md)**: ID Generation, Redirects.
