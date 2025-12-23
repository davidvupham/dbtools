# Example: Using the role with different configurations

## Example 1: Production Environment

> **Note:** You can manage multiple services in one run using `windows_service_account_rights_assignments`.

```yaml
---
- name: Configure SQL Server service account rights in production
  hosts: windows
  roles:
    - windows_service_account_rights
```

## Example 2: All SQL Server Hosts (Using Parent Group)

> **Note:** The `sql_servers` parent group includes all environments (development, staging, production).

```yaml
---
- name: Configure SQL Server service account rights across all SQL Servers
  hosts: windows
  roles:
    - windows_service_account_rights
```

## Example 3: All Environments (Development, Staging, Production)

```yaml
---
- name: Configure SQL Server service account rights across all environments
  hosts: windows
  roles:
    - windows_service_account_rights
```

## Example 4: Staging Environment with Specific Rights

```yaml
---
- name: Configure staging SQL Server with specific rights
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            rights:
              - SeServiceLogonRight
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege
```

## Example 5: Development Environment - Limited Rights

```yaml
---
- name: Configure development SQL Server with limited rights
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            rights:
              - SeServiceLogonRight
              - SeManageVolumePrivilege
```

## Example 6: Additional Windows Service

```yaml
---
- name: Configure a custom application service
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MyCustomService
            state: present
            rights:
              - SeServiceLogonRight
```

## Example 7: Environment-Specific Configuration

```yaml
---
- name: Configure SQL Server with environment-specific settings
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            rights: >-
              {{
                ['SeServiceLogonRight', 'SeManageVolumePrivilege', 'SeLockMemoryPrivilege']
                if inventory_hostname in groups['production']
                else ['SeServiceLogonRight', 'SeManageVolumePrivilege']
              }}
```

## Example 8: Multiple Services in Production

```yaml
---
- name: Configure multiple SQL Server services in production
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
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

## Example 9: Remove User Rights

```yaml
---
- name: Remove user rights from SQL Server service account
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MSSQLSERVER
            state: absent
            rights:
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege
```

---

## Advanced Examples

### Named SQL Server Instances (If Needed)

> **Note:** Named instances use the format `MSSQL$INSTANCENAME`. Most environments use only the default instance.

```yaml
---
- name: Configure SQL Server named instance in production
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: "MSSQL$PRODUCTION"  # Named instance format
            state: present
            rights:
              - SeServiceLogonRight
              - SeManageVolumePrivilege
              - SeLockMemoryPrivilege
```

### Custom Windows Service Across Environments

```yaml
---
- name: Configure custom application service
  hosts: windows
  roles:
    - role: windows_service_account_rights
      vars:
        windows_service_account_rights_assignments:
          - service_name: MyCustomService
            state: present
            rights:
              - SeServiceLogonRight
```

---

## How to add additional services and rights

Add another item under `windows_service_account_rights_assignments`:

```yaml
windows_service_account_rights_assignments:
  - service_name: AnotherService
    state: present
    rights:
      - SeServiceLogonRight
      - SeLockMemoryPrivilege
```

To remove rights, change `state` to `absent`:

```yaml
windows_service_account_rights_assignments:
  - service_name: AnotherService
    state: absent
    rights:
      - SeLockMemoryPrivilege
```
