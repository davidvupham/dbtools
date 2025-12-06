# Architecture Documentation Index

This section groups the architecture decision records, evaluations, and design specifications for the GDS platform. Each subdirectory captures related artifacts for a given domain.

## Observability & Monitoring

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

### Monitoring & Alerting

- [Enterprise Observability, Notification, and Data Pipeline Architecture](observability/Enterprise_Observability_Notification_Data_Pipeline_Architecture.md)
  - Comprehensive monitoring and alerting architecture
  - Notification systems and escalation policies
  - Data pipeline design for telemetry

- [GDS Architecture Evaluation (2025-11-06)](observability/GDS_ARCHITECTURE_EVALUATION_2025-11-06.md)
  - Architecture evaluation and recommendations
  - Technology stack decisions

---

> **Note**: Add future updates (implementation notes, follow-up reviews) to the corresponding domain directory and extend this index accordingly.
