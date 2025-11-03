# Requirements — GDS Notification Service

This document restates and clarifies functional and non-functional requirements before coding begins.

Primary goal
- Ingest monitoring alert emails and forward those alerts to recipient lists obtained from a SQL Server instance.

Assumptions (please confirm)
- Incoming alerts arrive as email messages (MIME). They can be delivered to our service using one of:
  - Managed inbound email webhook (preferred: SendGrid/Mailgun SES Inbound Parse) — provider POSTs email to our HTTP endpoint
  - IMAP mailbox polling/IDLE (alternative)
  - Direct SMTP ingest (only if necessary; higher operational burden)
- The SQL Server database does not currently contain the stored procedure; the service team will accept a schema and an implementation suggestion.
- The service must be cloud-agnostic but support deployment on Kubernetes. Managed queues (SQS/Service Bus) are acceptable.

Functional requirements
- Reliable ingestion of alert emails.
- For each unique alert, call a stored procedure (or DB API) to retrieve recipients.
- Forward the alert to recipients via SMTP or an email API (SendGrid/SES).
- Support recipient grouping and blacklist/blackout periods (time windows during which alerts are suppressed for a given group/instance).
- Persist processing status for each alert and recipient (sent/failed/no-recipients).

Non-functional requirements
- High availability: stateless front-end, durable queue, multiple worker replicas.
- At-least-once delivery semantics with idempotency safeguards so duplicates are not resent.
- Observability: metrics (queue depth, success/failure rates), structured logs, health checks.
- Security: webhook authentication, TLS for external connections, secrets stored in Vault-like store.
- Rate limiting: respect provider sending limits and avoid bursts that cause provider throttling.

- Choose ingestion method (webhook vs IMAP). If you can use a provider webhook, the PoC will assume webhook.
- Choose queue implementation (RabbitMQ for on-prem, SQS/Service Bus for cloud-managed).
- Choose outbound provider (SMTP vs SendGrid API). For PoC we'll use MailHog locally and provide an adapter for API.

SolarWinds DPA integration
- If your alerts originate from SolarWinds Database Performance Analyzer (DPA), see `docs/SOLARWINDS_INTEGRATION.md` for specific guidance. SolarWinds DPA can send alerts via email, webhook (e.g., Slack/Teams webhook contacts), and SNMP traps; the document recommends preferred integration patterns and mapping to the notification service.

Acceptance criteria for PoC
- Choose ingestion method (webhook vs IMAP). If you can use a provider webhook, the PoC will assume webhook.
- Choose queue implementation (RabbitMQ for on-prem, SQS/Service Bus for cloud-managed).
- Choose outbound provider (SMTP vs SendGrid API). For PoC we'll use MailHog locally and provide an adapter for API.

Acceptance criteria for PoC
- Able to POST a sample alert to an ingest endpoint.
- The service enqueues the alert and a worker calls the stored-proc (or mock) to get recipients.
- The worker sends message(s) to MailHog and status is updated to `sent`.
