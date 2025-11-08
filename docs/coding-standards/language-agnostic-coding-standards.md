# Language-Agnostic Coding Standards

> Version: 1.0.0
>
> Purpose: A concise, language-agnostic baseline for writing clear, secure, maintainable software across any stack. Use alongside language-specific standards and the Enforcement Guide.
>
> Last Updated: 2025-11-08

## Scope and How to Use

These standards apply to all code, regardless of language, framework, or runtime. Pair this with your language/framework guide (e.g., Python/PowerShell standards) and the Enforcement Guide for tooling, CI/CD, and IDE integration.

## Core Principles

- Readability over cleverness; optimize for maintainers.
- Simplicity first; avoid incidental complexity.
- Correctness and determinism; prefer pure functions when practical.
- Principle of least surprise; principle of least privilege for security.
- Security, privacy, and safety by default.
- Observability as a feature: logs, metrics, traces.
- Testability: code designed to be tested easily.
- Automation everywhere: formatting, linting, type checks, tests.

## Project Structure

- Organize by domain and clear module boundaries; avoid “misc/util” dumping grounds.
- Keep functions/classes small and single-purpose; apply single-responsibility.
- Separate domain logic from I/O and frameworks (hexagonal/clean architecture).
- Centralize cross-cutting concerns (logging, telemetry, auth, config) behind interfaces.
- Provide a top-level `README` and per-module `README` describing purpose and entry points.

## Naming, Style, and Layout

- Use descriptive, full-word names for clarity (avoid abbreviations).
- Name functions as verbs/verb-phrases; variables as nouns/noun-phrases.
- Use consistent casing per language ecosystem; do not mix styles in the same scope.
- Keep files focused; prefer multiple small files over one large file.
- Prefer explicit imports and exports; avoid wildcard imports.

## Documentation and Comments

- Document non-obvious rationale, invariants, and edge cases; avoid obvious comments.
- Provide module- and public-API-level docs explaining inputs, outputs, errors, and side effects.
- Maintain an Architecture Decision Record (ADR) trail for significant decisions; link ADRs from code where relevant.
- Keep examples up to date and runnable (doctests or CI-executed snippets where possible).

## Error Handling

- Fail fast and visibly; never silently swallow errors.
- Return or throw errors with context (what failed, inputs, correlation IDs).
- Prefer explicit, typed error categories (user error, transient, internal, external).
- Use retries with bounded backoff only for transient conditions; ensure idempotency.
- Provide user-safe messages externally; keep sensitive detail in logs only.

## Logging and Observability

- Log structured events with severity levels (trace/debug/info/warn/error/fatal).
- Include correlation/trace IDs, request IDs, and key identifiers (never secrets).
- Emit metrics for key success/failure rates and latency distributions.
- Use tracing for cross-service/cross-thread visibility.
- Protect PII/PHI: sanitize, minimize, and comply with data policies.

## Testing Strategy

- Test pyramid: unit >> integration >> end-to-end; target meaningful coverage across critical paths.
- Tests must be deterministic, isolated, and parallelizable by default.
- Use property-based and fuzz testing for critical parsing and security surfaces.
- Mock external systems; prefer contract tests for service boundaries.
- Use fixtures/factories; avoid test interdependence and global state.

## Concurrency and Async

- Avoid shared mutable state; prefer message passing or immutable data.
- Always set timeouts, cancellation, and deadlines for I/O and RPCs.
- Ensure idempotency for retried operations; use deduplication and idempotency keys where needed.
- Guard against deadlocks and starvation; keep critical sections small.

## Configuration and Secrets

- Follow 12-Factor principles: config via environment or injected config; never hardcode.
- Validate configuration at startup; fail fast on invalid config.
- Store secrets in a managed secret store; rotate regularly; never log secrets.
- Use feature flags for gradual rollout; default to safe behavior.

## Dependencies and Build

- Prefer standard library; add third-party deps only with clear benefit and maintenance plan.
- Pin versions and record a lock/constraints file; track SBOM where possible.
- Remove unused dependencies promptly.
- Keep builds reproducible and hermetic where feasible.

## Security Baseline

- Validate and sanitize all external inputs; encode outputs correctly.
- Adopt least privilege for credentials, tokens, and filesystem/network access.
- Enforce authentication and authorization consistently with centralized policy.
- Use modern cryptography primitives; avoid homegrown crypto.
- Keep dependencies updated and scanned (SCA); address critical CVEs promptly.
- Follow secure defaults: HTTPS/TLS, secure cookies, CSRF protections where relevant.

## Performance and Efficiency

- Measure before optimizing; use representative load and data.
- Prefer clarity unless a measured hotspot requires optimization.
- Consider algorithmic complexity and data structure choices for scale.
- Apply caching with explicit TTLs and invalidation strategy; verify correctness first.

## Accessibility and UX (when applicable)

- Respect localization/time zones/character sets; avoid assumptions about locale.
- Follow accessibility best practices (contrast, keyboard navigation, ARIA roles).
- Provide helpful, actionable error messages.

## Code Review Checklist

- Correctness: logic, edge cases, error handling, idempotency.
- Clarity: naming, structure, and documentation.
- Tests: sufficient coverage, deterministic, meaningful assertions.
- Security: input validation, authz/authn, secret handling, PII.
- Observability: structured logs, metrics, traces with context.
- Performance: big-O sanity, memory/latency hotspots only when measured.
- Backwards compatibility: APIs, configs, schema changes.
- Dependencies: necessity, pinned versions, licensing.
- Compliance: data policies, retention, auditing where applicable.

## CI/CD Expectations

- Automated formatting, linting, type checks, tests on every change.
- Require code review and status checks before merge.
- Build artifacts and SBOMs are reproducible and traceable.
- Use canary/blue-green where appropriate; include rollback plans.

## Versioning and Compatibility

- Version libraries and APIs semantically; document breaking changes clearly.
- Provide deprecation paths and timelines; add telemetry for usage of deprecated features.

## Maintenance

- Keep this document aligned with language-specific guides and the Enforcement Guide.
- Record updates with date and rationale in Version History.

## Version History

- 2025-11-08 — Initial publication.
