# Production Environment Inventory

This directory contains the inventory for the **production** environment.

## Structure

```
production/
├── hosts.ini           # Host definitions
├── group_vars/
│   └── all.yml        # Variables for all hosts in this environment
└── host_vars/         # Host-specific variable overrides (optional)
```

## Usage

```bash
# Target production environment
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=production"

# Test connectivity
ansible -i inventory/production production -m win_ping
```

## Security Notes

- **Use Ansible Vault** for sensitive data (passwords, API keys)
- **Restrict access** to this directory (production credentials)
- **Never commit** plain-text passwords to version control
- **Use Kerberos** authentication when possible

### Encrypting Sensitive Variables

```bash
# Create encrypted vault file
ansible-vault create inventory/production/group_vars/vault.yml

# Edit encrypted file
ansible-vault edit inventory/production/group_vars/vault.yml

# Run playbook with vault password
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=production" --ask-vault-pass
```
