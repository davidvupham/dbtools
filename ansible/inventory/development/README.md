# Development Environment Inventory

This directory contains the inventory for the **development** environment.

## Structure

```
development/
├── hosts.ini           # Host definitions
├── group_vars/
│   └── all.yml        # Variables for all hosts in this environment
└── host_vars/         # Host-specific variable overrides (optional)
```

## Usage

```bash
# Target development environment
ansible-playbook windows_service_account_rights.yml -i inventory/development -e "target_hosts=development"

# Test connectivity
ansible -i inventory/development development -m win_ping
```

## Adding Hosts

Edit `hosts.ini`:

```ini
[development]
sql-dev-01 ansible_host=192.168.1.10
sql-dev-02 ansible_host=192.168.1.11
sql-dev-03 ansible_host=192.168.1.12  # New host
```

## Host-Specific Variables

Create files in `host_vars/` for host-specific overrides:

```bash
# host_vars/sql-dev-01.yml
ansible_port: 5985  # Override for this specific host
```
