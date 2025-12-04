# Systems Design Best Practices

> Version: 1.0.0
>
> Purpose: Practical, technology-agnostic guidance for designing reliable, scalable, secure, and maintainable systems. Use with project-specific ADRs and threat models.
>
> Last Updated: 2025-11-08

## Core Principles

- Start from user and business outcomes; define SLOs and error budgets early.
- Optimize for simplicity, evolvability, and operability before micro-optimizations.
- Make failure a first-class scenario: design for resilience, not just happy paths.
- Prefer boring, well-understood tech for critical paths; minimize novelty surface area.
- Observe everything: logs, metrics, traces, profiles; make it easy to debug.
- Security and privacy by default; least privilege and data minimization.

## Architecture and Boundaries

- Choose the simplest architecture that meets requirements; prefer modular monoliths until clear scaling or ownership boundaries emerge.
- Separate domain/core from adapters (hexagonal/clean architecture); keep frameworks at the edges.
- Establish clear service boundaries, ownership, and SLAs; design APIs as contracts.
- Avoid tight coupling through shared databases or shared mutable state across services.

## Data Modeling and Storage

- Model data from access patterns and invariants; use correct normalization/denormalization trade-offs.
- Define consistency needs (strong, eventual, bounded staleness) explicitly per use case.
- Use transactions where needed; when not available, use sagas/outbox patterns with idempotency.
- Plan for schema evolution: forward/backward compatibility, migrations with dual writes/reads when necessary.
- Classify data (PII/PHI/PCI) and apply retention, encryption, and access controls accordingly.
- Support "Right to be Forgotten" (GDPR/CCPA) with automated deletion/anonymization workflows.

## API and Contract Design

- Contract-first design (OpenAPI/AsyncAPI/GraphQL SDL) with explicit versioning.
- Stable resource models, predictable pagination, filtering, and sorting.
- Idempotent and safe operations where applicable; provide idempotency keys for retries.
- Consistent error models with actionable messages and machine-readable details.
- Backwards-compatible changes by default; document and sunset breaking changes.

## State, Caching, and Performance

- Use caches to reduce latency and load, with explicit TTLs and invalidation strategies.
- Prefer cache-aside for simplicity; consider write-through/write-behind when justified.
- Avoid unbounded caches; enforce size/time limits; measure hit ratios.
- Apply rate limiting and backpressure at edges to protect downstreams.
- Profile critical paths; measure p50, p95, p99 latencies; right-size resources based on data.

## Async Communication and Events

- Choose async (queues/streams) for decoupling and throughput; document delivery guarantees (at-most/at-least/exactly-once semantics).
- Ensure idempotency for consumers; use deduplication windows and idempotency keys.
- Use the transactional outbox or change data capture to avoid dual-write anomalies.
- Define DLQs and replay strategies; make reprocessing safe and bounded.

## Resilience Patterns

- Timeouts everywhere; never rely on infinite waits.
- Retries with jittered exponential backoff for transient failures; limit attempts and total time.
- Circuit breakers, bulkheads, and request hedging where appropriate.
- Graceful degradation and feature kill switches for partial outages.
- Chaos, latency, and failure injection testing in non-prod; practice incident response.

## Observability

- Structured logs with correlation/trace IDs and key context; no secrets in logs.
- Metrics follow RED (Rate, Errors, Duration) and USE (Utilization, Saturation, Errors) methods.
- Distributed tracing across service boundaries with sampling strategies.
- Build golden signals dashboards and alert on SLO-based burn rates, not raw metrics alone.
- Monitor cost as a first-class metric (FinOps); tag resources for attribution.

## Security and Privacy

- Threat model early; track and remediate high-risk findings.
- Centralize authn/authz; prefer short-lived tokens and scoped credentials.
- Encrypt data in transit and at rest; manage keys securely (KMS/HSM).
- Validate and sanitize inputs; encode outputs; use secure defaults (CORS, CSP, cookie flags).
- Minimize data collection; apply retention and deletion policies; log access for audit.

## Deployment and Operations

- Infrastructure as Code; immutable artifacts; provenance and SBOMs.
- Progressive delivery (canary/blue-green) with automated rollback on SLO regressions.
- Keep configuration and secrets external; validate on startup; fail fast.
- Runbooks for common incidents; playbooks for failover and disaster recovery.
- Capacity planning and autoscaling policies with headroom for N+1 failures.
- Optimize for sustainability and cost-efficiency; right-size resources dynamically.

## Testing Strategy

- Unit and contract tests for interfaces; integration tests for critical flows.
- Soak and load tests; capture baseline and regressions before go-live.
- Chaos and disaster recovery drills; practice RPO/RTO objectives.

## Disaster Recovery and Geo

- Define RTO/RPO and tier systems accordingly.
- Backups: test restore regularly; automate and audit.
- Multi-AZ by default for critical services; consider multi-region for strict SLOs.
- Data sovereignty and residency requirements inform placement and replication.

## Governance and Change Management

- Use ADRs for significant decisions; capture context, options, consequences.
- Enforce change approval for high-risk changes; automate low-risk paths.
- Treat documentation as code; version control architecture decisions and runbooks.
- Track operational readiness with a pre-launch checklist (below).

## Operational Readiness Checklist

- SLOs defined and observable; alerts mapped to runbooks.
- Capacity model and load test results documented; autoscaling configured.
- Backups and restores tested; DR plan and drills completed.
- Security review complete; secrets managed; dependencies scanned; SBOM available.
- Config validated; feature flags and kill switches in place.
- Clear on-call ownership; escalation paths; dashboards and logs in place.
- Rollback strategy tested; canary/blue-green plan ready.

## References

- The Twelve-Factor App — [https://12factor.net](https://12factor.net)
- Google SRE Book — [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)
- OWASP ASVS — [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/)
- AWS Well-Architected — [https://docs.aws.amazon.com/wellarchitected/latest/framework/](https://docs.aws.amazon.com/wellarchitected/latest/framework/)
- NIST SP 800-53 — [https://csrc.nist.gov/publications/sp800-53](https://csrc.nist.gov/publications/sp800-53)

## Version History

- 2025-11-08 — Initial publication.
