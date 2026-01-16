# Molecule testing for win_service_rights

**🔗 [← Back to Role Documentation](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 16, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

This document explains how to use Molecule to test the `win_service_rights` Ansible role.

## Table of contents

- [What is Molecule?](#what-is-molecule)
- [Why use Molecule for testing?](#why-use-molecule-for-testing)
- [Test scenarios](#test-scenarios)
- [Prerequisites](#prerequisites)
- [Running tests](#running-tests)
- [Test lifecycle](#test-lifecycle)
- [CI/CD integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## What is Molecule?

**Molecule** is the de facto standard framework for testing Ansible roles. It provides a consistent workflow for:

1. **Linting** - Static analysis of your Ansible code
2. **Syntax checking** - Validate YAML and Ansible syntax
3. **Provisioning** - Create test infrastructure (VMs, containers, or delegated hosts)
4. **Converging** - Apply your role to the test infrastructure
5. **Idempotence testing** - Run the role twice to verify no unnecessary changes
6. **Verification** - Assert the expected state was achieved
7. **Cleanup** - Remove test artifacts and restore original state

### How Molecule works

```
┌─────────────────────────────────────────────────────────────────┐
│                     Molecule Test Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DEPENDENCY    Install required Ansible collections           │
│        ↓                                                         │
│  2. LINT          Run ansible-lint and yamllint                  │
│        ↓                                                         │
│  3. SYNTAX        Validate playbook syntax                       │
│        ↓                                                         │
│  4. CREATE        Provision test infrastructure (delegated)      │
│        ↓                                                         │
│  5. PREPARE       Set up test prerequisites (accounts, services) │
│        ↓                                                         │
│  6. CONVERGE      Apply the role under test                      │
│        ↓                                                         │
│  7. IDEMPOTENCE   Re-run converge, expect no changes             │
│        ↓                                                         │
│  8. VERIFY        Assert expected state (user rights applied)    │
│        ↓                                                         │
│  9. CLEANUP       Remove test artifacts                          │
│        ↓                                                         │
│  10. DESTROY      Tear down test infrastructure                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Molecule with Windows (delegated driver)

Unlike Linux testing which typically uses Docker containers, Windows testing requires the **delegated driver**. This means:

- Molecule does not create/destroy the Windows hosts
- You provide pre-existing Windows servers
- Molecule connects via WinRM to run the tests
- Tests are fully automated once infrastructure is available

[↑ Back to Table of Contents](#table-of-contents)

## Why use Molecule for testing?

| Manual Testing | Molecule Testing |
|----------------|------------------|
| Inconsistent execution | Repeatable, identical every run |
| Easy to skip steps | All steps enforced |
| No CI/CD integration | Full CI/CD support |
| Results in documents | Results in logs/artifacts |
| Requires human verification | Automated assertions |
| Cleanup often forgotten | Automatic cleanup |

### Benefits for this role

1. **Verifies user rights are actually applied** - Uses `secedit` to confirm rights
2. **Tests error handling** - Validates failure on non-existent services
3. **Tests safety checks** - Confirms built-in account protection works
4. **Idempotence guarantee** - Ensures running twice doesn't break anything
5. **Supports both standalone and domain environments** - Two complete scenarios

[↑ Back to Table of Contents](#table-of-contents)

## Test scenarios

### WSL2-local scenario (recommended for development)

Tests from **RHEL in WSL2** against the **Windows 11 host** with real SQL Server.

```
┌─────────────────────────────────────────────────────────┐
│                    Windows 11 Host                       │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │    WSL2 (RHEL)  │    │    Windows Services         │ │
│  │  ┌───────────┐  │    │  - MSSQLSERVER              │ │
│  │  │  Ansible  │──┼────│  - SQLServerAgent           │ │
│  │  │  Molecule │  │    │  - SQL Server Browser       │ │
│  │  └───────────┘  │    └─────────────────────────────┘ │
│  └─────────────────┘              ▲                      │
│         └─────── WinRM (5986) ────┘                      │
└─────────────────────────────────────────────────────────┘
```

| Component | Description |
|-----------|-------------|
| Control node | RHEL in WSL2 on Windows 11 |
| Target | Windows 11 host (same machine) |
| Authentication | NTLM (local Windows account) |
| Test target | Real SQL Server services (MSSQLSERVER, etc.) |
| Fallback | Creates test service if SQL Server not found |

**When to use:** Local development, testing against real SQL Server, quick iteration.

### Standalone scenario

Tests against a **non-domain-joined Windows Server** using local accounts.

| Component | Description |
|-----------|-------------|
| Authentication | NTLM (local admin account) |
| Test account | Local user `MoleculeTestSvc` |
| Test service | `MoleculeTestService` (created during test) |
| Verified rights | SeServiceLogonRight, SeManageVolumePrivilege, SeLockMemoryPrivilege |

**When to use:** Testing against remote standalone servers, CI/CD with isolated Windows VMs.

### Domain scenario

Tests against a **domain-joined Windows Server** with Active Directory.

| Component | Description |
|-----------|-------------|
| Authentication | Kerberos (domain account) |
| Test account | Domain user `svc_molecule_test` (created in AD) |
| Test service | `MoleculeTestService` (created during test) |
| Hosts required | Domain controller + domain member server |
| Verified rights | SeServiceLogonRight, SeManageVolumePrivilege, SeLockMemoryPrivilege |

**When to use:** Production validation, testing domain account workflows, enterprise CI/CD pipelines.

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

### Install Molecule and dependencies

```bash
# Install Molecule with Windows support
pip install molecule ansible-lint yamllint pywinrm

# For Kerberos authentication (domain scenario)
pip install pywinrm[kerberos]
sudo apt-get install krb5-user libkrb5-dev  # Debian/Ubuntu
sudo dnf install krb5-workstation krb5-devel  # RHEL
```

### Install required Ansible collections

```bash
ansible-galaxy collection install -r molecule/requirements.yml
```

### Windows host requirements

**WSL2-local scenario:**
- Windows 11 with WSL2 and RHEL/Ubuntu installed
- WinRM enabled over HTTPS on Windows host (port 5986)
- Local Windows administrator account
- SQL Server installed (optional - creates test service if not found)

**Standalone scenario:**
- Windows Server 2016/2019/2022
- WinRM enabled over HTTPS (port 5986)
- Local administrator account
- Network connectivity from Ansible control node

**Domain scenario:**
- All standalone requirements, plus:
- Domain-joined Windows Server
- Domain Controller accessible
- Domain admin account (or delegated rights)
- Kerberos configured on Ansible control node

### Setting up WinRM on Windows 11 for WSL2 testing

Run these commands in an **elevated PowerShell** on your Windows 11 host:

```powershell
# Option 1: Quick setup with self-signed certificate (Development only)
$cert = New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My
winrm create winrm/config/Listener?Address=*+Transport=HTTPS "@{Hostname=`"$env:COMPUTERNAME`";CertificateThumbprint=`"$($cert.Thumbprint)`"}"

# Enable WinRM service
Enable-PSRemoting -Force

# Allow NTLM authentication
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $false
Set-Item -Path WSMan:\localhost\Service\Auth\Negotiate -Value $true

# Open firewall for WinRM HTTPS
New-NetFirewallRule -Name "WinRM-HTTPS" -DisplayName "WinRM over HTTPS" -Enabled True -Direction Inbound -Protocol TCP -LocalPort 5986 -Action Allow

# Verify listener is configured
winrm enumerate winrm/config/listener
```

```powershell
# Option 2: Using GDS.WindowsOS module (if available)
Import-Module GDS.WindowsOS
Enable-GDSWindowsRemoting -ForceNewSSLCert
```

**Test connectivity from WSL2:**

```bash
# Get Windows host IP
WIN_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Windows host IP: $WIN_HOST"

# Test port connectivity
nc -zv $WIN_HOST 5986

# Test with Ansible
ansible -i "$WIN_HOST," all -m win_ping \
  -e "ansible_connection=winrm" \
  -e "ansible_port=5986" \
  -e "ansible_winrm_scheme=https" \
  -e "ansible_winrm_transport=ntlm" \
  -e "ansible_winrm_server_cert_validation=ignore" \
  -e "ansible_user=YourWindowsUser" \
  -e "ansible_password=YourPassword"
```

[↑ Back to Table of Contents](#table-of-contents)

## Running tests

### WSL2-local scenario (recommended for development)

This scenario auto-detects the Windows host IP from WSL2.

```bash
# Set environment variables (Windows host IP is auto-detected)
export MOLECULE_WIN_USER="YourWindowsUsername"
export MOLECULE_WIN_PASSWORD="YourWindowsPassword"

# Run the full test suite
cd ansible/roles/win_service_rights
molecule test -s wsl2-local

# Or specify Windows host explicitly
export MOLECULE_WIN_HOST="$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')"
molecule test -s wsl2-local
```

**Important notes for WSL2-local:**
- Uses real SQL Server if installed (MSSQLSERVER, MSSQL$SQLEXPRESS, etc.)
- Falls back to creating a test service if SQL Server not found
- By default, does NOT remove rights from real SQL Server on cleanup
- To cleanup real SQL Server rights: `MOLECULE_CLEANUP_REAL=true molecule cleanup -s wsl2-local`

### Standalone scenario

```bash
# Set environment variables
export MOLECULE_WIN_HOST="192.168.1.100"        # Windows server IP/hostname
export MOLECULE_WIN_USER="Administrator"         # Local admin account
export MOLECULE_WIN_PASSWORD="YourPassword"      # Password

# Run the full test suite
cd ansible/roles/win_service_rights
molecule test -s standalone

# Or run individual steps
molecule converge -s standalone    # Just apply the role
molecule verify -s standalone      # Just run verification
molecule cleanup -s standalone     # Just run cleanup
```

### Domain scenario

```bash
# Obtain Kerberos ticket
kinit admin@CORP.EXAMPLE.COM

# Set environment variables
export MOLECULE_WIN_HOST="srv01.corp.example.com"    # Domain member FQDN
export MOLECULE_WIN_DOMAIN="CORP.EXAMPLE.COM"        # AD domain
export MOLECULE_WIN_USER="admin@CORP.EXAMPLE.COM"    # Domain admin UPN
export MOLECULE_DC_HOST="dc01.corp.example.com"      # Domain controller FQDN

# Run the full test suite
molecule test -s domain
```

### Run specific test phases

```bash
# Lint only (fast, no Windows required)
molecule lint -s standalone

# Syntax check only
molecule syntax -s standalone

# Converge and verify (skip cleanup for debugging)
molecule converge -s standalone
molecule verify -s standalone

# Interactive debugging - login to verify manually
molecule login -s standalone -h win-standalone-01

# Destroy/cleanup when done
molecule destroy -s standalone
```

[↑ Back to Table of Contents](#table-of-contents)

## Test lifecycle

### What each phase does

| Phase | File | Purpose |
|-------|------|---------|
| **prepare** | `prepare.yml` | Creates test service account and Windows service |
| **converge** | `converge.yml` | Applies the `win_service_rights` role |
| **verify** | `verify.yml` | Asserts user rights were applied correctly |
| **cleanup** | `cleanup.yml` | Removes test artifacts (account, service, rights) |

### Test assertions performed

The `verify.yml` playbook checks:

1. ✅ `SeServiceLogonRight` contains test account SID
2. ✅ `SeManageVolumePrivilege` contains test account SID
3. ✅ `SeLockMemoryPrivilege` contains test account SID
4. ✅ Role fails for non-existent service (error handling)
5. ✅ Role fails for built-in accounts (safety check)
6. ✅ `target_service_name` filtering works correctly (domain only)

[↑ Back to Table of Contents](#table-of-contents)

## CI/CD integration

### GitHub Actions example

```yaml
name: Test win_service_rights role

on:
  push:
    paths:
      - 'ansible/roles/win_service_rights/**'
  pull_request:
    paths:
      - 'ansible/roles/win_service_rights/**'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install molecule ansible-lint yamllint
      - name: Run linting
        run: |
          cd ansible/roles/win_service_rights
          molecule lint -s standalone

  test-standalone:
    runs-on: self-hosted  # Requires Windows access
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Run Molecule tests
        env:
          MOLECULE_WIN_HOST: ${{ secrets.WIN_TEST_HOST }}
          MOLECULE_WIN_USER: ${{ secrets.WIN_TEST_USER }}
          MOLECULE_WIN_PASSWORD: ${{ secrets.WIN_TEST_PASSWORD }}
        run: |
          cd ansible/roles/win_service_rights
          molecule test -s standalone
```

### Azure DevOps example

```yaml
trigger:
  paths:
    include:
      - ansible/roles/win_service_rights/**

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Lint
    jobs:
      - job: AnsibleLint
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'
          - script: |
              pip install molecule ansible-lint yamllint
              cd ansible/roles/win_service_rights
              molecule lint -s standalone
            displayName: 'Run ansible-lint'

  - stage: Test
    dependsOn: Lint
    jobs:
      - job: MoleculeTest
        pool: 'Windows-Test-Pool'  # Self-hosted pool with Windows access
        steps:
          - script: |
              cd ansible/roles/win_service_rights
              molecule test -s standalone
            displayName: 'Run Molecule tests'
            env:
              MOLECULE_WIN_HOST: $(WIN_TEST_HOST)
              MOLECULE_WIN_USER: $(WIN_TEST_USER)
              MOLECULE_WIN_PASSWORD: $(WIN_TEST_PASSWORD)
```

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Common issues

**WinRM connection refused:**
```bash
# Verify WinRM is listening
Test-NetConnection -ComputerName $host -Port 5986

# Check WinRM configuration on Windows
winrm enumerate winrm/config/listener
```

**Kerberos authentication failed:**
```bash
# Check your ticket
klist

# Renew if expired
kinit user@DOMAIN.COM

# Verify krb5.conf has correct realm
cat /etc/krb5.conf
```

**Test account creation failed:**
```
# Ensure you have permissions to create AD users
# Or adjust the test OU in prepare.yml
```

**Service creation failed:**
```powershell
# Check if service already exists
Get-Service MoleculeTestService

# Manually delete if stuck
sc.exe delete MoleculeTestService
```

### Debug mode

```bash
# Run with verbose output
molecule --debug test -s standalone

# Keep infrastructure after failure for debugging
molecule converge -s standalone
# ... inspect the Windows host ...
molecule destroy -s standalone
```

### View test logs

```bash
# Molecule logs are in the current directory
ls -la molecule/standalone/

# Ansible logs
cat ~/.ansible/log/ansible.log
```

[↑ Back to Table of Contents](#table-of-contents)
