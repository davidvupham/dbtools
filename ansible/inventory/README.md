# Ansible Inventory Structure

This directory contains inventory files for managing Windows SQL Server hosts across different environments.

## Structure

```bash
inventory/
├── development/         # Development environment
│   ├── hosts.ini
│   ├── group_vars/
│   │   └── all.yml
│   ├── host_vars/
│   └── README.md
├── test/               # Test environment
│   ├── hosts.ini
│   ├── group_vars/
│   │   └── all.yml
│   ├── host_vars/
│   └── README.md
├── staging/            # Staging environment
│   ├── hosts.ini
│   ├── group_vars/
│   │   └── all.yml
│   ├── host_vars/
│   └── README.md
└── production/         # Production environment
    ├── hosts.ini
    ├── group_vars/
    │   └── all.yml
    ├── host_vars/
    └── README.md
```

## Environment Isolation

Each environment is completely isolated with its own:

- **hosts.ini**: Host definitions for that environment
- **group_vars/**: Environment-specific variables
- **host_vars/**: Host-specific variable overrides (optional)

This structure provides:

- ✅ Complete separation between environments
- ✅ Different credentials per environment
- ✅ Independent security controls
- ✅ No risk of cross-environment contamination

## Usage

### Target a Specific Environment

```bash
# Development
ansible-playbook windows_service_account_rights.yml -i inventory/development -e "target_hosts=windows"

# Test
ansible-playbook windows_service_account_rights.yml -i inventory/test -e "target_hosts=windows"

# Staging
ansible-playbook windows_service_account_rights.yml -i inventory/staging -e "target_hosts=windows"

# Production
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=windows"
```

### Test Connectivity

```bash
# Development
ansible -i inventory/development windows -m win_ping

# Production
ansible -i inventory/production windows -m win_ping
```

## Configuration Hierarchy

Variables are loaded in this order (later overrides earlier):

1. `group_vars/all.yml` - Applies to all hosts in the environment
2. `group_vars/<group_name>.yml` - Applies to specific group
3. `host_vars/<hostname>.yml` - Applies to specific host

### Example: Environment-Specific Settings

**development/group_vars/all.yml:**

```yaml
ansible_connection: winrm
ansible_port: 5985  # HTTP for dev
ansible_winrm_transport: basic
```

**production/group_vars/all.yml:**

```yaml
ansible_connection: winrm
ansible_port: 5986  # HTTPS for prod
ansible_winrm_transport: kerberos
```

### Example: Host-Specific Override

**production/host_vars/sql-prd-01.yml:**

```yaml
ansible_port: 5985  # This specific host uses different port
```

## Adding New Hosts

Edit the appropriate environment's `hosts.ini`:

```ini
# production/hosts.ini
[windows]
sql-prd-01 ansible_host=192.168.1.100
sql-prd-02 ansible_host=192.168.1.101
sql-prd-04 ansible_host=192.168.1.104  # New host

[linux]
app-prd-01 ansible_host=192.168.1.110

[production:children]
windows
linux
```

## Security Best Practices

### Development/Test

- Basic auth acceptable for convenience
- Passwords can be in plain text (not committed to git)

### Staging

- Use Kerberos or NTLM
- Consider using Ansible Vault for passwords

### Production

- **Always use Kerberos** when possible
- **Always use Ansible Vault** for sensitive data
- **Restrict file permissions** on production inventory
- **Audit access** to production credentials

### Using Ansible Vault

```bash
# Create encrypted vault file
ansible-vault create inventory/production/group_vars/vault.yml

# Edit encrypted vault file
ansible-vault edit inventory/production/group_vars/vault.yml

# Run playbook with vault password
ansible-playbook windows_service_account_rights.yml \
  -i inventory/production \
  -e "target_hosts=windows" \
  --ask-vault-pass
```

**vault.yml example:**

```yaml
vault_production_password: SecurePassword123!
vault_production_user: administrator@DOMAIN.COM
```

**all.yml reference:**

```yaml
ansible_user: "{{ vault_production_user }}"
ansible_password: "{{ vault_production_password }}"
```

## Environment-Specific Documentation

Each environment directory contains its own README with specific usage instructions:

- [development/README.md](development/README.md)
- [test/README.md](test/README.md)
- [staging/README.md](staging/README.md)
- [production/README.md](production/README.md)

## Migration from Flat Structure

If you have existing flat inventory files (dev.yml, prd.yml, etc.), they are deprecated. Use the directory structure instead for better organization and security.
