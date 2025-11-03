# RabbitMQ vs Kafka — queue comparison for GDS Notification Service

Short answer
- For this alert-forwarding service RabbitMQ is the better choice in most deployments: it matches the work-queue/competing-consumer pattern, is easier to operate, and provides straightforward DLQ/retry and routing features. Choose Kafka only if you need very high throughput, long-term retention and native replay for many independent consumers.

Why this matters for the project
- Project requirements (summary):
  - Ingest alerts (email, SNMP, Slack/Teams-format webhooks) and deliver them to recipients.
  - Worker-pool processing: multiple worker replicas pull jobs, call a SQL Server stored-proc, and send outbound mail.
  - High availability and durability: alerts must not be lost; support retries and dead-lettering.
  - Throughput is expected to be modest — bursts of alerts, but each alert requires DB calls and outbound sends.
  - Ability to replay or audit alerts is useful, but primary need is prompt, reliable processing.

Comparison summary

1) RabbitMQ (recommended)
- Processing model: work-queue with competing consumers. Consumers ack/nack messages when processed.
- Guarantees: at-least-once delivery by default. Durable queues and persistent messages supported.
- DLQ & retries: native support via dead-letter exchanges and TTL-based retry patterns.
- Routing: flexible exchanges (direct, topic, headers) for routing alerts by db_instance, severity, etc.
- Ordering: FIFO per queue; you can create per-instance queues when ordering matters.
- Ops: simpler to operate and reason about. Managed options and k8s operators available.
- Best fit: worker queue, moderate volume, simple DLQ/retry requirements, fast time-to-operate.

2) Kafka
- Processing model: append-only log with partitions and consumer groups. Consumers manage offsets.
- Guarantees: at-least-once by default; exactly-once possible with careful config (idempotent producers, transactions).
- Replay & retention: excellent built-in replay and configurable long-term retention.
- Throughput & scaling: very high throughput and low per-message overhead; good for streaming/analytics.
- Ordering: ordering guaranteed within a partition; requires partition key planning.
- Ops: higher operational complexity (cluster management, partitioning, schema governance).
- Best fit: event streaming, long-term audit, many independent consumers, or extremely high ingest rates.

Key tradeoffs for this project
- Idempotency & exactly-once
  - RabbitMQ: easier app-level idempotency; at-least-once is natural and acceptable for alerts. Per-recipient dedupe is straightforward.
  - Kafka: can support exactly-once but requires more effort; good if you need absolute dedupe and transactional semantics.
- Reprocessing & audit
  - RabbitMQ: messages are removed after ack — reprocessing requires persisted `alert_events` (recommended) or special replay topics.
  - Kafka: native replay; consumers can rewind offsets and reprocess historical events easily.
- DLQ & retries
  - RabbitMQ: straightforward with dead-letter exchanges, TTLs and requeue strategies.
  - Kafka: implement retry topics/consumer logic or use frameworks for retry.
- Ordering
  - RabbitMQ: queue-level FIFO; use per-instance queues for strict ordering.
  - Kafka: partition-level ordering; plan keys and partition counts to preserve ordering.
- Operational cost
  - RabbitMQ: easier to run, quicker to get right for a team with standard infra.
  - Kafka: more operational overhead; consider managed Kafka if needed.

Recommendation
- Use RabbitMQ for the PoC and most production deployments for the GDS Notification Service. It maps to the ingest → durable queue → worker → send pattern and keeps operational burden low.
- Keep the option to adopt Kafka later if requirements evolve (e.g., need for long retention, multi-team replay, or very high ingest volume). Design the ingest path so alerts are persisted (in `alert_events`) and can be published to Kafka later without changing core processing logic.

Production configuration guidance (RabbitMQ)
- Durability:
  - Use durable queues and persistent messages (delivery_mode=2).
  - Enable publisher confirms so producers know when messages are safely stored.
- HA & queues:
  - Use quorum queues for HA in modern RabbitMQ setups (prefer over classic mirrored queues).
  - Configure appropriate VM/cluster sizing and monitoring.
- Consumers:
  - Set prefetch_count low (e.g., 1 or a small number) so a worker blocked on DB/send doesn't hold many messages.
  - Acknowledge only after per-recipient sends succeed (or persist attempt before send for stronger dedupe).
- DLQ & retry:
  - Use dead-letter exchanges for failed messages and TTL-based retry queues for backoff. Alternatively track attempt_count in DB and requeue as needed.
- Message size & attachments:
  - Keep broker messages small: include alert metadata and a link to attachments stored in object storage. Avoid sending large attachments through the broker.
- Observability:
  - Use rabbitmq_exporter for Prometheus metrics; alert on unacked messages, queue depth, and publish/confirm failures.

If Kafka becomes necessary
- Consider using Kafka alongside RabbitMQ: publish the persisted `alert_events` to a Kafka topic for analytics and replay while RabbitMQ drives real-time processing.
- If moving entirely to Kafka, design topics and partitions so that ordering and consumer group semantics match your per-instance delivery needs.

Suggested next engineering steps
1. Harden RabbitMQ usage in the PoC:
   - Persist `alert_events` before enqueueing.
   - Use publisher confirms and persistent messages.
   - Add DLQ and retry queues (TTL + dead-letter exchange) and implement attempt_count tracking in DB.
2. Add observability: queue depth, unacked counts, and producer confirm metrics.
3. Optional: add a Kafka export path for analytics/audit if replay/audit is needed later.

Contact
If you want, I can implement the RabbitMQ hardening (publisher confirms, durable messages, DLQ + persistence) in the PoC and run local tests — tell me to proceed and I'll update the todo and apply the changes.
