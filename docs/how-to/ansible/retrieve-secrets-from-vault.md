# Retrieve secrets from HashiCorp Vault in Ansible playbooks

**[← Back to Ansible How-To Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Ansible-blue)
![Topic](https://img.shields.io/badge/Topic-Vault-purple)

> [!IMPORTANT]
> **Related Docs:** [Documentation Standards](../../best-practices/documentation-standards.md) | [Vault Secrets Role README](../../../ansible/roles/vault_secrets/README.md)

## Table of contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Authentication methods](#authentication-methods)
  - [AppRole authentication (recommended)](#approle-authentication-recommended)
  - [JWT authentication (CI/CD pipelines)](#jwt-authentication-cicd-pipelines)
  - [Token authentication (development)](#token-authentication-development)
- [Basic usage](#basic-usage)
- [Integration patterns](#integration-patterns)
  - [Pattern 1: Pre-play secret retrieval](#pattern-1-pre-play-secret-retrieval)
  - [Pattern 2: Inline role inclusion](#pattern-2-inline-role-inclusion)
  - [Pattern 3: Direct lookup plugin](#pattern-3-direct-lookup-plugin)
- [Configuration reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)

## Overview

The `vault_secrets` Ansible role provides a reusable, secure way to retrieve secrets from HashiCorp Vault across all playbooks. It supports multiple authentication methods and follows HashiCorp's recommended security practices.

**Key features:**

- Multiple authentication methods (AppRole, JWT, Kubernetes, LDAP, Token)
- Automatic retry with exponential backoff
- Sensitive data protection with `no_log`
- Support for KV v1 and v2 secrets engines
- Environment variable integration for credentials

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

1. **Install the HashiCorp Vault Ansible collection:**

   ```bash
   ansible-galaxy collection install community.hashi_vault
   ```

   Or add to your `requirements.yml`:

   ```yaml
   collections:
     - name: community.hashi_vault
       version: ">=6.0.0"
   ```

2. **Configure Vault access** (choose one method):

   - **AppRole (recommended):** Obtain `role_id` and `secret_id` from your Vault administrator
   - **JWT:** Configure OIDC/JWT authentication in Vault for your CI/CD platform
   - **Token:** Generate a Vault token (development only)

3. **Set environment variables** (recommended approach):

   ```bash
   export VAULT_ADDR="https://vault.example.com:8200"
   export VAULT_ROLE_ID="your-role-id"
   export VAULT_SECRET_ID="your-secret-id"
   ```

[↑ Back to Table of Contents](#table-of-contents)

## Authentication methods

### AppRole authentication (recommended)

AppRole is the recommended method for automation and CI/CD pipelines. It uses a `role_id` (not secret) and `secret_id` (secret) pair.

> [!NOTE]
> The RoleID is not sensitive and can be embedded in configuration. The SecretID must be kept secret and should come from environment variables or a secure secrets store.

**Environment variables:**

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_ROLE_ID="db7a8f2c-1234-5678-9abc-def012345678"
export VAULT_SECRET_ID="your-secret-id-here"
```

**Playbook configuration:**

```yaml
vars:
  vault_auth_method: approle
  # Credentials loaded automatically from environment
```

### JWT authentication (CI/CD pipelines)

Use JWT authentication when running from CI/CD platforms like GitHub Actions, GitLab CI, or Azure DevOps that provide OIDC tokens.

**Environment variables:**

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_JWT="$CI_JOB_JWT"  # Platform-specific JWT token
```

**Playbook configuration:**

```yaml
vars:
  vault_auth_method: jwt
  vault_jwt_role: "ci-pipeline-role"
```

### Token authentication (development)

> [!WARNING]
> Token authentication is intended for development and testing only. Do not use static tokens in production.

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="hvs.your-dev-token"
```

```yaml
vars:
  vault_auth_method: token
```

[↑ Back to Table of Contents](#table-of-contents)

## Basic usage

### Step 1: Define secrets to retrieve

```yaml
vars:
  vault_secrets_to_fetch:
    - path: "myapp/database"        # Path in Vault (without engine prefix)
      key: "password"               # Specific key to extract (optional)
      fact_name: "db_password"      # Ansible fact name to store the value

    - path: "myapp/api-keys"
      fact_name: "api_keys"         # Without 'key', stores entire secret as dict
```

### Step 2: Include the role

```yaml
- name: Retrieve application secrets
  hosts: localhost
  gather_facts: false

  vars:
    vault_auth_method: approle
    vault_secrets_to_fetch:
      - path: "myapp/database"
        key: "password"
        fact_name: "db_password"

  roles:
    - vault_secrets

  tasks:
    - name: Use the retrieved secret
      ansible.builtin.debug:
        msg: "Password length: {{ db_password | length }}"
      no_log: true
```

### Step 3: Run the playbook

```bash
ansible-playbook my_playbook.yml -i inventory/development
```

[↑ Back to Table of Contents](#table-of-contents)

## Integration patterns

### Pattern 1: Pre-play secret retrieval

Fetch all secrets in a dedicated play, then use them in subsequent plays:

```yaml
---
# Play 1: Fetch secrets
- name: Retrieve secrets from Vault
  hosts: localhost
  gather_facts: false
  vars:
    vault_auth_method: approle
    vault_secrets_to_fetch:
      - path: "database/postgres"
        fact_name: "postgres_creds"

  roles:
    - vault_secrets

  post_tasks:
    - name: Share secrets with target hosts
      ansible.builtin.set_fact:
        db_credentials: "{{ postgres_creds }}"
      delegate_to: "{{ item }}"
      delegate_facts: true
      loop: "{{ groups['app_servers'] }}"
      no_log: true


# Play 2: Use secrets
- name: Configure application
  hosts: app_servers
  tasks:
    - name: Configure database connection
      ansible.builtin.template:
        src: database.conf.j2
        dest: /etc/myapp/database.conf
        mode: "0600"
      no_log: true
```

### Pattern 2: Inline role inclusion

Include the role within tasks for more control:

```yaml
- name: Application deployment
  hosts: app_servers
  tasks:
    - name: Fetch database credentials
      ansible.builtin.include_role:
        name: vault_secrets
      vars:
        vault_auth_method: approle
        vault_secrets_to_fetch:
          - path: "myapp/database"
            fact_name: "db_creds"

    - name: Deploy configuration
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/myapp/app.conf
      no_log: true
```

### Pattern 3: Direct lookup plugin

For simple cases, use the lookup plugin directly (requires a token):

```yaml
- name: Direct lookup example
  hosts: localhost
  tasks:
    - name: Fetch secret using lookup
      ansible.builtin.set_fact:
        my_secret: >-
          {{ lookup('community.hashi_vault.vault_kv2_get',
               'myapp/config',
               url=lookup('env', 'VAULT_ADDR'),
               token=lookup('env', 'VAULT_TOKEN'),
               engine_mount_point='kv-v2'
             ).secret.data }}
      no_log: true
```

[↑ Back to Table of Contents](#table-of-contents)

## Configuration reference

### Connection settings

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_addr` | `$VAULT_ADDR` | Vault server URL |
| `vault_namespace` | `$VAULT_NAMESPACE` | Vault namespace (Enterprise) |
| `vault_validate_certs` | `true` | Verify SSL certificates |
| `vault_ca_cert` | `""` | Path to CA certificate |
| `vault_timeout` | `30` | Connection timeout (seconds) |

### Authentication settings

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_auth_method` | `approle` | Auth method: approle, token, jwt, kubernetes, ldap, userpass |
| `vault_auth_mount_point` | `{{ vault_auth_method }}` | Auth method mount point |
| `vault_approle_role_id` | `$VAULT_ROLE_ID` | AppRole Role ID |
| `vault_approle_secret_id` | `$VAULT_SECRET_ID` | AppRole Secret ID |
| `vault_token` | `$VAULT_TOKEN` | Vault token |
| `vault_jwt` | `$VAULT_JWT` | JWT token |
| `vault_jwt_role` | `""` | JWT auth role name |

### Secret retrieval settings

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_secrets_engine` | `kv-v2` | Secrets engine mount point |
| `vault_kv_version` | `2` | KV engine version (1 or 2) |
| `vault_secrets_to_fetch` | `[]` | List of secrets to retrieve |
| `vault_missing_secret_behavior` | `fail` | Behavior when secret not found: fail or skip |

### Retry settings

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_retries` | `3` | Number of retry attempts |
| `vault_retry_delay` | `1` | Delay between retries (seconds) |

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Authentication failures

**Symptom:** `permission denied` or `invalid credentials`

**Solution:**

1. Verify environment variables are set:

   ```bash
   echo $VAULT_ADDR $VAULT_ROLE_ID
   ```

2. Test authentication manually:

   ```bash
   vault write auth/approle/login \
     role_id="$VAULT_ROLE_ID" \
     secret_id="$VAULT_SECRET_ID"
   ```

3. Check the auth mount point matches your Vault configuration.

### Secret not found

**Symptom:** `secret not found at path`

**Solution:**

1. Verify the path exists in Vault:

   ```bash
   vault kv get kv-v2/myapp/database
   ```

2. Check `vault_secrets_engine` matches your mount point.

3. For KV v2, ensure you're not including `/data/` in the path (the role adds it automatically).

### SSL certificate errors

**Symptom:** `certificate verify failed`

**Solution:**

1. Set `vault_validate_certs: false` for testing (not recommended for production).

2. Provide the CA certificate:

   ```yaml
   vault_ca_cert: "/etc/ssl/certs/vault-ca.pem"
   ```

### Timeout errors

**Symptom:** `connection timed out`

**Solution:**

1. Increase the timeout:

   ```yaml
   vault_timeout: 60
   ```

2. Increase retries:

   ```yaml
   vault_retries: 5
   vault_retry_delay: 2
   ```

[↑ Back to Table of Contents](#table-of-contents)
