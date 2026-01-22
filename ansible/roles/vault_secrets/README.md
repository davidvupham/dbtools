# vault_secrets

Ansible role for retrieving secrets from HashiCorp Vault with support for multiple authentication methods.

## Requirements

- Ansible >= 2.14
- `community.hashi_vault` collection >= 6.0.0

Install the required collection:

```bash
ansible-galaxy collection install community.hashi_vault
```

## Supported authentication methods

| Method | Use Case | Required Variables |
|:-------|:---------|:-------------------|
| **AppRole** | Automation, CI/CD (recommended) | `vault_approle_role_id`, `vault_approle_secret_id` |
| **Token** | Development, testing | `vault_token` |
| **JWT** | CI/CD with OIDC | `vault_jwt`, `vault_jwt_role` |
| **Kubernetes** | Kubernetes workloads | `vault_kubernetes_role` |
| **LDAP** | Enterprise directory auth | `vault_username`, `vault_password` |
| **Userpass** | Simple username/password | `vault_username`, `vault_password` |

## Quick start

### 1. Set environment variables

```bash
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"
```

### 2. Use in a playbook

```yaml
- name: Retrieve secrets
  hosts: localhost
  vars:
    vault_auth_method: approle
    vault_secrets_to_fetch:
      - path: "myapp/database"
        key: "password"
        fact_name: "db_password"
  roles:
    - vault_secrets

  tasks:
    - name: Use the secret
      debug:
        msg: "Got password"
      when: db_password is defined
```

## Role variables

### Connection

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_addr` | `$VAULT_ADDR` | Vault server URL |
| `vault_namespace` | `""` | Vault namespace (Enterprise) |
| `vault_validate_certs` | `true` | Verify SSL certificates |
| `vault_timeout` | `30` | Connection timeout (seconds) |

### Authentication

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_auth_method` | `approle` | Authentication method |
| `vault_approle_role_id` | `$VAULT_ROLE_ID` | AppRole Role ID |
| `vault_approle_secret_id` | `$VAULT_SECRET_ID` | AppRole Secret ID |

### Secrets

| Variable | Default | Description |
|:---------|:--------|:------------|
| `vault_secrets_engine` | `kv-v2` | Secrets engine mount |
| `vault_kv_version` | `2` | KV engine version |
| `vault_secrets_to_fetch` | `[]` | List of secrets to retrieve |

## Secret retrieval format

```yaml
vault_secrets_to_fetch:
  - path: "myapp/database"    # Path in Vault
    key: "password"           # Specific key (optional)
    fact_name: "db_password"  # Fact name to store value
    engine: "kv-v2"           # Override engine (optional)
```

## Documentation

See the full documentation at: [docs/how-to/ansible/retrieve-secrets-from-vault.md](../../docs/how-to/ansible/retrieve-secrets-from-vault.md)

## Testing

Run unit tests:

```bash
cd tests && pytest
```

Run Ansible validation:

```bash
ansible-playbook tests/test_playbook.yml --check
```

## License

MIT
