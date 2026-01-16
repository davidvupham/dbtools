# Windows service account rights (win_service_rights)

**🔗 [← Back to Ansible Index](../../README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 16, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

An Ansible role to retrieve the "Log On As" account for one or more Windows services and add/remove Windows user rights assignments for those accounts.

## Table of contents

- [Description](#description)
- [Requirements](#requirements)
- [Role variables](#role-variables)
- [Dependencies](#dependencies)
- [Example playbook](#example-playbook)
- [How to add additional services / rights](#how-to-add-additional-services--rights)
- [User rights explained](#user-rights-explained)
- [Notes](#notes)

## Description

This role automates the process of:

1. Querying Windows services to identify their service accounts (or using an explicit override)
2. Adding or removing user rights assignments for each service account

This is useful for SQL Server, monitoring agents, and any other service that runs under a domain/local user and needs specific privileges.

[↑ Back to Table of Contents](#table-of-contents)

## Requirements

- Ansible 2.10 or higher
- `ansible.windows` collection installed
- Windows Server 2016 or higher
- WinRM configured on target Windows hosts
- Appropriate credentials with administrative privileges

[↑ Back to Table of Contents](#table-of-contents)

## Role variables

### Required variables

You must provide (or accept the defaults for) `win_service_rights_assignments`.

### Primary variable: `win_service_rights_assignments`

This is a list of "assignments". Each assignment describes:

- which Windows service to look up (`service_name`)
- whether to grant or revoke rights (`state: present|absent`)
- which rights to manage (`rights` list)

```yaml
win_service_rights_assignments:
  - service_name: MSSQLSERVER
    state: present
    rights:
      - SeServiceLogonRight
      - SeManageVolumePrivilege
      - SeLockMemoryPrivilege
```

### Assignment fields

| Field | Required | Default | Description |
| ------ | -------- | ------- | ----------- |
| `service_name` | Yes | n/a | Windows service name (e.g., `MSSQLSERVER`, `SQLSentryServer`, `IgnitePl`) |
| `state` | No | `present` | `present` grants rights; `absent` removes rights |
| `rights` | Yes | n/a | One or more user rights to manage (e.g., `SeServiceLogonRight`) |
| `service_account` | No | empty | If set, skip auto-detection and manage rights for this account directly |
| `fail_on_builtin_account` | No | `true` | Fail if service runs as LocalSystem/LocalService/NetworkService |

[↑ Back to Table of Contents](#table-of-contents)

## Dependencies

None

## Example playbook

### Basic usage (defaults)

By default, the role is configured with these services:

- `MSSQLSERVER` (3 rights)
- `SQLSentryServer` (SeServiceLogonRight)
- `IgnitePl` (SeServiceLogonRight)

```yaml
---
- name: Configure service account user rights
  hosts: sql_servers
  roles:
    - win_service_rights
```

### Configure multiple services (recommended)

```yaml
---
- name: Configure multiple services in one run
  hosts: windows_servers
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            rights:
              - SeServiceLogonRight
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege

          - service_name: SQLSentryServer
            state: present
            rights:
              - SeServiceLogonRight

          - service_name: IgnitePl
            state: present
            rights:
              - SeServiceLogonRight
```

### Remove rights (state: absent)

```yaml
---
- name: Remove rights from a service account
  hosts: sql_servers
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: MSSQLSERVER
            state: absent
            rights:
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege
```

### Named SQL Server instance

```yaml
---
- name: Configure named SQL Server instance
  hosts: sql_servers
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: "MSSQL$PROD"
            state: present
            rights:
              - SeServiceLogonRight
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege
```

### Override the service account (skip auto-detection)

Use this when you want to manage rights for a specific account directly.

```yaml
---
- name: Override service account
  hosts: windows
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            service_account: "DOMAIN\\sqlsvc"
            rights:
              - SeServiceLogonRight
```

[↑ Back to Table of Contents](#table-of-contents)

## How to add additional services / rights

1. Identify the Windows service name:
   - Use `services.msc` on the host, or PowerShell: `Get-Service`.
2. Decide the desired `state`:
   - `present` to grant
   - `absent` to remove
3. Add an item under `win_service_rights_assignments`:

```yaml
win_service_rights_assignments:
  - service_name: MyCustomService
    state: present
    rights:
      - SeServiceLogonRight
```

[↑ Back to Table of Contents](#table-of-contents)

## User rights explained

### SeServiceLogonRight (Log on as a service)

Allows an account to log on as a service. This is typically already granted to service accounts but is included for completeness.

### SeManageVolumePrivilege (Perform volume maintenance tasks)

Enables instant file initialization for SQL Server, which can significantly improve performance when creating or growing database files.

### SeLockMemoryPrivilege (Lock pages in memory)

Prevents the operating system from paging SQL Server memory to disk, which can improve performance for systems with large amounts of memory.

[↑ Back to Table of Contents](#table-of-contents)

## Notes

- The role fails if a specified service does not exist (unless you provide `service_account` override)
- The role fails by default if the service runs as a built-in account (LocalSystem, LocalService, NetworkService)
  - Set `fail_on_builtin_account: false` per assignment to bypass this guard
- Changes take effect immediately and do not require a service restart

[↑ Back to Table of Contents](#table-of-contents)

## License

MIT

## Author information

Created for the dbtools repository.

[↑ Back to Table of Contents](#table-of-contents)
