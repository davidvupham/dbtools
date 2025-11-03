# RabbitMQ vs Amazon MQ — comparison and cost guidance

This document compares operating RabbitMQ yourself (self-host), using generic managed RabbitMQ providers, and using Amazon MQ (AWS managed brokers that support RabbitMQ and ActiveMQ). It includes the cost drivers for Amazon MQ and an illustrative cost example to help with budgeting. Exact prices change over time — always consult the provider pricing page or the AWS Pricing Calculator for up-to-date numbers.

Summary recommendation
- If you want RabbitMQ semantics (competing consumers, exchanges, DLQ patterns) with minimal broker ops, a managed RabbitMQ provider (CloudAMQP, Amazon MQ for RabbitMQ, etc.) is a strong choice.
- Amazon MQ is a good managed option if you prefer first-class AWS integration and a managed, supported broker — it runs RabbitMQ or ActiveMQ and eliminates most operational work.
- Self-host RabbitMQ is attractive when you need full control, are on-prem, or have strict compliance requirements, but it requires ongoing operations (clustering, backups, upgrades, monitoring).

Key differences

- Operational responsibility
  - Self-host RabbitMQ: you operate and maintain cluster, PVs, upgrades and HA.
  - Managed RabbitMQ (CloudAMQP or Amazon MQ): provider manages the broker, HA, patching and some backups; you manage configuration, policies and credentials.

- Feature parity
  - Managed RabbitMQ offerings generally provide standard RabbitMQ semantics (exchanges, queues, DLQs). Amazon MQ for RabbitMQ is an AWS-managed RabbitMQ deployment with AWS integrations (IAM, CloudWatch, VPC support).

- Integration with cloud ecosystem
  - Amazon MQ integrates well with AWS networking, monitoring (CloudWatch), IAM and VPC. CloudAMQP and other managed providers provide different integrations and may be easier to use across multi-cloud.

- SLA & support
  - Managed services typically provide an SLA and vendor support; self-host relies on your SRE team.

Amazon MQ cost components (what you'll be billed for)

Amazon MQ pricing is made up of several components. The following list describes typical cost drivers — consult the AWS pricing page for exact per-region rates and current pricing.

- Broker instance hours
  - You pay per-hour for each broker instance. Amazon MQ offers instance classes of different sizes. For HA you typically run a pair or cluster across AZs.

- Storage
  - Persistent storage for queues/offsets/snapshots is billed per GB-month and may include I/O/throughput considerations.

- Data transfer
  - Data transferred out of the broker (cross-AZ or Internet) may incur data transfer charges.

- Snapshot / backup and retention
  - If Amazon MQ charges for snapshots or backup storage beyond included amounts, those add to cost.

- Optional features & support
  - Additional support tiers, monitoring, or premium features may add cost.

Illustrative example (costs are examples, not a quote)

The goal here is to show how to build a simple monthly estimate. Replace the placeholders with current AWS region prices from the AWS pricing page or AWS Pricing Calculator.

Assumptions for this example
- Region: us-east-1 (example)
- Broker choice: Amazon MQ for RabbitMQ
- Broker size: 2 x medium instances for HA (example)
- Storage: 100 GB persistent storage
- Data transfer out: 100 GB per month

Cost components (illustrative rates)
- Broker instance hourly rate (example): $0.20 per hour per broker
- Storage: $0.10 per GB-month
- Data transfer out: $0.09 per GB

Monthly calculation (30 days)
- Broker compute: 2 brokers * $0.20/hr * 24 hr/day * 30 days = $288.00
- Storage: 100 GB * $0.10/GB-month = $10.00
- Data transfer: 100 GB * $0.09/GB = $9.00
-- Total (illustrative): $307.00 / month

Notes about the example
- The hourly rate used above is an illustrative placeholder. Actual Amazon MQ instance-hour pricing depends on the instance type and region and may be higher or lower.
- For production you will likely choose instance types based on expected throughput and durability; higher throughput or larger memory will increase per-hour cost.

How to produce an accurate estimate for Amazon MQ

1. Determine capacity
   - Expected message rate (messages/sec), average message size, peak burst size, and retention/TTL for messages.
   - Expected number of concurrent connections (producer and consumer clients).

2. Choose broker size and HA model
   - For high availability, plan for at least two brokers across AZs. Choose instance sizes based on throughput.

3. Estimate storage and retention
   - Determine how much persistent storage you need (GB). If you plan long retention or large messages, storage grows.

4. Estimate network transfer
   - Estimate monthly outbound data transfer (GB). Data transfer between AZs may also incur charges.

5. Use the AWS Pricing Calculator or the Amazon MQ pricing page
   - Enter instance hours, storage, and data transfer to produce a monthly estimate. AWS provides per-region prices that you must use for a final quote.

Cost trade-offs and considerations

- Managed convenience vs cost
  - Managed Amazon MQ removes most broker ops and reduces staffing/time costs, but the per-month bill may be higher than raw infrastructure for large clusters.

- Right-sizing
  - Start with smaller broker instances for PoC and scale up. Monitor CPU, memory, and I/O and resize as needed.

- Multi-region / disaster recovery
  - If you need cross-region replication or federation, costs increase significantly.

- Alternative: CloudAMQP and other RabbitMQ SaaS
  - CloudAMQP offers RabbitMQ as a service with tiered pricing; it may be cheaper for small-to-medium workloads and offers easy scaling and plan-based pricing.

- Alternative: cloud-native queues (SQS, Service Bus)
  - If you prefer minimal operations and are OK with different semantics, SQS or Azure Service Bus may be cheaper and easier to operate at scale. They change semantics (visibility timeout, lack of exchange routing) and may require design changes.

Operational guidance — choosing between Amazon MQ and self-host

- Choose Amazon MQ if:
  - You want AWS-managed RabbitMQ with VPC, CloudWatch integration, and a managed SLA.
  - You prefer to avoid running a stateful broker and want AWS to handle HA, backups and patching.

- Choose self-host RabbitMQ if:
  - You must stay on-prem or air-gapped, have strict compliance or specific networking requirements, or already operate RabbitMQ at scale and can absorb the ops cost.

Final notes and links
- Exact Amazon MQ prices vary by region and instance class. For an accurate budget, use:
  - AWS Pricing Calculator: https://calculator.aws/
  - Amazon MQ pricing page: https://aws.amazon.com/amazon-mq/pricing/
  - CloudAMQP pricing: https://www.cloudamqp.com/pricing.html

If you want, I can:
- Replace the illustrative numbers above with a region- and instance-specific estimate (I will fetch current prices or you can provide a preferred AWS region and instance class), or
- Update the PoC to support a configurable `RABBIT_URL` and add a short doc showing how to connect to an Amazon MQ RabbitMQ broker (TLS config and IAM/credentials notes).
