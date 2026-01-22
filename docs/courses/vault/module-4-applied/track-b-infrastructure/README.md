# Track B: Infrastructure

**[← Back to Module 4](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Track overview

Learn to integrate Vault with infrastructure tools: Kubernetes, Terraform, and CI/CD systems.

## Lessons

| Lesson | Title | Topics |
|--------|-------|--------|
| 16 | Kubernetes Integration | Vault Agent, CSI driver, sidecar injection |
| 17 | Terraform Provider | Vault provider, dynamic secrets in IaC |
| 18 | CI/CD Patterns | GitHub Actions, Jenkins, secure pipelines |

## Prerequisites

- Kubernetes basics
- Terraform experience
- Completed Modules 1-3

## Key concepts

### Vault Agent Injector

```yaml
# Pod with Vault sidecar
apiVersion: v1
kind: Pod
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "myapp"
    vault.hashicorp.com/agent-inject-secret-db: "database/creds/app"
spec:
  serviceAccountName: myapp
  containers:
    - name: app
      # Secret at /vault/secrets/db
```

### Terraform Vault Provider

```hcl
provider "vault" {
  address = "https://vault.example.com:8200"
}

data "vault_generic_secret" "db" {
  path = "database/creds/app"
}

resource "kubernetes_secret" "db" {
  data = {
    username = data.vault_generic_secret.db.data["username"]
    password = data.vault_generic_secret.db.data["password"]
  }
}
```

---

[← Back to Module 4](../README.md)
