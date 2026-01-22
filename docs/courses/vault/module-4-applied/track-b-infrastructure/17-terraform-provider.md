# Terraform provider

**[← Back to Track B: Infrastructure](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-17-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Configure the Terraform Vault provider for authentication
- Manage Vault resources (policies, auth methods, secrets engines) with Terraform
- Generate dynamic secrets for use in Terraform configurations
- Implement best practices for Vault infrastructure as code

## Table of contents

- [Provider configuration](#provider-configuration)
- [Managing Vault resources](#managing-vault-resources)
- [Dynamic secrets in Terraform](#dynamic-secrets-in-terraform)
- [Managing Kubernetes secrets](#managing-kubernetes-secrets)
- [Best practices](#best-practices)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Provider configuration

The Terraform Vault provider allows you to manage Vault configuration and consume secrets within your Terraform workflows.

### Basic provider setup

```hcl
# providers.tf
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
  }
}

provider "vault" {
  address = "https://vault.example.com:8200"

  # Authentication via token
  token = var.vault_token
}

variable "vault_token" {
  description = "Vault authentication token"
  type        = string
  sensitive   = true
}
```

### Authentication methods

The provider supports multiple authentication methods:

```hcl
# Token authentication (simplest, good for CI/CD)
provider "vault" {
  address = var.vault_address
  token   = var.vault_token
}

# AppRole authentication (recommended for automation)
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/approle/login"

    parameters = {
      role_id   = var.vault_role_id
      secret_id = var.vault_secret_id
    }
  }
}

# Kubernetes authentication (for K8s-based pipelines)
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/kubernetes/login"

    parameters = {
      role = "terraform"
      jwt  = file("/var/run/secrets/kubernetes.io/serviceaccount/token")
    }
  }
}

# AWS IAM authentication
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/aws/login"

    parameters = {
      role = "terraform-role"
    }
  }
}
```

### Environment variable configuration

```bash
# Set these environment variables instead of hardcoding
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="s.xxxxxxxxxxxxxxxx"

# Or for AppRole
export VAULT_ROLE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export VAULT_SECRET_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

```hcl
# Provider will use environment variables automatically
provider "vault" {
  # address and token read from VAULT_ADDR and VAULT_TOKEN
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Managing Vault resources

Terraform can manage the complete Vault configuration as code.

### Enabling secrets engines

```hcl
# Enable KV v2 secrets engine
resource "vault_mount" "kv" {
  path        = "secret"
  type        = "kv"
  description = "KV Version 2 secret engine"

  options = {
    version = "2"
  }
}

# Enable database secrets engine
resource "vault_mount" "database" {
  path        = "database"
  type        = "database"
  description = "Database dynamic credentials"
}

# Enable PKI secrets engine
resource "vault_mount" "pki" {
  path                      = "pki"
  type                      = "pki"
  description               = "PKI secrets engine"
  default_lease_ttl_seconds = 3600
  max_lease_ttl_seconds     = 86400
}
```

### Managing policies

```hcl
# Define a policy
resource "vault_policy" "app_read" {
  name = "app-read"

  policy = <<EOT
path "secret/data/app/*" {
  capabilities = ["read", "list"]
}

path "database/creds/app-role" {
  capabilities = ["read"]
}
EOT
}

# Policy from file
resource "vault_policy" "admin" {
  name   = "admin"
  policy = file("${path.module}/policies/admin.hcl")
}

# Dynamic policy using templatefile
resource "vault_policy" "team" {
  for_each = toset(["backend", "frontend", "platform"])

  name = "${each.key}-team"

  policy = templatefile("${path.module}/policies/team.hcl.tpl", {
    team_name = each.key
  })
}
```

**policies/team.hcl.tpl:**
```hcl
# Team-specific policy for ${team_name}
path "secret/data/${team_name}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/${team_name}/*" {
  capabilities = ["list", "read", "delete"]
}
```

### Configuring authentication methods

```hcl
# Enable AppRole auth
resource "vault_auth_backend" "approle" {
  type = "approle"
  path = "approle"
}

# Create an AppRole role
resource "vault_approle_auth_backend_role" "app" {
  backend        = vault_auth_backend.approle.path
  role_name      = "app-role"
  token_policies = ["app-read"]

  token_ttl     = 3600
  token_max_ttl = 14400

  secret_id_ttl         = 86400
  secret_id_num_uses    = 0
  token_num_uses        = 0
  bind_secret_id        = true
}

# Enable Kubernetes auth
resource "vault_auth_backend" "kubernetes" {
  type = "kubernetes"
  path = "kubernetes"
}

# Configure Kubernetes auth
resource "vault_kubernetes_auth_backend_config" "config" {
  backend            = vault_auth_backend.kubernetes.path
  kubernetes_host    = var.kubernetes_host
  kubernetes_ca_cert = var.kubernetes_ca_cert
}

# Create Kubernetes auth role
resource "vault_kubernetes_auth_backend_role" "app" {
  backend                          = vault_auth_backend.kubernetes.path
  role_name                        = "app-role"
  bound_service_account_names      = ["app-sa"]
  bound_service_account_namespaces = ["production"]
  token_policies                   = ["app-read"]
  token_ttl                        = 3600
}
```

### Managing secrets

```hcl
# Static KV secrets (be careful with state!)
resource "vault_kv_secret_v2" "app_config" {
  mount = vault_mount.kv.path
  name  = "app/config"

  data_json = jsonencode({
    environment = "production"
    log_level   = "info"
    # Don't store actual secrets here - they end up in state!
  })
}

# Database connection configuration
resource "vault_database_secret_backend_connection" "postgres" {
  backend       = vault_mount.database.path
  name          = "postgres"
  allowed_roles = ["app-role"]

  postgresql {
    connection_url = "postgresql://{{username}}:{{password}}@db.example.com:5432/mydb"
  }

  # Store the root password in Vault first, reference it here
  data = {
    username = "vault_admin"
    password = data.vault_kv_secret_v2.db_root.data["password"]
  }
}

# Database role for dynamic credentials
resource "vault_database_secret_backend_role" "app" {
  backend     = vault_mount.database.path
  name        = "app-role"
  db_name     = vault_database_secret_backend_connection.postgres.name

  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";",
  ]

  revocation_statements = [
    "REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM \"{{name}}\";",
    "DROP ROLE IF EXISTS \"{{name}}\";",
  ]

  default_ttl = 3600
  max_ttl     = 86400
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Dynamic secrets in Terraform

Use Vault to generate dynamic credentials for other Terraform providers.

### Database credentials for AWS RDS

```hcl
# Read dynamic database credentials from Vault
data "vault_database_credentials" "app" {
  backend = "database"
  role    = "app-role"
}

# Use credentials with PostgreSQL provider
provider "postgresql" {
  host     = "mydb.xxxxx.us-east-1.rds.amazonaws.com"
  port     = 5432
  database = "mydb"
  username = data.vault_database_credentials.app.username
  password = data.vault_database_credentials.app.password
}

# Create a table using dynamic credentials
resource "postgresql_schema" "app_schema" {
  name = "app"
}
```

### AWS credentials from Vault

```hcl
# Get dynamic AWS credentials from Vault
data "vault_aws_access_credentials" "creds" {
  backend = "aws"
  role    = "terraform-role"
  type    = "sts"
}

# Use the credentials with AWS provider
provider "aws" {
  region     = "us-east-1"
  access_key = data.vault_aws_access_credentials.creds.access_key
  secret_key = data.vault_aws_access_credentials.creds.secret_key
  token      = data.vault_aws_access_credentials.creds.security_token
}

# Now create AWS resources with dynamic credentials
resource "aws_s3_bucket" "app_data" {
  bucket = "my-app-data-bucket"
}
```

### PKI certificates

```hcl
# Generate a certificate from Vault PKI
data "vault_pki_secret_backend_cert" "app" {
  backend     = "pki"
  name        = "web-server"
  common_name = "app.example.com"
  alt_names   = ["www.app.example.com"]
  ttl         = "720h"
}

# Use the certificate in a Kubernetes secret
resource "kubernetes_secret" "app_tls" {
  metadata {
    name      = "app-tls"
    namespace = "production"
  }

  type = "kubernetes.io/tls"

  data = {
    "tls.crt" = data.vault_pki_secret_backend_cert.app.certificate
    "tls.key" = data.vault_pki_secret_backend_cert.app.private_key
  }
}
```

### Reading KV secrets

```hcl
# Read a secret from KV v2
data "vault_kv_secret_v2" "app_secrets" {
  mount = "secret"
  name  = "app/production"
}

# Use secret values in other resources
resource "kubernetes_secret" "app_config" {
  metadata {
    name      = "app-config"
    namespace = "production"
  }

  data = {
    api_key    = data.vault_kv_secret_v2.app_secrets.data["api_key"]
    secret_key = data.vault_kv_secret_v2.app_secrets.data["secret_key"]
  }
}

# Use with sensitive output
output "db_connection_string" {
  value     = data.vault_kv_secret_v2.app_secrets.data["database_url"]
  sensitive = true
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Managing Kubernetes secrets

A common pattern is using Terraform with Vault to provision Kubernetes secrets.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Terraform Workflow                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐                                                       │
│   │   Terraform     │                                                       │
│   │   Configuration │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│   │  Vault Provider │────▶│      Vault      │────▶│   K8s Provider  │      │
│   │  (read secrets) │     │   (source of    │     │  (create secret)│      │
│   └─────────────────┘     │     truth)      │     └────────┬────────┘      │
│                           └─────────────────┘              │                │
│                                                            ▼                │
│                                                   ┌─────────────────┐       │
│                                                   │   Kubernetes    │       │
│                                                   │    Secret       │       │
│                                                   └─────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Complete example

```hcl
# providers.tf
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/approle/login"
    parameters = {
      role_id   = var.vault_role_id
      secret_id = var.vault_secret_id
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  context     = var.kube_context
}
```

```hcl
# main.tf
# Read secrets from Vault
data "vault_kv_secret_v2" "db_creds" {
  mount = "secret"
  name  = "production/database"
}

data "vault_kv_secret_v2" "api_keys" {
  mount = "secret"
  name  = "production/api-keys"
}

# Create Kubernetes namespace
resource "kubernetes_namespace" "app" {
  metadata {
    name = "myapp"
  }
}

# Create Kubernetes secret from Vault data
resource "kubernetes_secret" "db_credentials" {
  metadata {
    name      = "db-credentials"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    username = data.vault_kv_secret_v2.db_creds.data["username"]
    password = data.vault_kv_secret_v2.db_creds.data["password"]
    host     = data.vault_kv_secret_v2.db_creds.data["host"]
  }
}

# Create ConfigMap with non-sensitive config
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "app-config"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    LOG_LEVEL   = "info"
    ENVIRONMENT = "production"
  }
}
```

### Using dynamic database credentials

```hcl
# Get dynamic credentials
data "vault_database_credentials" "app_db" {
  backend = "database"
  role    = "production-app"
}

# Create K8s secret with dynamic credentials
resource "kubernetes_secret" "dynamic_db_creds" {
  metadata {
    name      = "db-dynamic-creds"
    namespace = "myapp"
    annotations = {
      "vault.hashicorp.com/lease-id"         = data.vault_database_credentials.app_db.lease_id
      "vault.hashicorp.com/lease-duration"   = data.vault_database_credentials.app_db.lease_duration
      "vault.hashicorp.com/lease-renewable"  = data.vault_database_credentials.app_db.lease_renewable
    }
  }

  data = {
    username = data.vault_database_credentials.app_db.username
    password = data.vault_database_credentials.app_db.password
  }

  # Note: These credentials will expire based on the lease
  # Consider using Vault Agent Injector for automatic refresh
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Best practices

### State management

```hcl
# NEVER store sensitive values in Terraform state directly
# BAD - secret value in state
resource "vault_kv_secret_v2" "bad_example" {
  mount = "secret"
  name  = "app/config"
  data_json = jsonencode({
    password = "actual-password-here"  # This ends up in state!
  })
}

# GOOD - reference existing secrets, don't create them via Terraform
data "vault_kv_secret_v2" "existing" {
  mount = "secret"
  name  = "app/config"
}
```

### Token management

```hcl
# Use short-lived tokens with minimal permissions
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/approle/login"
    parameters = {
      role_id   = var.vault_role_id
      secret_id = var.vault_secret_id
    }
  }

  # Token will be renewable
  max_lease_ttl_seconds = 3600
}
```

### Workspace separation

```hcl
# Use different Vault paths per environment
locals {
  env_path = terraform.workspace == "production" ? "prod" : "dev"
}

data "vault_kv_secret_v2" "config" {
  mount = "secret"
  name  = "${local.env_path}/app/config"
}
```

### Secure CI/CD integration

```yaml
# .github/workflows/terraform.yml
jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: hashicorp/setup-terraform@v3

      - name: Configure Vault
        uses: hashicorp/vault-action@v3
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: approle
          roleId: ${{ secrets.VAULT_ROLE_ID }}
          secretId: ${{ secrets.VAULT_SECRET_ID }}
          secrets: |
            secret/data/terraform/aws access_key | AWS_ACCESS_KEY_ID ;
            secret/data/terraform/aws secret_key | AWS_SECRET_ACCESS_KEY

      - name: Terraform Apply
        run: terraform apply -auto-approve
        env:
          VAULT_ADDR: ${{ secrets.VAULT_ADDR }}
          VAULT_TOKEN: ${{ steps.vault.outputs.token }}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Terraform 1.0+
- Vault dev server running (from previous labs)
- Docker and Docker Compose

### Setup

```bash
# Start Vault dev server
docker run -d --name vault-dev \
    -p 8200:8200 \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
    hashicorp/vault:1.15

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Create a working directory
mkdir -p ~/vault-terraform-lab && cd ~/vault-terraform-lab
```

### Exercise 1: Configure Vault resources with Terraform

1. Create the Terraform configuration:

   ```bash
   cat > main.tf <<'EOF'
   terraform {
     required_providers {
       vault = {
         source  = "hashicorp/vault"
         version = "~> 4.0"
       }
     }
   }

   provider "vault" {
     address = "http://127.0.0.1:8200"
     token   = "root"
   }

   # Enable KV v2 secrets engine
   resource "vault_mount" "kv" {
     path        = "apps"
     type        = "kv"
     description = "Application secrets"
     options = {
       version = "2"
     }
   }

   # Create a policy
   resource "vault_policy" "app_read" {
     name = "app-read"
     policy = <<EOT
   path "apps/data/*" {
     capabilities = ["read", "list"]
   }
   EOT
   }

   # Enable AppRole auth
   resource "vault_auth_backend" "approle" {
     type = "approle"
   }

   # Create AppRole role
   resource "vault_approle_auth_backend_role" "app" {
     backend        = vault_auth_backend.approle.path
     role_name      = "app-role"
     token_policies = [vault_policy.app_read.name]
     token_ttl      = 3600
   }
   EOF
   ```

2. Initialize and apply:

   ```bash
   terraform init
   terraform plan
   terraform apply -auto-approve
   ```

3. Verify the resources were created:

   ```bash
   vault secrets list
   vault policy read app-read
   vault auth list
   ```

**Observation:** Vault is now configured entirely through Terraform code.

### Exercise 2: Read secrets with Terraform

1. First, create a secret manually:

   ```bash
   vault kv put apps/myapp/config \
       db_host="postgres.example.com" \
       db_user="appuser" \
       db_pass="secretpass123"
   ```

2. Add data source to read the secret:

   ```bash
   cat >> main.tf <<'EOF'

   # Read the secret we created
   data "vault_kv_secret_v2" "app_config" {
     mount = vault_mount.kv.path
     name  = "myapp/config"
   }

   # Output the values (marked sensitive)
   output "db_host" {
     value = data.vault_kv_secret_v2.app_config.data["db_host"]
   }

   output "db_credentials" {
     value = {
       username = data.vault_kv_secret_v2.app_config.data["db_user"]
       password = data.vault_kv_secret_v2.app_config.data["db_pass"]
     }
     sensitive = true
   }
   EOF
   ```

3. Apply and check outputs:

   ```bash
   terraform apply -auto-approve
   terraform output db_host
   terraform output -json db_credentials
   ```

**Observation:** Terraform can read secrets from Vault and use them in other resources.

### Exercise 3: Use AppRole for authentication

1. Get the AppRole credentials:

   ```bash
   # Get Role ID
   vault read auth/approle/role/app-role/role-id

   # Generate Secret ID
   vault write -f auth/approle/role/app-role/secret-id
   ```

2. Create a new configuration using AppRole:

   ```bash
   cat > approle-test.tf <<'EOF'
   terraform {
     required_providers {
       vault = {
         source  = "hashicorp/vault"
         version = "~> 4.0"
       }
     }
   }

   variable "role_id" {
     type = string
   }

   variable "secret_id" {
     type      = string
     sensitive = true
   }

   provider "vault" {
     address = "http://127.0.0.1:8200"

     auth_login {
       path = "auth/approle/login"
       parameters = {
         role_id   = var.role_id
         secret_id = var.secret_id
       }
     }
   }

   data "vault_kv_secret_v2" "test" {
     mount = "apps"
     name  = "myapp/config"
   }

   output "test_db_host" {
     value = data.vault_kv_secret_v2.test.data["db_host"]
   }
   EOF
   ```

3. Test with AppRole authentication:

   ```bash
   # Replace with actual values from step 1
   terraform init
   terraform apply -auto-approve \
       -var="role_id=YOUR_ROLE_ID" \
       -var="secret_id=YOUR_SECRET_ID"
   ```

**Observation:** Terraform authenticates to Vault using AppRole instead of root token.

### Cleanup

```bash
# Destroy Terraform resources
terraform destroy -auto-approve

# Stop Vault container
docker stop vault-dev && docker rm vault-dev

# Clean up files
cd ~ && rm -rf ~/vault-terraform-lab
```

---

## Key takeaways

1. **Infrastructure as Code** - Manage Vault configuration through version-controlled Terraform code
2. **Multiple auth methods** - Use AppRole or Kubernetes auth instead of static tokens in automation
3. **State security** - Never store actual secrets in Terraform; reference existing secrets instead
4. **Dynamic credentials** - Use Vault's dynamic secrets engines to provide short-lived credentials
5. **Provider chaining** - Vault provider can supply credentials to other Terraform providers
6. **Least privilege** - Create specific policies for Terraform operations with minimal permissions
7. **Environment separation** - Use Terraform workspaces or separate paths for different environments

---

[← Previous: Kubernetes Integration](./16-kubernetes-integration.md) | [Back to Track B: Infrastructure](./README.md) | [Next: CI/CD Patterns →](./18-cicd-patterns.md)
