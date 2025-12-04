# Example: Using the role with different configurations

## Example 1: SQL Server Default Instance (Standard Usage)

> **Note:** The default SQL Server instance service name is `MSSQLSERVER`. This is the standard configuration for Windows servers with a single SQL Server installation.

```yaml
---
- name: Configure SQL Server service account rights
  hosts: sql_servers
  roles:
    - windows_service_account_rights  # Uses default: service_name=MSSQLSERVER
```

## Example 2: Grant Only Specific Rights

```yaml
---
- name: Grant only volume maintenance and lock pages rights
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        user_rights_to_grant:
          - SeManageVolumePrivilege
          - SeLockMemoryPrivilege
```

## Example 3: SQL Server Agent

```yaml
---
- name: Configure SQL Server Agent service account
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: SQLSERVERAGENT
```

## Example 4: Multiple Servers with Different Configurations

```yaml
---
- name: Configure SQL Server across multiple environments
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        # All servers use default instance MSSQLSERVER
        user_rights_to_grant:
          - SeServiceLogonRight
          - SeManageVolumePrivilege
          - SeLockMemoryPrivilege
```

## Example 5: Custom Windows Service

```yaml
---
- name: Configure custom application service
  hosts: windows_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: MyCustomService
        user_rights_to_grant:
          - SeServiceLogonRight
```

---

## Advanced Examples

### Named SQL Server Instances (If Needed)

> **Note:** Named instances use the format `MSSQL$INSTANCENAME`. Most environments use only the default instance.

```yaml
---
- name: Configure SQL Server named instance
  hosts: sql_servers
  roles:
    - role: windows_service_account_rights
      vars:
        service_name: "MSSQL$PRODUCTION"  # Named instance format
```

### Multiple Services on Same Host

```yaml
---
- name: Configure multiple services
  hosts: sql_servers
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
