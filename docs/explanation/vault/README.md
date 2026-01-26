# Vault Documentation - Where to Start

**[← Back to Documentation Index](../../README.md)**

> **Last Updated:** January 15, 2026

This directory contains comprehensive documentation for HashiCorp Vault secrets management. **Use this guide to navigate the right documents for your needs.**

## Quick Start

**New to Vault?** Start here:

1. **[Vault Concepts Guide](./vault-concepts.md)**
   - What is HashiCorp Vault?
   - Core concepts (Secrets Engines, Auth Methods, Policies, Tokens)
   - How Vault works
   - Security model
   - Key decisions to make

2. **[Vault Architecture Guide](./vault-architecture.md)**
   - Vault server architecture
   - Sealing and unsealing
   - Storage backends
   - High availability patterns
   - Our deployment standards

3. **[Developing with gds_vault](../../how-to/vault/developing-with-gds-vault.md)**
   - Authentication patterns
   - Retrieving secrets
   - Caching strategies
   - Best practices for applications

4. **[Vault Reference](../../reference/vault/README.md)**
   - **[gds_vault API](../../reference/vault/gds-vault-api.md)**
   - **[Vault CLI](../../reference/vault/vault-cli.md)**
   - **[Troubleshooting](../../reference/vault/troubleshooting.md)**
   - Environment variables
   - Configuration options
   - Glossary

## Document Map

### For Different User Roles

| Role | Read These First |
|:---|:---|
| **New Vault User** | Concepts → Architecture → Developing |
| **Developer Using gds_vault** | Concepts → Developing → Reference API |
| **DevOps/Platform Engineer** | Concepts → Architecture → Production Hardening |
| **Security Engineer** | Concepts → Architecture → Audit & Monitoring |
| **Troubleshooting Issues** | Reference (Troubleshooting section) |

### For Different Scenarios

| Scenario | Document | Section |
|:---|:---|:---|
| I want to understand what Vault does | Concepts | [What is Vault?](./vault-concepts.md#what-is-hashicorp-vault) |
| I want to understand core concepts | Concepts | [Core Concepts](./vault-concepts.md#core-concepts) |
| I need to retrieve secrets in Python | Developing | [Using gds_vault](../../how-to/vault/developing-with-gds-vault.md#using-gds_vault) |
| I need to authenticate my application | Developing | [Authentication Patterns](../../how-to/vault/developing-with-gds-vault.md#authentication-patterns) |
| I need to rotate AD passwords | How-To | [Rotate AD Passwords](../../how-to/vault/rotate-ad-passwords.md) |
| I'm seeing an error | Reference | [Troubleshooting](../../reference/vault/troubleshooting.md) |
| I need to harden production Vault | Architecture | [Production Hardening](./vault-architecture.md#production-hardening) |

## Full Document List

### 1. **Concepts Guide** (Read First!)

[vault-concepts.md](./vault-concepts.md)

**What it covers:**
- What Vault is and why use it
- Core concepts clearly explained
- Secrets engines (KV, Database, AD)
- Authentication methods (AppRole, Token)
- Policies and access control
- Tokens and leases

**When to read:**
- You're new to Vault
- You want to understand the fundamentals
- You're explaining Vault to others
- You're designing your secrets management strategy

---

### 2. **Architecture Guide** (Deployment & Security)

[vault-architecture.md](./vault-architecture.md)

**What it covers:**
- Vault server architecture
- Seal/Unseal process
- Storage backends
- High availability patterns
- Production hardening
- Audit logging
- Our deployment standards

**When to read:**
- You need to understand Vault server architecture
- You're deploying or managing Vault
- You're implementing production security
- You're configuring audit logging

**Prerequisites:** Read Concepts Guide first

---

### 3. **Developing with gds_vault** (Client Usage)

[how-to/vault/developing-with-gds-vault.md](../../how-to/vault/developing-with-gds-vault.md)

**What it covers:**
- Using gds_vault Python package
- Authentication strategies
- Retrieving and caching secrets
- Error handling patterns
- Best practices for applications
- Integration patterns

**When to read:**
- You're building an application that uses Vault
- You need to retrieve secrets in Python
- You want to implement caching
- You need to handle errors gracefully

**Prerequisites:** Read Concepts Guide first

---

### 4. **Reference Guide** (Lookup When Needed)

[reference/vault/README.md](../../reference/vault/README.md)

**What it covers:**
- gds_vault API reference
- Environment variables
- Configuration options
- Exception types
- Troubleshooting guide
- Common errors and solutions
- Glossary of terms

**When to read:**
- You're looking up a specific API or option
- You're troubleshooting an error
- You need to configure environment variables
- You're looking up terminology

**Prerequisites:** Concepts Guide

---

## Document Relationships

```
CONCEPTS GUIDE (Foundation)
    │
    ├─→ ARCHITECTURE GUIDE (Server & Security)
    │        │
    │        └─→ Production Hardening & Audit Logging
    │
    └─→ DEVELOPING GUIDE (Application Usage)
             │
             └─→ REFERENCE GUIDE (Lookup & Troubleshooting)
```

## Related Package Documentation

The `gds_vault` Python package has additional documentation in its source directory:

| Document | Purpose |
|:---|:---|
| [gds_vault/docs/DEVELOPERS_GUIDE.md](../../../python/gds_vault/docs/DEVELOPERS_GUIDE.md) | Complete API usage guide |
| [gds_vault/docs/BEGINNERS_GUIDE.md](../../../python/gds_vault/docs/BEGINNERS_GUIDE.md) | Learning Python through Vault |
| [gds_vault/docs/ROTATION_AWARE_TTL_GUIDE.md](../../../python/gds_vault/docs/ROTATION_AWARE_TTL_GUIDE.md) | Rotation-aware caching |

## Tutorials

See [docs/tutorials/gds-vault/](../../tutorials/gds-vault/README.md) for hands-on tutorials:

- [Learning Path](../../tutorials/gds-vault/gds-vault-learning-path.md) - Complete beginner to advanced
- [Vault Module Tutorial](../../tutorials/gds-vault/02-vault-module-tutorial.md) - Step-by-step walkthrough
- [Python Concepts](../../tutorials/gds-vault/05-gds-vault-python-concepts.md) - OOP patterns in gds_vault

## Getting Help

**Before asking for help, check:**

1. This README to find the right document
2. The relevant document's table of contents
3. Use Ctrl+F to search within the document
4. Check the [Troubleshooting Guide](../../reference/vault/troubleshooting.md)

**If you still need help:**
- Check the [Official HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- Ask your team's Vault/Infrastructure lead

## How We Keep Docs Updated

- **Concepts Guide:** Updated when fundamental Vault changes
- **Architecture Guide:** Updated when deployment standards change
- **Developing with gds_vault:** Updated with new patterns and best practices
- **Reference Guide:** Updated with each gds_vault release

Last update: January 15, 2026
