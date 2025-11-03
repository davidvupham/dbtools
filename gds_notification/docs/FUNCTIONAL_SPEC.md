# Functional Specification — GDS Notification Service

This functional spec describes the responsibilities, API contracts, data flows, and success criteria for each component prior to implementation.

1. Actors and Inputs
- Monitoring systems: send alert emails.
- The service: receives alert emails, enriches them, determines recipients, forwards alerts.

2. High-level flow
1. Ingest: inbound webhook POSTs or the IMAP poller receives the email. The ingest service normalizes to an Alert object and persists it with an idempotency key (derived from Message-ID or generated hash).
2. Queue: the ingest service writes a job to a durable queue (or directly schedules a worker task).
3. Worker: picks the job, queries SQL Server stored proc to obtain recipients for that alert (based on alert name and DB instance), evaluates blackout periods, and prepares per-recipient messages.
4. Send: worker sends messages via configured outbound provider and records per-recipient status.
5. Post-processing: retries for transient failures, move to DLQ after N attempts, metrics emitted.

3. API Contract (PoC)
- POST /ingest
  - Accepts JSON or multipart mimicking inbound parse providers. Minimal required fields: message_id, subject, body_text, body_html (optional), received_at, raw_headers.
  - Responses: 202 Accepted with job id and idempotency id.

4. Stored Procedure Contract (example)
- Name: dbo.GetRecipientsForAlert
- Inputs:
  - @AlertName NVARCHAR(200)
  - @DbInstanceId INT
  - @AlertSeverity INT = NULL
  - @IdempotencyId NVARCHAR(200) = NULL
- Output: result set with columns: RecipientEmail NVARCHAR(256), RecipientName NVARCHAR(256), RecipientId INT, DeliveryChannel NVARCHAR(20) (e.g., 'email')

5. Idempotency
- Use `message_id` (Message-ID header) as the idempotency id. If missing, compute SHA256 of (subject + body + received_at).
- Persisted alert record keyed by idempotency id. If duplicate ingestion occurs the endpoint returns 200/202 with existing job id and does not re-enqueue.

6. Blackout periods
- Can be specified per recipient group or per database instance.
- Worker filters recipients where current time overlaps an active blackout period.

7. Delivery semantics
- At-least-once overall, but de-duplication when possible so recipients don't receive duplicates.
- Retries for transient failures with exponential backoff. After configurable max attempts, move recipient/job to DLQ and alert ops.

8. Failure modes & recovery
- Stored-proc or DB down: worker retries; if persistent, job returns to queue or moves to DLQ.
- SMTP/provider throttling: worker applies rate limiting and respects provider response codes.

9. Security
- Webhook auth using HMAC signature (or provider-specific header verification).
- All internal secrets in Vault (e.g., DB creds, SMTP keys). Use short-lived tokens where possible.

10. Observability
- Expose Prometheus-style metrics: queue_depth, jobs_processed_total, jobs_failed_total, recipient_send_success_total, recipient_send_failed_total.
- Structured logs include job id, idempotency id, alert name, db_instance_id, and recipient id.
