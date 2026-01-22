# Capstone Project: Enterprise Secrets Platform

**[← Back to Module 5](./README.md)**

## Scenario

You are the lead architect for "TechCorp," a company with three development teams needing secure secrets management.

## Teams

- **Platform Team**: Manages infrastructure, needs access to all secrets
- **Backend Team**: Develops APIs, needs database and API credentials
- **Frontend Team**: Builds web apps, needs limited API credentials

## Requirements

### Phase 1: Foundation

- [ ] Deploy Vault cluster (single node for demo is acceptable)
- [ ] Configure TLS (self-signed OK)
- [ ] Set up audit logging

### Phase 2: Authentication

- [ ] Configure userpass for developers
- [ ] Configure AppRole for applications
- [ ] Create entities and groups for teams

### Phase 3: Secrets

- [ ] Set up KV engine for static secrets
- [ ] Configure database engine for PostgreSQL
- [ ] Set up Transit engine for app encryption

### Phase 4: Policies

- [ ] Team-specific access policies
- [ ] Templated policies for user workspaces
- [ ] Admin policy with full access

### Phase 5: Integration

- [ ] Python application using gds_vault
- [ ] CI/CD pipeline using AppRole
- [ ] Monitoring dashboard (optional)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      TECHCORP SECRETS PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                         VAULT CLUSTER                             │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │
│   │  │   KV v2     │  │  Database   │  │   Transit   │               │  │
│   │  │  (static)   │  │  (dynamic)  │  │ (encryption)│               │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘               │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                               │                                          │
│            ┌──────────────────┼──────────────────┐                      │
│            │                  │                  │                      │
│            ▼                  ▼                  ▼                      │
│   ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐              │
│   │ Platform Team   │ │Backend Team │ │ Frontend Team   │              │
│   │ (full access)   │ │ (db creds)  │ │ (api keys)      │              │
│   └─────────────────┘ └─────────────┘ └─────────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Deliverables

1. **docker-compose.yml** - Infrastructure setup
2. **policies/** - All HCL policy files
3. **scripts/** - Setup and demo scripts
4. **docs/** - Architecture documentation
5. **demo/** - Demo application code

## Evaluation

See [Evaluation Rubric](./evaluation-rubric.md)

---

[← Back to Module 5](./README.md) | [Evaluation Rubric →](./evaluation-rubric.md)
