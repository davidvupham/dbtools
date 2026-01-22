# Module 2: Authentication and Access Control

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-yellow)

> [!IMPORTANT]
> **Prerequisites:** Complete Module 1, understanding of basic policies

## Module overview

This module covers Vault's authentication methods and advanced access control. You will learn how to authenticate users and applications, design sophisticated policies, and manage identity with entities and groups.

## Learning objectives

By the end of this module, you will be able to:

- Understand Vault's token-based authentication system
- Configure AppRole authentication for applications
- Set up userpass and LDAP authentication for users
- Write advanced policies with templating and constraints
- Manage identity using entities and groups

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 06 | [Token Authentication](./06-token-authentication.md) | Token types, hierarchy, TTLs, accessors |
| 07 | [AppRole Authentication](./07-approle-authentication.md) | Role configuration, secret IDs, CI/CD integration |
| 08 | [Userpass and LDAP](./08-userpass-ldap-authentication.md) | Human authentication, LDAP integration |
| 09 | [Advanced Policies](./09-advanced-policies.md) | Templating, parameters, fine-grained control |
| 10 | [Entities and Groups](./10-entity-groups.md) | Identity management, group policies |

## Project

**[Project 2: Multi-User Secret Store](./project-2-multi-user-store.md)**

Build a secret store supporting multiple teams with different access levels.

**Skills practiced:**
- Multiple auth methods
- Role-based access control
- Policy templating
- Identity management

## Assessment

- **[Quiz: Module 2](./quiz-module-2.md)** - Test your understanding
- **[Exercises](./exercises/)** - Hands-on practice

## Estimated time

| Component | Duration |
|-----------|----------|
| Lessons (5) | 5-6 hours |
| Exercises | 2-3 hours |
| Project | 2-3 hours |
| Quiz | 30 minutes |
| **Total** | 9-12 hours |

## Key concepts

### Authentication flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VAULT AUTHENTICATION FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    1. Present credentials    ┌──────────────────┐       │
│   │  Client  │ ──────────────────────────▶  │   Auth Method    │       │
│   │          │                               │  (AppRole/LDAP)  │       │
│   │          │    2. Verify identity         │                  │       │
│   │          │ ◀──────────────────────────── │  → Check creds   │       │
│   │          │                               │  → Lookup entity │       │
│   │          │    3. Issue token             │  → Attach policies       │
│   │          │ ◀──────────────────────────── │                  │       │
│   └──────────┘    (policies, TTL, metadata)  └──────────────────┘       │
│        │                                                                 │
│        │ 4. Use token for operations                                    │
│        ▼                                                                 │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │                      VAULT OPERATIONS                         │     │
│   │  • Read secrets (if policy allows)                           │     │
│   │  • Write secrets (if policy allows)                          │     │
│   │  • Generate dynamic credentials (if policy allows)           │     │
│   └──────────────────────────────────────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Auth method comparison

| Method | Use Case | Best For |
|--------|----------|----------|
| **Token** | Direct token usage | Testing, emergency access |
| **AppRole** | Machine-to-machine | CI/CD, applications |
| **Userpass** | Username/password | Human users (simple) |
| **LDAP** | Enterprise directory | Human users (enterprise) |
| **Kubernetes** | K8s workloads | Container deployments |
| **AWS IAM** | AWS workloads | EC2, Lambda |

## Getting started

1. Ensure Module 1 is complete
2. Have your Vault dev server running
3. Read [Lesson 06: Token Authentication](./06-token-authentication.md)

---

**Ready to start?** Begin with [Lesson 06: Token Authentication](./06-token-authentication.md).
