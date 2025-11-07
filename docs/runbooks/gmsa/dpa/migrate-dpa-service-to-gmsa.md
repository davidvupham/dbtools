# Migrate SolarWinds DPA Service Logon to a Group Managed Service Account

## Table of Contents

- [Summary](#summary)
- [Change Drivers](#change-drivers)
- [Preconditions](#preconditions)
- [Roles and Approvals](#roles-and-approvals)
- [Prerequisites](#prerequisites)
- [Pre-Execution Checklist](#pre-execution-checklist)
- [Execution Steps](#execution-steps)
  - [1. Verify gMSA Availability](#1-verify-gmsa-availability)
  - [2. Install gMSA on Target Server](#2-install-gmsa-on-target-server)
  - [3. Grant Filesystem Permissions (If Needed)](#3-grant-filesystem-permissions-if-needed)
  - [4. Update Service Logon Account](#4-update-service-logon-account)
  - [5. Register SPNs (If Required)](#5-register-spns-if-required)
- [Validation](#validation)
- [Rollback Plan](#rollback-plan)
- [Post-Change Tasks](#post-change-tasks)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Summary

Migrate the Windows service account used by SolarWinds Database Performance Analyzer (DPA) to a Group Managed Service Account (gMSA) to improve credential hygiene and satisfy security policy requirements.

- **Service name**: `SolarWindsDPAService`
- **Target hosts**: All DPA application servers (`<replace-with-hostnames>`)
- **Change window**: 30 minutes per host (includes validation and rollback buffer)

## Change Drivers

- Rotate static service credentials with automated gMSA password management.
- Enforce least privilege and eliminate manual password storage.
- Align with corporate identity governance policy for Tier-1 services.

## Preconditions

- Change request approved in the authoritative change management system.
- Downtime accepted: DPA service restart required.
- DPA application version supports gMSA authentication (2019.4 or later).

## Roles and Approvals

- **Change Owner**: DPA platform engineer.
- **Executing Engineer**: Windows systems administrator with local admin rights on each DPA host.
- **Approvers**: Identity management owner and DPA service owner.
- **Escalation**: Infra on-call → Identity on-call → DPA product owner.

## Prerequisites

1. **gMSA Provisioned in Active Directory**
   - Account name format: `svc_dpa_gmsa` (example). Includes trailing `$` in AD but not when referencing in PowerShell.
   - Host(s) joined to the security group allowed to retrieve gMSA keys.
   - SPN registered if DPA uses Kerberos to reach downstream databases.
2. **Windows Feature Support**
   - Windows Server 2012 or later with KB patches that enable gMSA.
   - PowerShell modules `ActiveDirectory` and `ADDSDeployment` installed on management workstation.
3. **Local Permissions**
   - Execute PowerShell as domain user with rights to install the gMSA on target servers.
   - Confirm `Log on as a service` local policy allows the gMSA (automatic when using `Set-Service` with gMSA on Server 2012 R2+).
4. **Backups and Snapshots**
   - Latest DPA configuration backup exported.
   - VM snapshot or backup checkpoint within the last 24 hours.

## Pre-Execution Checklist

- [ ] Notify stakeholders and on-call via agreed communications channel.
- [ ] Validate service health dashboard baseline status.
- [ ] Confirm gMSA replication using `Test-ADServiceAccount` from a management host.
- [ ] Document current service logon credentials for rollback (store securely).
- [ ] Schedule maintenance window and verify access to servers.

## Execution Steps

### 1. Verify gMSA Availability

Run on a management host or the target server:

```powershell
Import-Module ActiveDirectory
Test-ADServiceAccount -Identity svc_dpa_gmsa
```

Expected result is `True`. If `False`, remediate AD configuration (membership in the `PrincipalsAllowedToRetrieveManagedPassword` set, replication status, or domain connectivity) before continuing.

### 2. Install gMSA on Target Server

Execute on each DPA server:

```powershell
Add-WindowsFeature RSAT-AD-PowerShell -IncludeAllSubFeature
Install-ADServiceAccount -Identity svc_dpa_gmsa
```

If the feature is already present, PowerShell reports success without change.

### 3. Grant Filesystem Permissions (If Needed)

If DPA stores data outside `ProgramData`, grant the gMSA access:

```powershell
$paths = @(
    'C:\ProgramData\SolarWinds\DPA',
    'D:\SolarWinds\DPAData'              # update if custom path
)

foreach ($path in $paths) {
    icacls $path /grant "DOMAIN\svc_dpa_gmsa$:(OI)(CI)M" /T
}
```

Replace `DOMAIN` and verify the permissions align with security requirements (e.g., `RX` instead of `M` if appropriate).

### 4. Update Service Logon Account

Stop the DPA service, switch to the gMSA, and restart:

```powershell
$serviceName = 'SolarWindsDPAService'
$gmsa = 'DOMAIN\svc_dpa_gmsa$'

Stop-Service -Name $serviceName -Force
Set-Service -Name $serviceName -StartupType Automatic
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\$serviceName" -Name ObjectName -Value $gmsa
Start-Service -Name $serviceName
```

Alternatively, use the Services MMC: set Log On As to `DOMAIN\svc_dpa_gmsa$` leaving the password fields blank.

### 5. Register SPNs (If Required)

If DPA authenticates to SQL Server instances using Kerberos, ensure SPNs exist:

```powershell
setspn -S MSSQLSvc/sql-host.contoso.com:1433 DOMAIN\svc_dpa_gmsa$
```

Replace with actual database hosts and ports. Confirm duplicates are not reported.

## Validation

1. **Service State** – `Get-Service SolarWindsDPAService` returns `Running`.
2. **Event Viewer** – No new errors in `Application` or `System` logs referencing DPA startup or logon failures.
3. **DPA UI** – Log in to the web console, confirm monitored database instances show `Green` status.
4. **Task Scheduler Jobs** – Verify any scheduled tasks that reference the service account run successfully or update them to use the gMSA if applicable.
5. **Database Authentication** – Validate downstream database connections (Kerberos tickets if required) with DPA diagnostic tests.

Document validation outcomes in the change record.

## Rollback Plan

1. Stop the `SolarWindsDPAService` service.
2. Reconfigure the service logon to the previously documented account and password via Services MMC or PowerShell (`Set-Service` and registry `ObjectName`).
3. Restore original filesystem ACLs if they were tightened or relaxed for gMSA access.
4. Start the service and validate functionality using the same checks as above.
5. If issues persist, escalate per the escalation chain and provide logs.

## Post-Change Tasks

- Update inventory/CMDB entries to reflect the new service account.
- Close or update the change ticket with validation evidence.
- Monitor DPA health dashboard for 60 minutes for delayed failures.
- Schedule periodic review of gMSA group membership and SPNs.

## Troubleshooting

- **`Test-ADServiceAccount` fails** – Ensure the server is added to the gMSA's allowed principals group and replicate AD (`repadmin /syncall`).
- **Service fails to start with logon error 1069** – Confirm the `ObjectName` value includes the trailing `$` and no password is set. Check local security policy for `Log on as a service` rights.
- **Kerberos authentication failures** – Use `klist` to confirm tickets, validate SPNs, and flush cached tickets (`klist purge`).
- **Permission denied to DPA directories** – Reapply `icacls` grants or inherit default ACLs from parent directories.

## References

- [Microsoft gMSA Overview](https://learn.microsoft.com/windows-server/security/group-managed-service-accounts/overview)
- [SolarWinds DPA Administrator Guide](https://documentation.solarwinds.com/en/success_center/dpa/)
- Internal identity governance standards (`<link-to-internal-doc>`)
