# Ansible Playbooks for Windows Management

This directory contains Ansible playbooks and roles for managing Windows servers.

## Directory Structure

```
ansible/
├── ansible.cfg
├── windows_service_account_rights.yml
├── inventory/
│   ├── development/
│   │   ├── hosts.ini
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── host_vars/
│   ├── test/
│   │   ├── hosts.ini
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── host_vars/
│   ├── staging/
│   │   ├── hosts.ini
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── host_vars/
│   ├── production/
│   │   ├── hosts.ini
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── host_vars/
│   └── README.md
└── roles/
    └── windows_service_account_rights/
        ├── tasks/
        │   └── main.yml
        ├── defaults/
        │   └── main.yml
        ├── meta/
        │   └── main.yml
        └── README.md
```

## Prerequisites

### 1. Install Ansible and Required Collections

```bash
# Install Ansible
pip install ansible

# Install Windows collection
ansible-galaxy collection install ansible.windows
```

### 2. Configure Windows Hosts

Ensure your Windows hosts have WinRM configured. You can use the ConfigureRemotingForAnsible.ps1 script from the Ansible documentation:

```powershell
# On the Windows server (run as Administrator)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$url = "https://raw.githubusercontent.com/ansible/ansible-documentation/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"
(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
powershell.exe -ExecutionPolicy ByPass -File $file
```

### 3. Configure Kerberos Authentication (Recommended)

For domain-joined hosts, configure Kerberos on your Linux control node:

```bash
# Install Kerberos packages
sudo apt-get install python3-dev libkrb5-dev krb5-user

# Install Python Kerberos libraries
pip install pywinrm[kerberos]

# Configure /etc/krb5.conf with your domain settings
# Then obtain a Kerberos ticket
kinit user@DOMAIN.COM
```

## Quick Start

### 1. Update Inventory

The inventory is organized by environment directory. Each environment is completely isolated:

- `inventory/development/` - Development
- `inventory/test/` - Test
- `inventory/staging/` - Staging
- `inventory/production/` - Production

Edit the appropriate environment's `hosts.ini` file:

```ini
# inventory/production/hosts.ini
[production]
sql-prd-01 ansible_host=192.168.1.100
sql-prd-02 ansible_host=192.168.1.101
```

Connection settings are in each environment's `group_vars/all.yml`.

### 2. Run the Playbook

```bash
# Test connectivity (production)
ansible -i inventory/production production -m win_ping

# Run against production
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=production"

# Run against staging
ansible-playbook windows_service_account_rights.yml -i inventory/staging -e "target_hosts=staging"

# Run against development
ansible-playbook windows_service_account_rights.yml -i inventory/development -e "target_hosts=development"

# Run against test
ansible-playbook windows_service_account_rights.yml -i inventory/test -e "target_hosts=test"
```

### 3. Verify Results

On the Windows server, check the Local Security Policy:

1. Open `secpol.msc`
2. Navigate to Local Policies → User Rights Assignment
3. Verify the service account appears in:
   - Log on as a service
   - Perform volume maintenance tasks
   - Lock pages in memory

## Available Roles

### windows_service_account_rights

Retrieves the service account for a Windows service and grants it specific user rights assignments.

**Key Features:**

- Auto-detects service account from service configuration
- Grants Log on as a service, Perform volume maintenance tasks, and Lock pages in memory rights
- Configurable for any Windows service
- Includes validation and error handling

See [roles/windows_service_account_rights/README.md](roles/windows_service_account_rights/README.md) for detailed documentation.

## Common Use Cases

### SQL Server Default Instance (Production)

```bash
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=production"
```

### SQL Server Named Instance (Staging)

```bash
ansible-playbook windows_service_account_rights.yml -i inventory/staging -e "target_hosts=staging" -e "service_name=MSSQL\$INSTANCENAME"
```

### Remove User Rights (Production)

```bash
ansible-playbook windows_service_account_rights.yml -i inventory/production -e "target_hosts=production" -e "user_rights_action=remove"
```

### Grant Specific Rights Only (Development)

```bash
ansible-playbook windows_service_account_rights.yml -i inventory/development -e "target_hosts=development" -e '{"user_rights_to_grant": ["SeManageVolumePrivilege", "SeLockMemoryPrivilege"]}'
```

## Troubleshooting

### Connection Issues

```bash
# Test WinRM connectivity
ansible windows_servers -m win_ping -vvv

# Check Kerberos ticket
klist
```

### Permission Issues

Ensure your Ansible user has administrative privileges on the target Windows hosts.

### Service Not Found

Verify the service name:

```bash
# List all services on Windows host
ansible windows_servers -m ansible.windows.win_service_info
```

## Security Considerations

- Use Kerberos authentication for domain environments
- Store passwords in Ansible Vault, not plain text
- Use HTTPS (port 5986) for WinRM connections
- Enable certificate validation in production environments
- Follow the principle of least privilege for service accounts

## Additional Resources

- [Ansible Windows Documentation](https://docs.ansible.com/ansible/latest/os_guide/windows.html)
- [SQL Server User Rights Requirements](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-windows-service-accounts-and-permissions)
- [Windows User Rights Assignment](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/user-rights-assignment)
