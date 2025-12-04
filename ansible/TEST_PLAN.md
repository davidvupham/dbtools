# Test Plan: Windows Service Account Rights Role

This document outlines the test plan for validating the `windows_service_account_rights` Ansible role.

## Test Environment Requirements

### Control Node (Linux)

- Ansible 2.10 or higher
- `ansible.windows` collection installed
- Python 3.8+
- Kerberos client configured (for Kerberos authentication)

### Target Windows Hosts

- Windows Server 2016, 2019, or 2022
- WinRM configured and enabled
- SQL Server installed (or another Windows service for testing)
- Administrative access available

## Pre-Test Setup

### 1. Install Dependencies on Control Node

```bash
# Install Ansible
pip install ansible

# Install Windows collection
ansible-galaxy collection install ansible.windows

# Install Kerberos support (if using Kerberos)
pip install pywinrm[kerberos]
```

### 2. Configure Test Inventory

Edit `inventory/test/hosts.ini` to include your test server:

```ini
# inventory/test/hosts.ini
[windows]
test-sql-01 ansible_host=192.168.1.50
```

Ensure `inventory/test/group_vars/windows.yml` has the correct connection settings.

### 3. Verify Connectivity

```bash
ansible -i inventory/test windows -m win_ping
```

## Test Cases

### Test Case 1: Basic Functionality - SQL Server Default Instance

**Objective:** Verify the role can retrieve the service account for MSSQLSERVER and grant all three user rights.

**Prerequisites:**

- SQL Server default instance (MSSQLSERVER) installed
- Service running under a domain or local user account (not LocalSystem)

**Steps:**

1. Run the playbook with default settings:

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test
   ```

**Expected Results:**

- Playbook executes without errors
- Service account is correctly identified
- All three user rights are granted:
  - SeServiceLogonRight
  - SeManageVolumePrivilege
  - SeLockMemoryPrivilege

**Verification:**

```powershell
# On Windows host, run as Administrator
# Check user rights assignments
secedit /export /cfg C:\temp\secpol.cfg
Get-Content C:\temp\secpol.cfg | Select-String -Pattern "SeServiceLogonRight|SeManageVolumePrivilege|SeLockMemoryPrivilege"
```

Or use GUI:

1. Open `secpol.msc`
2. Navigate to Local Policies → User Rights Assignment
3. Verify service account appears in all three policies

---

### Test Case 2: Named SQL Server Instance

**Objective:** Verify the role works with named SQL Server instances.

**Prerequisites:**

- Named SQL Server instance installed (e.g., MSSQL$PROD)

**Steps:**

1. Run with custom service name:

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test -e "service_name=MSSQL\$PROD"
   ```

**Expected Results:**

- Playbook executes successfully
- Correct service account identified for named instance
- User rights granted

**Verification:**
Same as Test Case 1

---

### Test Case 3: Selective User Rights

**Objective:** Verify the role can grant only specific user rights.

**Steps:**

1. Create a test playbook that grants only two rights:

   ```yaml
   ---
   - hosts: windows
     roles:
       - role: windows_service_account_rights
         vars:
           service_name: MSSQLSERVER
           user_rights_to_grant:
             - SeManageVolumePrivilege
             - SeLockMemoryPrivilege
   ```

2. Run the playbook:

   ```bash
   ansible-playbook test_selective_rights.yml -i inventory/test
   ```

**Expected Results:**

- Only specified rights are processed
- No errors occur

**Verification:**
Verify only the specified rights were granted (SeServiceLogonRight may already exist)

---

### Test Case 4: Service Not Found Error Handling

**Objective:** Verify the role fails gracefully when service doesn't exist.

**Steps:**

1. Run with non-existent service:

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test -e "service_name=NONEXISTENT_SERVICE"
   ```

**Expected Results:**

- Playbook fails with clear error message
- Error message indicates service not found

**Verification:**
Check Ansible output for failure message

---

### Test Case 5: Built-in System Account Error Handling

**Objective:** Verify the role fails appropriately when service runs as LocalSystem.

**Prerequisites:**

- A service configured to run as LocalSystem, LocalService, or NetworkService

**Steps:**

1. Run against a system service (e.g., Windows Time service):

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test -e "service_name=W32Time"
   ```

**Expected Results:**

- Playbook fails with clear error message
- Error indicates the service runs as a built-in system account

**Verification:**
Check Ansible output for appropriate failure message

---

### Test Case 6: Idempotency

**Objective:** Verify the role is idempotent (can be run multiple times without issues).

**Steps:**

1. Run the playbook twice in succession:

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test
   ```

**Expected Results:**

- First run: Changes made (changed=true)
- Second run: No changes (changed=false or minimal changes)
- Both runs complete successfully

**Verification:**
Compare Ansible output from both runs

---

### Test Case 7: Multiple Services

**Objective:** Verify the role can configure multiple services in one playbook run.

**Steps:**

1. Create a playbook for multiple services:

   ```yaml
   ---
   - hosts: windows
     tasks:
       - include_role:
           name: windows_service_account_rights
         vars:
           service_name: MSSQLSERVER

       - include_role:
           name: windows_service_account_rights
         vars:
           service_name: SQLSERVERAGENT
   ```

2. Run the playbook:

   ```bash
   ansible-playbook test_multiple_services.yml -i inventory/test
   ```

**Expected Results:**

- Both services processed successfully
- User rights granted for both service accounts

**Verification:**
Verify rights for both service accounts in Local Security Policy

---

### Test Case 8: Different Authentication Methods

**Objective:** Verify the role works with different WinRM authentication methods.

### Test 8a: Kerberos Authentication

```yaml
ansible_winrm_transport: kerberos
```

### Test 8b: NTLM Authentication

```yaml
ansible_winrm_transport: ntlm
ansible_user: administrator
ansible_password: "{{ vault_password }}"
```

### Test 8c: Basic Authentication (Dev/Test Only)

```yaml
ansible_port: 5985
ansible_winrm_transport: basic
ansible_user: administrator
ansible_password: YourPassword
```

**Expected Results:**

- Role works with all authentication methods
- No authentication-related errors

---

### Test Case 9: Domain vs Local Accounts

**Objective:** Verify the role works with both domain and local service accounts.

### Test 9a: Domain Account

- Service configured with domain account (DOMAIN\user)

### Test 9b: Local Account

- Service configured with local account (.\user or HOSTNAME\user)

**Expected Results:**

- Both account types handled correctly
- User rights granted appropriately

---

### Test Case 10: Verbose Output Validation

**Objective:** Verify debug output provides useful information.

**Steps:**

1. Run with verbose output:

   ```bash
   ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test -vv
   ```

**Expected Results:**

- Service account displayed in output
- Granted rights listed
- Clear progress indicators

---

## Manual Verification Checklist

After running the playbook, verify on the Windows host:

- [ ] Open Local Security Policy (`secpol.msc`)
- [ ] Navigate to Local Policies → User Rights Assignment
- [ ] Verify service account in "Log on as a service"
- [ ] Verify service account in "Perform volume maintenance tasks"
- [ ] Verify service account in "Lock pages in memory"
- [ ] Restart SQL Server service (optional, to verify no issues)
- [ ] Check SQL Server error log for instant file initialization message (if applicable)

## Performance Testing

### Test Case 11: Execution Time

**Objective:** Measure typical execution time.

**Steps:**

1. Run playbook and note execution time:

   ```bash
   time ansible-playbook windows_service_account_rights.yml -e "target_hosts=windows" -i inventory/test
   ```

**Expected Results:**

- Execution completes in under 30 seconds for single service
- No timeout errors

---

## Security Testing

### Test Case 12: Least Privilege Verification

**Objective:** Verify the role doesn't grant excessive permissions.

**Steps:**

1. Before running: Document current user rights for service account
2. Run the playbook
3. After running: Compare user rights

**Expected Results:**

- Only specified rights are added
- No additional unexpected rights granted
- Existing rights preserved

---

## Regression Testing

When making changes to the role, re-run:

- Test Case 1 (Basic functionality)
- Test Case 6 (Idempotency)
- Test Case 4 (Error handling)

## Test Environment Cleanup

After testing, optionally remove the granted rights:

```powershell
# On Windows host, run as Administrator
# Remove user rights (replace DOMAIN\user with actual account)
$account = "DOMAIN\sqlservice"

# Note: Be careful with this - only remove if you added them for testing
# secedit can be used, or use the GUI to remove manually
```

## Known Limitations

1. The role adds rights but does not remove them
2. Changes are immediate but may require service restart for some applications to recognize
3. Role requires administrative privileges on target hosts
4. Does not validate if the account has other required permissions

## Test Results Template

| Test Case | Date | Tester | Result | Notes |
|-----------|------|--------|--------|-------|
| TC1: Basic Functionality | | | PASS/FAIL | |
| TC2: Named Instance | | | PASS/FAIL | |
| TC3: Selective Rights | | | PASS/FAIL | |
| TC4: Service Not Found | | | PASS/FAIL | |
| TC5: System Account | | | PASS/FAIL | |
| TC6: Idempotency | | | PASS/FAIL | |
| TC7: Multiple Services | | | PASS/FAIL | |
| TC8: Authentication | | | PASS/FAIL | |
| TC9: Account Types | | | PASS/FAIL | |
| TC10: Verbose Output | | | PASS/FAIL | |
| TC11: Performance | | | PASS/FAIL | |
| TC12: Security | | | PASS/FAIL | |

## Automated Testing (Future Enhancement)

Consider implementing automated tests using:

- Molecule for role testing
- TestInfra for verification
- CI/CD pipeline integration

Example Molecule test structure:

```yaml
molecule/
  default/
    molecule.yml
    converge.yml
    verify.yml
```
