# Vault How-To Guides

**[← Back to Vault Documentation Index](../../explanation/vault/README.md)**

> **Last Updated:** January 15, 2026

This directory contains task-oriented how-to guides for HashiCorp Vault and the `gds_vault` Python package. Each guide focuses on accomplishing a specific task.

## Quick Navigation

| Guide | Purpose |
|:---|:---|
| [Operations Guide](./vault-operations-guide.md) | Day-to-day usage of gds_vault in applications |
| [Rotate AD Passwords](./rotate-ad-passwords.md) | Configure Vault to manage Active Directory passwords |

## Operations Guide

**[vault-operations-guide.md](./vault-operations-guide.md)**

Comprehensive guide for using Vault in your applications:

- Getting started with gds_vault
- Authentication patterns (AppRole, Token, Environment)
- Retrieving and caching secrets
- Error handling and retry patterns
- Integration patterns (FastAPI, workers)
- Best practices for security and performance

**Start here if:** You're building an application that needs to retrieve secrets from Vault.

## Rotate AD Passwords

**[rotate-ad-passwords.md](./rotate-ad-passwords.md)**

Configure HashiCorp Vault's Active Directory Secrets Engine to:

- Automatically rotate service account passwords
- Manage database service accounts (MSSQL, PostgreSQL, MongoDB)
- Configure policies and access control
- Handle Kerberos keytab considerations

**Start here if:** You need to automate AD password rotation for service accounts.

## Related Documentation

### Explanation (Understanding)

- [Vault Concepts Guide](../../explanation/vault/vault-concepts.md) - What is Vault, core concepts
- [Vault Architecture Guide](../../explanation/vault/vault-architecture.md) - Server architecture, security

### Reference (Lookup)

- [Vault Reference](../../reference/vault/vault-reference.md) - API reference, troubleshooting, glossary

### Tutorials (Learning)

- [Vault Learning Path](../../tutorials/gds-vault/gds-vault-learning-path.md) - Structured learning path
- [Vault Module Tutorial](../../tutorials/gds-vault/02-vault-module-tutorial.md) - Step-by-step walkthrough

### Package Documentation

- [gds_vault Developer's Guide](../../../python/gds_vault/docs/DEVELOPERS_GUIDE.md) - Complete API usage
- [gds_vault Beginner's Guide](../../../python/gds_vault/docs/BEGINNERS_GUIDE.md) - Python concepts explained
