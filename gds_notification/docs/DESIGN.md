# Design — GDS Notification Service

This design document covers component choices, sequence diagrams, HA strategy, and data flow details.

Components
- Ingest service (stateless): receives inbound emails (preferred webhook). Validates signature, normalizes payload, persists the alert record (idempotency key), and pushes a job to a durable queue.
- Durable queue: decouples ingestion from processing. Options: RabbitMQ (self-hosted), SQS (AWS), Azure Service Bus. For development RabbitMQ will be used in docker-compose.
- Worker(s): stateless processors that pull jobs, call the stored-proc to get recipients, filter recipients (blackouts), then forward alerts via outbound provider adapter.
- Outbound provider adapter: abstraction over SMTP and provider APIs (SendGrid/SES). Use API where available for higher throughput and observability.
- Persistence: alerts and per-recipient statuses stored in a relational DB (can be SQL Server or Postgres for PoC). The stored-proc (see docs/DATA_MODEL.sql) returns recipients for a given alert.

Sequence
1. Monitoring system -> Ingest (POST webhook)
2. Ingest: compute idempotency id, persist alert, publish job to queue
3. Worker: fetch job, connect to DB, exec dbo.GetRecipientsForAlert(@AlertName, @DbInstanceId)
4. Worker filters recipients by blackout windows and group membership
5. Worker sends emails to recipients via outbound adapter and records status
6. Worker acknowledges job; failures cause retry according to backoff policy

High Availability & Reliability
- Stateless components run in multiple replicas behind load balancers (Kubernetes Deployments + HPA recommended).
- Durable queue provides durable storage of jobs; queue persistence configured for safety.
- Database used for state (alert records and idempotency) should be backed up and monitored.
- Idempotency ensures duplicates are no-ops. Workers mark per-recipient send attempts with a unique send id to avoid double-sends.

Idempotency & Exactly-once Goals
- We aim for at-least-once delivery with application-level idempotency for per-recipient sends.
- Use a per-send unique hash (alert id + recipient id) persisted before attempting send; if the hash exists, skip sending.

Rate limiting & Throttling
- Implement a worker-level token-bucket rate limiter for outbound provider quotas.
- Optionally use a central rate-limiter service if many workers are deployed (Redis/leaky-bucket).

Security
- Webhook signature validation on ingest endpoint.
- TLS enforced between services.
- Secrets in Vault / KeyVault. DB creds scoped to execute the recipient stored-proc only.

Future extensibility
- Add alternate channels (SMS/Slack) by adding DeliveryChannel and adapters.
- Add per-recipient preferences and timezones for blackout windows.
