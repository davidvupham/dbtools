# SolarWinds DPA — Integration Guidance

This document describes how SolarWinds Database Performance Analyzer (DPA) can deliver alerts and recommended ways to integrate DPA with the GDS Notification Service.

Summary from SolarWinds documentation
- DPA contact types: email contacts, webhook contacts (for Slack or Teams), and SNMP trap targets. You can group contacts into contact groups and assign groups to alerts or reports.

Supported outbound alert methods (relevant to ingestion)
- Email notifications: DPA can send alert emails using configurable email templates and contact lists. Emails are standard MIME messages and include headers and templates that identify alert name, instance, severity, and details.
- Webhook contacts: DPA supports webhook contacts (commonly used for Slack/Teams). Webhooks post JSON payloads to an HTTP endpoint.
- SNMP traps: DPA can send SNMP traps (not directly handled by this service; use a trap receiver if you prefer SNMP ingestion).

Recommended integration approaches
1. Preferred: Webhook contact -> GDS Notification HTTP ingest
   - Create a webhook contact in DPA that posts JSON to the `ingest` endpoint of this service (or to a small adapter). This gives structured payloads and avoids parsing email bodies.
   - Advantages: structured, easier to parse, lower chance of missing fields, supports rich metadata.

2. Email-based integration (common)
   - Configure DPA to send alert emails to an address handled by one of these options:
     - Inbound email provider (SendGrid/Mailgun/SES) which posts parsed JSON to our webhook endpoint (recommended if you prefer provider-managed ingestion).
     - A dedicated mailbox that our IMAP poller reads (if a provider webhook is not possible). The IMAP poller should read full MIME messages, extract Message-ID, subject, plain-text/html body and attachments.
   - Advantages: often simpler to configure within DPA (email contacts), works without custom scripting on DPA side.

3. Direct action (custom script)
   - DPA alerts can trigger actions or external programs; you can implement a small script on the DPA host that POSTs a clean JSON payload to the ingest endpoint (same benefits as webhook).

Mapping fields and idempotency
- For email ingestion use the `Message-ID` header as the idempotency key where available. If the header is missing, compute a hash over (alert_name, subject, body_text, received_at).
- For webhook ingestion, require an `idempotency_id` field in the JSON payload or derive one from a unique alert id provided by DPA.
- Typical fields to map from DPA alerts:
  - alert_name (or rule name)
  - db_instance (name or id)
  - severity
  - timestamp (when alert fired)
  - description/details
  - link to the DPA console for more context

Email template considerations
- If using email ingestion, configure DPA email templates to include a consistent alert name tag and, if possible, a unique alert id in the headers or body.
- Avoid sending extremely large attachments; if necessary, send links to logs or use an object store with short-lived links.

Blackout periods & recipient selection
- Use the stored-proc logic and the blackout periods table to filter recipients returned for a given (alert_name, db_instance) pair. Webhook payloads should include `alert_name` and `db_instance` so the worker can make correct DB lookups.

Authentication & security
- Webhook: protect the ingest endpoint using HMAC signatures or mutual TLS; configure the webhook contact in DPA to include a shared secret if possible.
- Email: if using inbound parse providers, configure SPF/DKIM as needed and restrict who can post to your provider's webhook.

Example minimal webhook payload (recommended)
{
  "idempotency_id": "dpa-12345",
  "alert_name": "High CPU",
  "db_instance": "db-prod-01",
  "severity": "critical",
  "timestamp": "2025-11-01T12:34:56Z",
  "subject": "DPA Alert: High CPU on db-prod-01",
  "body_text": "CPU at 98% on host...",
  "details_url": "https://dpa.company.example/alert/12345"
}

Recommended configuration checklist for DPA admins
- Create a dedicated contact or contact group for the notification service.
- Prefer webhook contacts pointing to a secure ingest endpoint. If webhook is not possible, use an email contact that delivers to a managed inbound-parsing provider or a dedicated mailbox.
- Add a header or a consistent template field you can use as an idempotency key if Message-ID is not reliable.

Next steps for this project
- If you want, I can add an example webhook adapter (FastAPI handler) that validates DPA webhook payloads and enqueues jobs, and/or extend the IMAP poller to parse common DPA email templates. Tell me which path you prefer (webhook adapter or IMAP parser), and I will implement it in the PoC.
