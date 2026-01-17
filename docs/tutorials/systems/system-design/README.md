# System Design Learning Path

This directory contains resources for learning System Design, organized into the **4 Phases of Scalability** (based on [Shalini Goyal's framework](https://x.com/goyalshaliniuk/status/1998278941665276137)).

## Phase 1: Scaling the Foundation
*The core building blocks associated with handling load.*
- **[Database Patterns](concepts/data_patterns.md)**: Sharding, CAP Theorem, NoSQL vs SQL.
- **[Caching](concepts/data_patterns.md#caching)**: Read-Through, Write-Behind, Eviction Policies.
- **[Load Balancers](concepts/scalability_reliability.md#1-load-balancers-l7-vs-l4)**: L4 vs L7, Horizontal Scaling.

## Phase 2: Architecting Your System
*Structuring the application logic.*
- **[Microservices](concepts/communication_patterns.md)**: Service Mesh, Sidecars.
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
