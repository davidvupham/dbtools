# HashiCorp Vault Course

**[← Back to Courses Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Vault-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick-reference.md) | [Glossary](./glossary.md) | [Troubleshooting](./troubleshooting.md)

## Introduction

This comprehensive course takes you from secrets management fundamentals to production-ready HashiCorp Vault deployments. You learn by doing: every concept is reinforced with hands-on labs using local Docker environments.

### Who is this course for?

- **Developers** who need to securely manage application secrets
- **DevOps Engineers** implementing secrets automation in CI/CD pipelines
- **Platform Engineers** deploying and operating Vault in production
- **Security Engineers** designing secrets management strategies

### Core philosophy: Understand, then automate

1. **Phase 1 (Modules 1-2)**: Learn Vault fundamentals with a dev server
2. **Phase 2 (Module 3)**: Master dynamic secrets and advanced engines
3. **Phase 3 (Modules 4-5)**: Apply knowledge to real-world scenarios

## Course structure

```text
docs/courses/vault/
├── README.md                      # You are here (Navigation Hub)
├── quick-reference.md             # Common commands cheat sheet
├── glossary.md                    # Terminology definitions
├── troubleshooting.md             # Common issues and solutions
├── module-1-foundations/          # Beginner: Core concepts
│   ├── 01-introduction-to-secrets-management.md
│   ├── 02-vault-architecture.md
│   ├── 03-vault-dev-environment.md
│   ├── 04-secrets-engines-basics.md
│   ├── 05-vault-policies-intro.md
│   ├── project-1-password-manager.md
│   ├── quiz-module-1.md
│   ├── exercises/
│   └── solutions/
├── module-2-authentication/       # Intermediate: Auth & Access
│   ├── 06-token-authentication.md
│   ├── 07-approle-authentication.md
│   ├── 08-userpass-ldap-authentication.md
│   ├── 09-advanced-policies.md
│   ├── 10-entity-groups.md
│   ├── project-2-multi-user-store.md
│   ├── quiz-module-2.md
│   ├── exercises/
│   └── solutions/
├── module-3-dynamic-secrets/      # Advanced: Dynamic Secrets
│   ├── 11-dynamic-secrets-concepts.md
│   ├── 12-database-secrets-engine.md
│   ├── 13-aws-secrets-engine.md
│   ├── 14-pki-secrets-engine.md
│   ├── 15-transit-secrets-engine.md
│   ├── project-3-db-connection-manager.md
│   ├── quiz-module-3.md
│   ├── exercises/
│   └── solutions/
├── module-4-applied/              # Applied: Specialization Tracks
│   ├── track-a-python/            # Python integration with gds_vault
│   ├── track-b-infrastructure/    # Kubernetes, Terraform
│   └── track-c-operations/        # HA, monitoring, audit
├── module-5-capstone/             # Capstone Project
│   ├── project-5-capstone.md
│   └── evaluation-rubric.md
├── docker/                        # Lab infrastructure
│   ├── docker-compose.dev.yml
│   ├── docker-compose.ha.yml
│   └── vault-config/
└── scripts/                       # Setup and validation
```

## Learning paths

Choose the path that fits your goals and experience level.

### Recommended path (Beginner to Advanced)

*Best for: Users new to Vault or secrets management.*

| Module | Focus | Lessons |
|--------|-------|---------|
| [Module 1: Foundations](./module-1-foundations/README.md) | Core concepts, dev environment | 5 lessons |
| [Module 2: Authentication](./module-2-authentication/README.md) | Auth methods, policies, identity | 5 lessons |
| [Module 3: Dynamic Secrets](./module-3-dynamic-secrets/README.md) | Database, PKI, Transit engines | 5 lessons |
| [Module 4: Applied](./module-4-applied/README.md) | Choose your specialization track | 3 tracks |
| [Module 5: Capstone](./module-5-capstone/README.md) | End-to-end project | 1 project |

### Fast track (Experienced users)

*Best for: Users familiar with secrets management who need Vault-specific knowledge.*

1. Skim [Module 1](./module-1-foundations/README.md) for Vault-specific concepts
2. Complete [Module 2](./module-2-authentication/README.md) for authentication patterns
3. Jump to your track in [Module 4](./module-4-applied/README.md)

### DevOps track

*Best for: CI/CD pipeline integration and infrastructure automation.*

1. [Module 1](./module-1-foundations/README.md) (required)
2. [Module 2](./module-2-authentication/README.md) (focus on AppRole)
3. [Module 4 Track B](./module-4-applied/track-b-infrastructure/README.md) (Kubernetes, Terraform)

### Developer track

*Best for: Application developers integrating Vault into their code.*

1. [Module 1](./module-1-foundations/README.md) (required)
2. [Module 2](./module-2-authentication/README.md) (focus on tokens)
3. [Module 4 Track A](./module-4-applied/track-a-python/README.md) (Python with gds_vault)

## Prerequisites

### Required knowledge

- Basic command line / terminal usage
- Understanding of environment variables
- Familiarity with JSON and YAML formats

### Required software

- Docker or Podman
- `curl` or a REST client
- Text editor (VS Code recommended)
- Python 3.9+ (for Track A)

### Recommended (optional)

- Basic understanding of PKI/TLS certificates
- Familiarity with PostgreSQL
- Kubernetes experience (for Track B)

## Quick resources

| Resource | Description |
|----------|-------------|
| [Quick Reference](./quick-reference.md) | Common commands and patterns |
| [Glossary](./glossary.md) | Vault terminology definitions |
| [Troubleshooting](./troubleshooting.md) | Common issues and solutions |
| [gds_vault Library](../../tutorials/infrastructure/vault/README.md) | Python client library docs |

## Getting started

### 1. Set up your environment

```bash
# Navigate to course directory
cd docs/courses/vault

# Start dev Vault server
docker compose -f docker/docker-compose.dev.yml up -d

# Verify Vault is running
curl http://localhost:8200/v1/sys/health
```

### 2. Begin Module 1

Start with [01: Introduction to Secrets Management](./module-1-foundations/01-introduction-to-secrets-management.md).

## Assessment and certification

Each module includes:

- **Quiz**: Test your conceptual understanding
- **Exercises**: Hands-on skill practice
- **Project**: Apply knowledge to realistic scenarios

Complete all modules and the capstone project to demonstrate Vault proficiency.

## Help and support

- **Vault Issues**: Check [Troubleshooting](./troubleshooting.md)
- **Course Questions**: Contact the Global Data Services Team
- **Community**:
  - [HashiCorp Discuss](https://discuss.hashicorp.com/c/vault/)
  - [Vault GitHub Issues](https://github.com/hashicorp/vault/issues)

---

**Ready to start?** Begin with [Module 1: Foundations](./module-1-foundations/README.md).
