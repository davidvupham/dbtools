# Deployment Notes & Runbook (PoC)

This document gives minimal guidance for local PoC deployment and notes for production deployment.

Local PoC (docker-compose)
- Requirements: Docker and Docker Compose
- Start services:

  docker-compose up --build

- This starts:
  - RabbitMQ (5672/15672)
  - MailHog (SMTP 1025, UI 8025)
  - `ingest` FastAPI service (8000)
  - `worker` consuming from `alerts` queue

Production guidance
- Use Kubernetes (Deployments + HPA) or managed container service with:
  - Stateless ingest service behind an ingress / ALB
  - Managed durable queue (SQS/Service Bus/RabbitMQ cluster)
  - Worker Deployment with replicas and liveness/readiness probes
  - SQL Server as persisted store (or Postgres equivalent) for alert events, idempotency and send status
  - Outbound provider: SendGrid/SES with API-based sending for scale

Secrets & configuration
- Store DB credentials and API keys in Vault/KeyVault/Secrets Manager.
- Use Kubernetes secrets or a sidecar agent to fetch secrets at startup.

Scaling & HA
- Scale the ingest service separately from workers. Ingest handles validation & enqueue; workers handle CPU/network.
- Configure queue redrive policies (DLQ) and set worker retry/backoff.

Runbook (common incidents)
- DB unavailable: workers should retry with backoff; monitor and alert on persistent failures; manual reprocessing from persisted alerts may be necessary.
- Large spike of alerts: throttle worker concurrency and ensure outbound provider rate limits are respected. Consider autoscaling workers and/or batching.
- DLQ items: provide an admin UI or script to examine and requeue after fix.
