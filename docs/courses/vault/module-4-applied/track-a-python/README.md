# Track A: Python Integration

**[← Back to Module 4](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Track overview

Learn to integrate Vault with Python applications using the `gds_vault` library.

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 16 | [gds_vault Library](./16-gds-vault-library.md) | VaultClient, configuration, basic usage |
| 17 | [Authentication Patterns](./17-authentication-patterns.md) | Token, AppRole, environment-based |
| 18 | [Caching and Retry](./18-caching-retry.md) | Secret caching, error handling |

## Prerequisites

- Python 3.9+
- `gds_vault` library installed
- Completed Modules 1-3

## Project

**[Track A Project: Vault-Enabled Application](./project-track-a.md)**

Build a Python application that securely retrieves and uses secrets from Vault.

## Getting started

```bash
# Install gds_vault
pip install gds_vault

# Or from monorepo
cd python/gds_vault && pip install -e .
```

---

[← Back to Module 4](../README.md) | [Start Lesson 16 →](./16-gds-vault-library.md)
