# Windows Service Account Rights

An Ansible role to retrieve the 'Log On As' account for a Windows service and grant it specific user rights assignments.

## Description

This role automates the process of:

1. Querying a Windows service to identify its service account
2. Adding or removing specific user rights assignments for the service account:
   - **SeServiceLogonRight**: Log on as a service
   - **SeManageVolumePrivilege**: Perform volume maintenance tasks
   - **SeLockMemoryPrivilege**: Lock pages in memory

This is particularly useful for SQL Server installations where these rights are required for optimal performance and functionality.

## Requirements

- Ansible 2.10 or higher
- `ansible.windows` collection installed
- Windows Server 2016 or higher
- WinRM configured on target Windows hosts
- Appropriate credentials with administrative privileges

## Role Variables

### Required Variables

None - the role uses sensible defaults.

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `service_name` | `MSSQLSERVER` | Name of the Windows service to query |
| `user_rights_action` | `add` | Action to perform: `add` or `remove` |
| `user_rights_to_grant` | See below | List of user rights to add/remove |
| `service_account_override` | `""` | Override auto-detection and specify account manually |

**Default `user_rights_to_grant`:**

```yaml
user_rights_to_grant:
  - SeServiceLogonRight
  - SeManageVolumePrivilege
  - SeLockMemoryPrivilege
```

## Dependencies

None

## Example Playbook

### Basic Usage (SQL Server Default Instance)

```yaml
---
- name: Configure SQL Server service account rights
  hosts: sql_servers
  roles:
    - windows_service_account_rights
```

### Custom Service Name

```yaml
---
- name: Configure custom service account rights
  hosts: windows_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: "MSSQL$INSTANCE01"
```

### Grant Specific Rights Only

```yaml
---
- name: Grant only volume maintenance rights
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: MSSQLSERVER
        user_rights_to_grant:
          - SeManageVolumePrivilege
          - SeLockMemoryPrivilege
```

### Named SQL Server Instance

```yaml
---
- name: Configure named SQL Server instance
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: "MSSQL$PROD"
```

### Remove User Rights

```yaml
---
- name: Remove user rights from service account
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: MSSQLSERVER
        user_rights_action: remove
        user_rights_to_grant:
          - SeManageVolumePrivilege
          - SeLockMemoryPrivilege
```

## User Rights Explained

### SeServiceLogonRight (Log on as a service)

Allows an account to log on as a service. This is typically already granted to service accounts but is included for completeness.

### SeManageVolumePrivilege (Perform volume maintenance tasks)

Enables instant file initialization for SQL Server, which can significantly improve performance when creating or growing database files.

### SeLockMemoryPrivilege (Lock pages in memory)

Prevents the operating system from paging SQL Server memory to disk, which can improve performance for systems with large amounts of memory.

## Notes

- The role will fail if the specified service does not exist
- The role will fail if the service runs as a built-in system account (LocalSystem, LocalService, NetworkService)
- The `user_rights_action` parameter controls whether rights are added or removed
- Default action is `add` - set to `remove` to revoke user rights
- Changes take effect immediately and do not require a service restart

## License

MIT

## Author Information

Created for the dbtools repository.
