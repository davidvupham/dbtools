# Module 3: Dynamic Secrets and Secret Engines

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)

> [!IMPORTANT]
> **Prerequisites:** Complete Modules 1-2, basic database knowledge

## Module overview

This module covers dynamic secrets - credentials generated on-demand with automatic expiration. You'll learn to configure database, AWS, PKI, and Transit secrets engines.

## Learning objectives

By the end of this module, you will be able to:

- Explain the benefits of dynamic secrets over static credentials
- Configure the database secrets engine for PostgreSQL
- Generate dynamic AWS IAM credentials
- Set up a PKI secrets engine for certificate management
- Use the Transit engine for encryption-as-a-service

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 11 | [Dynamic Secrets Concepts](./11-dynamic-secrets-concepts.md) | Leases, TTLs, rotation benefits |
| 12 | [Database Secrets Engine](./12-database-secrets-engine.md) | PostgreSQL, MySQL configuration |
| 13 | [AWS Secrets Engine](./13-aws-secrets-engine.md) | IAM users, STS credentials |
| 14 | [PKI Secrets Engine](./14-pki-secrets-engine.md) | Certificate authority, TLS certs |
| 15 | [Transit Secrets Engine](./15-transit-secrets-engine.md) | Encryption as a service |

## Project

**[Project 3: Database Connection Manager](./project-3-db-connection-manager.md)**

Build a service that provides applications with dynamic database credentials.

## Assessment

- **[Quiz: Module 3](./quiz-module-3.md)**
- **[Exercises](./exercises/)**

## Key concept: Dynamic vs static secrets

```
┌─────────────────────────────────────────────────────────────────────────┐
│                STATIC vs DYNAMIC SECRETS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   STATIC SECRETS (Traditional)                                          │
│   ────────────────────────────                                           │
│   • Created once, used forever                                          │
│   • Shared across applications                                          │
│   • Manual rotation required                                            │
│   • Long exposure window if compromised                                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ App1 ─┬─▶ password="SharedSecret123" ──▶ Database               │   │
│   │ App2 ─┤                                                          │   │
│   │ App3 ─┘   (Same credential, never expires)                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   DYNAMIC SECRETS (Vault)                                               │
│   ───────────────────────                                                │
│   • Generated on-demand                                                 │
│   • Unique per application/request                                      │
│   • Automatic expiration                                                │
│   • Minimal exposure window                                             │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ App1 ──▶ v-app1-abc123 (expires 1h) ──┐                         │   │
│   │ App2 ──▶ v-app2-def456 (expires 1h) ──┼──▶ Database             │   │
│   │ App3 ──▶ v-app3-ghi789 (expires 1h) ──┘                         │   │
│   │         (Unique, short-lived credentials)                        │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Estimated time

| Component | Duration |
|-----------|----------|
| Lessons (5) | 6-8 hours |
| Exercises | 3-4 hours |
| Project | 3-4 hours |
| Quiz | 30 minutes |
| **Total** | 12-16 hours |

## Lab environment

This module requires additional infrastructure:

```yaml
# docker-compose.module3.yml
services:
  vault:
    image: hashicorp/vault:1.15
    ports:
      - "8200:8200"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: vaultdemo
    ports:
      - "5432:5432"
```

## Getting started

1. Start the lab environment
2. Read [Lesson 11: Dynamic Secrets Concepts](./11-dynamic-secrets-concepts.md)
3. Complete each lesson's hands-on lab

---

**Ready to start?** Begin with [Lesson 11: Dynamic Secrets Concepts](./11-dynamic-secrets-concepts.md).
