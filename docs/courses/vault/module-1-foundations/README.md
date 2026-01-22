# Module 1: Foundations

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-green)

> [!IMPORTANT]
> **Prerequisites:** Basic command line usage, understanding of environment variables

## Module overview

This module introduces the fundamentals of secrets management and HashiCorp Vault. You will understand why secrets management matters, learn Vault's architecture, set up a development environment, and start working with secrets and policies.

## Learning objectives

By the end of this module, you will be able to:

- Explain why secrets management is critical for application security
- Describe Vault's architecture and core components
- Set up and configure a Vault development server
- Store and retrieve secrets using the KV secrets engine
- Write basic Vault policies to control access

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 01 | [Introduction to Secrets Management](./01-introduction-to-secrets-management.md) | The secrets problem, why Vault, use cases |
| 02 | [Vault Architecture](./02-vault-architecture.md) | Components, seal/unseal, storage backends |
| 03 | [Vault Dev Environment](./03-vault-dev-environment.md) | Docker setup, CLI basics, first commands |
| 04 | [Secrets Engines Basics](./04-secrets-engines-basics.md) | KV v1 vs v2, CRUD operations, versioning |
| 05 | [Vault Policies Introduction](./05-vault-policies-intro.md) | Policy syntax, capabilities, path patterns |

## Project

**[Project 1: Password Manager](./project-1-password-manager.md)**

Build a command-line password manager that stores credentials in Vault.

**Skills practiced:**
- Vault CLI operations
- KV secrets engine CRUD
- Basic policy creation
- Environment configuration

## Assessment

- **[Quiz: Module 1](./quiz-module-1.md)** - Test your understanding of core concepts
- **[Exercises](./exercises/)** - Hands-on practice for each lesson

## Estimated time

| Component | Duration |
|-----------|----------|
| Lessons (5) | 4-5 hours |
| Exercises | 2-3 hours |
| Project | 2-3 hours |
| Quiz | 30 minutes |
| **Total** | 8-11 hours |

## Prerequisites check

Before starting this module, verify you have:

```bash
# Docker or Podman installed
docker --version

# curl available
curl --version

# Text editor (VS Code recommended)
code --version
```

## Getting started

1. Read [Lesson 01: Introduction to Secrets Management](./01-introduction-to-secrets-management.md)
2. Complete the hands-on lab in each lesson
3. Work through the exercises in `exercises/`
4. Build [Project 1](./project-1-password-manager.md)
5. Take the [Module 1 Quiz](./quiz-module-1.md)

---

**Ready to start?** Begin with [Lesson 01: Introduction to Secrets Management](./01-introduction-to-secrets-management.md).
