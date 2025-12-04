# Test Environment Inventory

This directory contains the inventory for the **test** environment.

## Structure

```
test/
├── hosts.ini           # Host definitions
├── group_vars/
│   └── all.yml        # Variables for all hosts in this environment
└── host_vars/         # Host-specific variable overrides (optional)
```

## Usage

```bash
# Target test environment
ansible-playbook windows_service_account_rights.yml -i inventory/test -e "target_hosts=test"

# Test connectivity
ansible -i inventory/test test -m win_ping
```
