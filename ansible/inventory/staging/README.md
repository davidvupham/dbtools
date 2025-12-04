# Staging Environment Inventory

This directory contains the inventory for the **staging** environment.

## Structure

```
staging/
├── hosts.ini           # Host definitions
├── group_vars/
│   └── all.yml        # Variables for all hosts in this environment
└── host_vars/         # Host-specific variable overrides (optional)
```

## Usage

```bash
# Target staging environment
ansible-playbook windows_service_account_rights.yml -i inventory/staging -e "target_hosts=staging"

# Test connectivity
ansible -i inventory/staging staging -m win_ping
```
