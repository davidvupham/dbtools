# Decision Log: AD Password Rotation

This document records key architectural and design decisions made during the project using the Architecture Decision Record (ADR) format.

---

## ADR-001: Use HashiCorp Vault for Secrets Management

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Security Team, Platform Team

### Context

We need a centralized secrets management solution to automate AD password rotation for database service accounts. Options considered:

1. **HashiCorp Vault** - Enterprise secrets management with native AD integration
2. **Azure Key Vault** - Cloud-native, integrates with Azure AD
3. **CyberArk** - Enterprise PAM solution
4. **Custom Scripts** - PowerShell-based rotation with secure storage

### Decision

**Use HashiCorp Vault** with the AD Secrets Engine.

### Rationale

| Criteria | Vault | Azure Key Vault | CyberArk | Custom |
|----------|-------|-----------------|----------|--------|
| Native AD rotation | ✅ Built-in | ❌ Manual | ✅ Built-in | ❌ Manual |
| Multi-cloud support | ✅ Yes | ⚠️ Azure-centric | ✅ Yes | ⚠️ Limited |
| Existing infrastructure | ✅ Already deployed | ❌ New service | ❌ New license | ✅ Existing |
| Learning curve | ⚠️ Moderate | ✅ Low | ⚠️ High | ✅ Low |
| Cost | ⚠️ Enterprise license | ⚠️ Per-secret cost | ❌ High | ✅ Free |

### Consequences

- **Positive:** Leverages existing Vault cluster; native AD integration reduces custom code
- **Negative:** Requires Vault expertise; adds dependency on Vault availability
- **Risks:** Vault downtime impacts all rotations (mitigated by HA cluster)

---

## ADR-002: Lazy Rotation vs Scheduled Rotation

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Platform Team, DBA Team

### Context

Vault's AD engine supports "lazy rotation" where passwords rotate on the next credential request after TTL expires. Alternative is scheduled rotation via external triggers.

### Decision

**Use lazy rotation** (Vault's default behavior) with 24-hour TTL.

### Rationale

- **Lazy rotation** ensures credentials are only rotated when actively needed
- Reduces unnecessary password changes for inactive accounts
- Aligns with Vault's operational model
- Manual rotation available via `vault write -f ad/rotate-role/<role>` for emergencies

### Consequences

- **Positive:** Simpler architecture; no external scheduler needed
- **Negative:** Rotation timing is unpredictable (depends on when credentials are requested)
- **Mitigation:** Document lazy rotation behavior clearly; train operations team

---

## ADR-003: Vault Agent for Credential Delivery

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Platform Team, Security Team

### Context

How should applications/services receive rotated credentials? Options:

1. **Vault Agent** - Sidecar/daemon that manages auth and renders secrets
2. **Direct API Calls** - Application calls Vault API directly
3. **Init Container** - Kubernetes pattern for one-time fetch
4. **External Secrets Operator** - Kubernetes-native sync to K8s Secrets

### Decision

**Use Vault Agent** as the primary delivery mechanism for VMs and bare metal. Use **sidecar pattern** for containers.

### Rationale

| Criteria | Vault Agent | Direct API | Init Container |
|----------|-------------|------------|----------------|
| Handles token renewal | ✅ Automatic | ❌ App must implement | ❌ One-time |
| Triggers on rotation | ✅ Template command | ❌ App must poll | ❌ No |
| Application changes | ✅ None (file-based) | ❌ Significant | ⚠️ Minimal |
| Works on VMs | ✅ Yes | ✅ Yes | ❌ K8s only |

### Consequences

- **Positive:** Applications don't need Vault SDK; consistent pattern across platforms
- **Negative:** Additional daemon to manage; restart scripts required
- **Risks:** Agent failure = stale credentials (mitigated by monitoring)

---

## ADR-004: AppRole for Machine Authentication

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Security Team

### Context

How should Vault Agent authenticate to Vault? Options:

1. **AppRole** - Role ID + Secret ID (machine identity)
2. **Kubernetes Auth** - Service Account token (K8s only)
3. **Azure Auth** - Managed Identity (Azure only)
4. **TLS Certificates** - mTLS with client certs
5. **Static Token** - Long-lived token (not recommended)

### Decision

**Use AppRole** for VMs/bare metal. Use **Kubernetes Auth** for K8s workloads if applicable.

### Rationale

- AppRole is purpose-built for machine authentication
- Role ID can be baked into images (less sensitive)
- Secret ID is short-lived and rotatable (monthly via GitHub Actions)
- Works across all platforms (Windows, Linux, containers)

### Consequences

- **Positive:** Secure, rotatable, platform-agnostic
- **Negative:** Requires Secret ID distribution mechanism
- **Mitigation:** GitHub Actions workflow for monthly Secret ID rotation

---

## ADR-005: GitHub Actions for CI/CD

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Platform Team, DevOps Team

### Context

How should Vault configuration changes be deployed? Options:

1. **GitHub Actions** - CI/CD for Terraform + scheduled jobs
2. **Azure DevOps** - Enterprise CI/CD
3. **Jenkins** - Self-hosted CI/CD
4. **Terraform Cloud** - Managed Terraform

### Decision

**Use GitHub Actions** with Terraform for Vault configuration management.

### Rationale

- Repository already hosted on GitHub
- Native Terraform integration via `hashicorp/setup-terraform` action
- Scheduled workflows for Secret ID rotation
- PR-based review workflow with plan output as comments
- GitHub OIDC available for token-free Vault auth

### Consequences

- **Positive:** GitOps workflow; audit trail in Git history
- **Negative:** GitHub Actions runners don't have direct access to AD
- **Scope:** GitHub Actions manages Vault config only; actual rotation handled by Vault

---

## ADR-006: TLS/LDAPS for AD Communication

**Date:** 2024-XX-XX
**Status:** Accepted
**Deciders:** Security Team, AD Team

### Context

How should Vault communicate with Active Directory?

1. **LDAPS (Port 636)** - LDAP over TLS
2. **LDAP + StartTLS (Port 389)** - Upgrade to TLS after connect
3. **LDAP (Port 389)** - Unencrypted (not recommended)

### Decision

**Use LDAPS only** (port 636) with certificate validation.

### Rationale

- Microsoft requires TLS for password change operations
- LDAPS is simpler than StartTLS (single encrypted connection)
- Certificate validation prevents MITM attacks
- `insecure_tls=false` enforced in Vault config

### Consequences

- **Positive:** All password data encrypted in transit
- **Negative:** Requires valid CA certificate in Vault config
- **Prerequisite:** AD team must provide CA certificate

---

## Decision Template

Copy this template for new decisions:

```markdown
## ADR-XXX: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded
**Deciders:** [Team/Individuals]

### Context

[What is the issue that we're seeing that is motivating this decision?]

### Decision

[What is the change that we're proposing and/or doing?]

### Rationale

[Why is this the best choice? What alternatives were considered?]

### Consequences

- **Positive:** [What becomes easier?]
- **Negative:** [What becomes harder?]
- **Risks:** [What could go wrong?]
```
