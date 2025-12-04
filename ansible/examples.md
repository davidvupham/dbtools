# Example: Using the role with different configurations

## Example 1: Production Environment

> **Note:** The default SQL Server instance service name is `MSSQLSERVER`. This is the standard configuration for Windows servers with a single SQL Server installation.

```yaml
---
- name: Configure SQL Server service account rights in production
  hosts: production
  roles:
    - windows_service_account_rights  # Uses default: service_name=MSSQLSERVER
```

## Example 2: All SQL Server Hosts (Using Parent Group)

> **Note:** The `sql_servers` parent group includes all environments (development, staging, production).

```yaml
---
- name: Configure SQL Server service account rights across all SQL Servers
  hosts: sql_servers
  roles:
    - windows_service_account_rights
```

## Example 3: All Environments (Development, Staging, Production)

```yaml
---
- name: Configure SQL Server service account rights across all environments
  hosts: development:staging:production
  roles:
    - windows_service_account_rights
```

## Example 3: Staging Environment with Specific Rights

```yaml
---
- name: Configure staging SQL Server with specific rights
  hosts: staging
  roles:
    - role: windows_service_account_rights
      vars:
        user_rights_to_grant:
          - SeServiceLogonRight
          - SeManageVolumePrivilege
          - SeLockMemoryPrivilege
```

## Example 4: Development Environment - Limited Rights

```yaml
---
- name: Configure development SQL Server with limited rights
  hosts: development
  roles:
    - role: windows_service_account_rights
      vars:
        user_rights_to_grant:
          - SeServiceLogonRight
          - SeManageVolumePrivilege
```

## Example 5: SQL Server Agent Across Environments

```yaml
---
- name: Configure SQL Server Agent service account
  hosts: development:staging:production
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: SQLSERVERAGENT
```

## Example 6: Environment-Specific Configuration

```yaml
---
- name: Configure SQL Server with environment-specific settings
  hosts: all
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: MSSQLSERVER
        user_rights_to_grant: >-
          {{
            ['SeServiceLogonRight', 'SeManageVolumePrivilege', 'SeLockMemoryPrivilege']
            if inventory_hostname in groups['production']
            else ['SeServiceLogonRight', 'SeManageVolumePrivilege']
          }}
```

## Example 7: Multiple Services in Production

```yaml
---
- name: Configure multiple SQL Server services in production
  hosts: production
  tasks:
    - name: Configure SQL Server default instance
      ansible.builtin.include_role:
        name: windows_service_account_rights
      vars:
        service_name: MSSQLSERVER

    - name: Configure SQL Server Agent
      ansible.builtin.include_role:
        name: windows_service_account_rights
      vars:
        service_name: SQLSERVERAGENT
```

---

## Advanced Examples

### Named SQL Server Instances (If Needed)

> **Note:** Named instances use the format `MSSQL$INSTANCENAME`. Most environments use only the default instance.

```yaml
---
- name: Configure SQL Server named instance in production
  hosts: production
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: "MSSQL$PRODUCTION"  # Named instance format
```

### Custom Windows Service Across Environments

```yaml
---
- name: Configure custom application service
  hosts: development:staging:production
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: MyCustomService
        user_rights_to_grant:
          - SeServiceLogonRight
```
