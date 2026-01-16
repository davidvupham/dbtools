# Changelog

All notable changes to the gds_metrics package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-05

### Added

- **OpenTelemetry Support**: New `OpenTelemetryMetrics` backend for unified observability
  - Automatic trace context enrichment (trace_id, span_id)
  - Integrates with OTel Collector for centralized telemetry
  - Counter, gauge, histogram, and timing support
- **Trace Context Utilities**: New `context.py` module
  - `get_current_trace_context()` - Extract trace_id/span_id from active span
  - `with_trace_context()` - Enrich labels with trace context
- **Instrumentation Guide**: New `docs/INSTRUMENTATION_GUIDE.md`
  - Python application instrumentation patterns
  - PowerShell script instrumentation
  - Auto-instrumentation examples (Flask, SQLAlchemy)
  - Best practices for observability

### Changed

- Updated README with OpenTelemetry as recommended backend
- Added `opentelemetry` optional dependency group

### Dependencies

```toml
[project.optional-dependencies]
opentelemetry = [
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "opentelemetry-exporter-otlp>=1.20.0",
]
```

---

## [0.1.0] - 2025-12-05

### Added

- Initial release of gds_metrics package
- `MetricsCollector` protocol for type-safe metrics collection
- `NoOpMetrics` - Null object pattern for zero-overhead disabled metrics
- `ConsoleMetrics` - Debug-friendly metrics that print to stdout
- `PrometheusMetrics` - Full Prometheus integration with HTTP endpoint
- `CompositeMetrics` - Fan-out to multiple metrics backends simultaneously
- Comprehensive test suite with 98% code coverage
- Documentation including ARCHITECTURE.md, ROADMAP.md, and QUICKSTART.md

### Design Patterns

- **Strategy Pattern**: Swap metrics backends without code changes
- **Null Object Pattern**: NoOpMetrics for disabled metrics with zero overhead
- **Composite Pattern**: CompositeMetrics for multi-backend fan-out
- **Protocol/Interface**: Type-safe duck typing via `typing.Protocol`

### Implementations

| Implementation | Purpose | Dependencies |
|----------------|---------|--------------|
| NoOpMetrics | Disabled metrics | None |
| ConsoleMetrics | Debug/development | None |
| PrometheusMetrics | Production monitoring | prometheus-client |
| CompositeMetrics | Multi-backend fan-out | None |

---

## [Unreleased]

### Planned

- Structured logging integration
- Additional metric types (summary, info)
- Enhanced histogram bucket configuration
- Async metric collection
