# Test plan: Windows service account rights role

**🔗 [← Back to Ansible Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 16, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

This document describes how to validate the `win_service_rights` Ansible role.

The role's purpose is simple:

1. For each configured Windows service, determine which account the service runs under.
2. For that account, add/remove Windows User Rights Assignments.

The role supports multiple services per run via `win_service_rights_assignments`.

## Table of contents

- [Scope](#scope)
- [Role input](#role-input)
- [Test environment requirements](#test-environment-requirements)
- [Pre-test setup](#pre-test-setup)
- [How to run the tests](#how-to-run-the-tests)
- [Test cases](#test-cases)
- [Verification (Windows host)](#verification-windows-host)
- [Cleanup](#cleanup)
- [Known limitations](#known-limitations)
- [Test results template](#test-results-template)

## Scope

In-scope validation:

- Multiple services in one run
- One or more rights per service
- Grant (`state: present`) and revoke (`state: absent`)
- Error handling (missing service, built-in service accounts)
- Idempotency (running twice should be stable)

Out of scope:

- Functional testing of SQL Server / SQL Sentry / Ignite beyond verifying the rights were applied
- Hardening or policy decisions about *which* rights are "correct" for your organization

[↑ Back to Table of Contents](#table-of-contents)

## Role input

The role reads a list of assignments:

```yaml
win_service_rights_assignments:
  - service_name: MSSQLSERVER
    state: present        # present=grant, absent=revoke
    rights:
      - SeServiceLogonRight
      - SeManageVolumePrivilege
      - SeLockMemoryPrivilege
```

Per assignment:

- `service_name` (required): Windows service name (what `services.msc` shows in "Service name")
- `state` (optional): `present` or `absent` (defaults to `present`)
- `rights` (required): list of one or more user rights (e.g., `SeServiceLogonRight`)
- `service_account` (optional): override account to manage rights for (skips service lookup)
- `fail_on_builtin_account` (optional): defaults `true` and fails for LocalSystem/LocalService/NetworkService

[↑ Back to Table of Contents](#table-of-contents)

## Test environment requirements

### Control node (Linux)

- Ansible 2.10+
- `ansible.windows` collection installed
- Network access to Windows hosts over WinRM

### Target Windows hosts

- Windows Server 2016/2019/2022
- WinRM configured and reachable
- Administrative access available (rights assignment requires admin privileges)
- At least one of these services installed (or replace with services available in your environment): `MSSQLSERVER`, `SQLSentryServer`, `IgnitePl`

[↑ Back to Table of Contents](#table-of-contents)

## Pre-test setup

### 1) Install dependencies

```bash
cd ansible

pip install ansible
ansible-galaxy collection install ansible.windows
```

### 2) Configure test inventory

Edit `inventory/test/hosts.ini`:

```ini
[windows]
test-win-01 ansible_host=192.168.1.50
```

Ensure `inventory/test/group_vars/windows.yml` has correct WinRM connection settings.

### 3) Verify connectivity

```bash
ansible -i inventory/test windows -m win_ping
```

[↑ Back to Table of Contents](#table-of-contents)

## How to run the tests

Preferred method: create small, explicit test playbooks (easier than long `-e` overrides).

All example commands below assume you are in the `ansible/` directory.

## Test cases

### TC1: Default configuration (multi-service)

**Objective:** Validate the role runs with defaults and processes all configured services.

**Steps:**

```bash
ansible-playbook -i inventory/test playbooks/configure_win_service_rights.yml -e "target_hosts=windows"
```

**Expected results:**

- For each configured service, output shows the detected service account
- For each right, the module runs and reports changes as needed

### TC2: Grant rights for a single service (custom assignment)

**Objective:** Validate minimal input works (one service, one or more rights).

**Steps:** Create `test_single_service_present.yml`:

```yaml
---
- name: Test: single service present
  hosts: windows
  gather_facts: false
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: MSSQLSERVER
            state: present
            rights:
              - SeServiceLogonRight
```

Run:

```bash
ansible-playbook -i inventory/test test_single_service_present.yml
```

**Expected results:**

- Role completes successfully
- Rights are added if missing

### TC3: Revoke rights (state: absent)

**Objective:** Validate rights removal.

**Steps:** Create `test_single_service_absent.yml`:

```yaml
---
- name: Test: single service absent
  hosts: windows
  gather_facts: false
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

Run:

```bash
ansible-playbook -i inventory/test test_single_service_absent.yml
```

**Expected results:**

- Role completes successfully
- The listed rights are removed from the service account (if present)

### TC4: Service not found

**Objective:** Validate clear failure when a service does not exist.

**Steps:** Create `test_service_not_found.yml`:

```yaml
---
- name: Test: service not found
  hosts: windows
  gather_facts: false
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: NONEXISTENT_SERVICE
            state: present
            rights:
              - SeServiceLogonRight
```

Run:

```bash
ansible-playbook -i inventory/test test_service_not_found.yml
```

**Expected results:**

- Play fails with message indicating the service was not found

### TC5: Built-in service account safety check

**Objective:** Validate default safety: fail when service runs as LocalSystem/LocalService/NetworkService.

**Steps:** Create `test_builtin_account_fails.yml`:

```yaml
---
- name: Test: builtin service account fails
  hosts: windows
  gather_facts: false
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: W32Time
            state: present
            rights:
              - SeServiceLogonRight
```

Run:

```bash
ansible-playbook -i inventory/test test_builtin_account_fails.yml
```

**Expected results:**

- Play fails with a message explaining the service uses a built-in account

### TC6: Override service account (skip lookup)

**Objective:** Validate `service_account` override path.

**Steps:** Create `test_override_account.yml`:

```yaml
---
- name: Test: override service account
  hosts: windows
  gather_facts: false
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

Run:

```bash
ansible-playbook -i inventory/test test_override_account.yml
```

**Expected results:**

- Role completes successfully without querying the service
- Rights apply to the provided account

### TC7: Idempotency

**Objective:** Validate running twice is stable.

**Steps:** Run the same playbook twice (for example, TC2’s playbook):

```bash
ansible-playbook -i inventory/test test_single_service_present.yml
ansible-playbook -i inventory/test test_single_service_present.yml
```

**Expected results:**

- First run may report `changed=true`
- Second run should be `changed=false` (or minimal/no changes)

### TC8: Target specific service (filtering)

**Objective:** Validate that `target_service_name` strictly limits execution to that service.

**Steps:**

```bash
ansible-playbook -i inventory/test playbooks/configure_win_service_rights.yml \
  -e "target_hosts=windows target_service_name=SQLSentryServer"
```

**Expected results:**

- Role only processes `SQLSentryServer`
- Other configured services (e.g., MSSQLSERVER) are **ignored** (skipped)

### TC9: Force revoke via target_state

**Objective:** Validate that `target_state=absent` overrides the default `present` state.

**Steps:**

```bash
ansible-playbook -i inventory/test playbooks/configure_win_service_rights.yml \
  -e "target_hosts=windows target_service_name=SQLSentryServer target_state=absent"
```

**Expected results:**

- Rights for `SQLSentryServer` are revoked (state forced to absent)
- Output shows removal (or `ok` if already absent) for that specific service

### TC10: Bypass built-in account safety check

**Objective:** Validate that `fail_on_builtin_account: false` allows managing rights for built-in accounts.

**Steps:** Create `test_builtin_account_bypass.yml`:

```yaml
---
- name: Test: bypass builtin account safety check
  hosts: windows
  gather_facts: false
  roles:
    - role: win_service_rights
      vars:
        win_service_rights_assignments:
          - service_name: W32Time
            state: present
            fail_on_builtin_account: false
            rights:
              - SeServiceLogonRight
```

Run:

```bash
ansible-playbook -i inventory/test test_builtin_account_bypass.yml
```

**Expected results:**

- Role completes successfully (does not fail on built-in account)
- Rights are applied to the built-in account

[↑ Back to Table of Contents](#table-of-contents)

## Verification (Windows host)

### Verify with secedit

```powershell
# Run as Administrator
secedit /export /cfg C:\temp\secpol.cfg
Get-Content C:\temp\secpol.cfg | Select-String -Pattern "SeServiceLogonRight|SeManageVolumePrivilege|SeLockMemoryPrivilege"
```

### Verify with GUI

1. Run `secpol.msc`
2. Local Policies → User Rights Assignment
3. Confirm the service account is listed under the specified policies

[↑ Back to Table of Contents](#table-of-contents)

## Cleanup

Preferred cleanup is to run the role with `state: absent` for only the rights you added.

Example:

```yaml
win_service_rights_assignments:
  - service_name: MSSQLSERVER
    state: absent
    rights:
      - SeManageVolumePrivilege
      - SeLockMemoryPrivilege
```

[↑ Back to Table of Contents](#table-of-contents)

## Known limitations

1. Changes are immediate but some applications may need a service restart to observe them
2. Role requires administrative privileges on target hosts
3. Role does not validate other permissions the application might require (beyond user rights assignment)

[↑ Back to Table of Contents](#table-of-contents)

## Test results template

| Test Case | Date | Tester | Result | Notes |
| --------- | ---- | ------ | ------ | ----- |
| TC1: Default configuration | | | PASS/FAIL | |
| TC2: Single service present | | | PASS/FAIL | |
| TC3: Single service absent | | | PASS/FAIL | |
| TC4: Service not found | | | PASS/FAIL | |
| TC5: Built-in account fails | | | PASS/FAIL | |
| TC6: Override service account | | | PASS/FAIL | |
| TC7: Idempotency | | | PASS/FAIL | |
| TC8: Target specific service | | | PASS/FAIL | |
| TC9: Force revoke via target_state | | | PASS/FAIL | |
| TC10: Bypass built-in account check | | | PASS/FAIL | |

[↑ Back to Table of Contents](#table-of-contents)
