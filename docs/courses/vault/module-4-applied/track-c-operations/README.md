# Track C: Operations

**[← Back to Module 4](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Track overview

Learn to operate Vault in production: high availability, monitoring, and compliance.

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 16 | High Availability | Raft clusters, auto-unseal, disaster recovery |
| 17 | Monitoring and Metrics | Prometheus, Grafana, alerting |
| 18 | Audit and Compliance | Audit devices, log analysis, compliance reporting |

## Prerequisites

- Linux system administration
- Completed Modules 1-3

## Key concepts

### HA Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VAULT HA CLUSTER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │
│   │   Vault 1      │  │   Vault 2      │  │   Vault 3      │           │
│   │   (Active)     │  │   (Standby)    │  │   (Standby)    │           │
│   └───────┬────────┘  └───────┬────────┘  └───────┬────────┘           │
│           │                   │                   │                      │
│           └───────────────────┼───────────────────┘                      │
│                               │                                          │
│                      ┌────────┴────────┐                                │
│                      │   Raft Storage  │                                │
│                      │  (Integrated)   │                                │
│                      └─────────────────┘                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Auto-Unseal with AWS KMS

```hcl
# vault.hcl
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "alias/vault-unseal"
}
```

---

[← Back to Module 4](../README.md)
