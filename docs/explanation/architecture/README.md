# Architecture documentation index

This section groups the architecture decision records, evaluations, and design specifications for the GDS platform. Each subdirectory captures related artifacts for a given domain.

## Architecture decision records

- [Architecture Decision Records](decisions/README.md)
  - [ADR-001: UV Workspace Monorepo](decisions/001-uv-workspace-monorepo.md)
  - [ADR-002: Src Layout for Python](decisions/002-src-layout-python-packages.md)
  - [ADR-003: Diátaxis Documentation](decisions/003-diataxis-documentation.md)
  - [ADR-004: Database Abstraction Layer](decisions/004-database-abstraction-layer.md)

## Package structure

- [Package Dependencies](package-dependencies.md)
  - Internal package dependency visualization
  - Dependency matrix and categories
  - Guidelines for new packages

## Database & infrastructure

- [PostgreSQL High Availability](postgres-high-availability.md)
  - HA patterns and configurations

- [Database Change CI/CD](database-change-cicd/)
  - Database change management pipelines
  - Liquibase integration patterns

## Observability & monitoring

### OpenTelemetry

- [OpenTelemetry Architecture](observability/OPENTELEMETRY_ARCHITECTURE.md)
  - Comprehensive guide to unified observability with traces, metrics, and logs
  - Python and PowerShell integration patterns
  - OTLP vs Kafka architecture decisions
  - Correlation strategies for distributed systems
  - Trend analysis and predictive analytics approaches

### Logging

- [PowerShell Logging Architecture](observability/POWERSHELL_LOGGING_ARCHITECTURE.md)
  - Cross-platform PowerShell logging best practices
  - PSFramework, Serilog, and native approaches
  - Kafka streaming integration
  - Structured logging and log correlation
  - Configuration examples and troubleshooting

### Monitoring & alerting

- [Enterprise Observability, Notification, and Data Pipeline Architecture](observability/Enterprise_Observability_Notification_Data_Pipeline_Architecture.md)
  - Comprehensive monitoring and alerting architecture
  - Notification systems and escalation policies
  - Data pipeline design for telemetry

- [GDS Architecture Evaluation (2025-11-06)](observability/GDS_ARCHITECTURE_EVALUATION_2025-11-06.md)
  - Architecture evaluation and recommendations
  - Technology stack decisions

---

> **Note**: Add future updates (implementation notes, follow-up reviews) to the corresponding domain directory and extend this index accordingly.
