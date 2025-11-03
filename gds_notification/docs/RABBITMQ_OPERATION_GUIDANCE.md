# RabbitMQ: Self-host vs Managed — Guidance for GDS Notification Service

This document summarises the operational choices for RabbitMQ and gives practical
recommendations for the GDS Notification Service: when to self-host, when to use a
managed provider, and what you must do in each case.

Short recommendation
- Use a managed RabbitMQ offering (CloudAMQP, Amazon MQ for RabbitMQ, or vendor SaaS) if you
  want to minimize operational burden and get the RabbitMQ semantics the service expects.
- Self-host RabbitMQ (VMs, containers or Kubernetes with the RabbitMQ Operator) only if you
  require full control (air-gapped networks, strict compliance, or specific on-prem constraints).

Why this decision matters
- RabbitMQ is a stateful, clustered service that requires ongoing operation for HA, backups,
  upgrades, monitoring, capacity planning and incident response. Choosing managed vs self-host
  changes who performs these tasks and how much engineering time is spent on the broker.

Responsibilities: Self-hosted RabbitMQ
If you run RabbitMQ yourself you must cover the following areas:

- Provisioning & installation
  - Install RabbitMQ nodes (or operator), provision VMs/k8s resources and persistent volumes.
  - Plan capacity: CPU, memory, disk I/O, and network.

- Clustering & HA
  - Configure quorum queues or mirrored queues (quorum recommended for modern deployments).
  - Design node placement across availability zones / hosts to tolerate failures.
  - Plan for split-brain and node recovery scenarios.

- Upgrades & patches
  - Test and execute RabbitMQ version upgrades, Erlang compatibility, and plugin lifecycle.

- Security
  - Operate TLS for client and inter-node communication, manage TLS certificates, and rotate them.
  - Enforce user permissions, vhosts and network ACLs. Optionally integrate with LDAP/AD.

- Monitoring & alerting
  - Export and monitor metrics (queue depth, unacked messages, memory/disk alarms, connection counts).
  - Alert on critical thresholds and degraded node health.

- Backups & recovery
  - Understand durability guarantees and plan for persistent storage backups.
  - Consider shovel/federation for cross-region replication or disaster recovery.

- Operations & runbook
  - Build runbooks for common incidents: node failure, high disk usage, partition handling.
  - Automate health checks, automated restarts, and safe maintenance windows.

Responsibilities: Managed RabbitMQ (recommended path)
Using a managed service shifts most of the above responsibilities to the provider. You still are
responsible for:

- Configuration & policies
  - Define queues, exchanges, bindings, policies (e.g., DLQ, TTL) and tuning parameters.

- Credentials & access control
  - Create and rotate credentials for applications. Use short-lived credentials when supported.

- Observability & application-level health
  - Integrate provider metrics into your monitoring and alerting. Monitor queue depth and unacked counts.

- Cost & provisioning
  - Manage cost, sizing and scaling settings with the provider (plan instance size, throughput tiers).

Pros and cons (summary)

- Self-host
  - Pros: full control, possible lower raw cost at very large scale, fits strict on-prem / compliance needs.
  - Cons: operational overhead, patching/upgrades, backups, HA complexity, staffing cost.

- Managed
  - Pros: minimal broker ops, provider handles HA/patching/backups, faster time-to-production.
  - Cons: recurring cost, limited to provider features/quotas, some network/latency considerations.

When to self-host
- You must be on-prem / air-gapped with no external managed options.
- You have internal policy or compliance requiring full control over the messaging layer.
- You already operate RabbitMQ at scale and have automation and SRE processes in place.

When to use managed
- You prefer to minimize operational burden and focus on application logic.
- You need a quick, reliable managed environment for PoC and production without building the
  people/process to run a stateful broker.

Practical production recommendations (managed or self-host)

- Use quorum queues (or provider equivalent) for high durability.
- Always publish persistent messages (delivery_mode=2) and enable publisher confirms in producers.
- Use prefetch_count=1 (or small) for workers that perform blocking DB and network calls.
- Keep messages small; offload attachments to object storage and pass links in messages.
- Implement DLQ via dead-letter exchange and TTLs (or provider-managed DLQ features).
- Instrument with Prometheus metrics (rabbitmq_exporter) and alert on queue depth, unacked messages, disk alarms.

Connecting the PoC to managed RabbitMQ

If you choose managed RabbitMQ I can update the PoC to support a connection URL (AMQP URI) via env
var `RABBIT_URL` and provide sample configuration for CloudAMQP and Amazon MQ, including secure
TLS connectivity and credential rotation notes.

If you choose self-host on Kubernetes

- Use the official RabbitMQ Kubernetes Operator to simplify lifecycle management.
- Use persistent volumes with high IOPS and configure resource requests/limits per node.
- Automate upgrades using the operator and test Erlang/RabbitMQ version compatibility.

Next steps I can take for you
- Implement PoC wiring for a managed RabbitMQ provider (CloudAMQP example): update `service/main.py` to
  use publisher confirms and persistent messages, and add docs showing connection setup.
- Add Helm manifests / k8s Operator configuration for running RabbitMQ on your cluster.
- Add monitoring dashboards and example Prometheus alerts for queue depth and unacked messages.

- Pick which path you want and I will implement the corresponding artifacts in the project.
