# Migrate SolarWinds SQL Entry Service Logon to a Group Managed Service Account

## Table of Contents

- [Summary](#summary)
- [Change Drivers](#change-drivers)
- [Preconditions](#preconditions)
- [Roles and Approvals](#roles-and-approvals)
- [Prerequisites](#prerequisites)
- [Pre-Execution Checklist](#pre-execution-checklist)
- [Execution Steps](#execution-steps)
  - [1. Verify gMSA Functionality](#1-verify-gmsa-functionality)
  - [2. Install gMSA on Host](#2-install-gmsa-on-host)
  - [3. Update Filesystem and Registry Permissions](#3-update-filesystem-and-registry-permissions)
  - [4. Update Service Logon Accounts](#4-update-service-logon-accounts)
  - [5. Validate Scheduled Tasks or Jobs](#5-validate-scheduled-tasks-or-jobs)
  - [6. Register Required SPNs](#6-register-required-spns)
- [Validation](#validation)
- [Rollback Plan](#rollback-plan)
- [Post-Change Tasks](#post-change-tasks)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Summary

Transition the Windows services that power SolarWinds SQL Entry (also branded as SolarWinds SQL Sentry) to run under a Group Managed Service Account (gMSA) to remove static credentials and align with security policy.

- **Primary services**: `SQLSentryMonitoringService`, `SQLSentryPortalService` (confirm in Services console)
- **Target hosts**: SQL Entry application servers (`<replace-with-hostnames>`)
- **Estimated window**: 45 minutes per host, including validation and rollback buffer

## Change Drivers

- Replace expiring or manually rotated service account passwords with automatic gMSA rotation.
- Ensure compliance with corporate managed-identity control requirements.
- Reduce operational risk from credential exposure in configuration files or scheduled tasks.

## Preconditions

- Approved change record with documented scope and maintenance window.
- SQL Entry version 2021.6 or later (earlier versions may not honor gMSA permissions for the portal service).
- Application owners acknowledge the required service restart.

## Roles and Approvals

- **Change Owner**: SQL Entry product owner or delegate.
- **Executing Engineer**: Windows systems administrator with local admin rights.
- **Approvers**: Identity management owner + SQL Entry application owner.
- **Escalation Path**: Infra on-call → Identity on-call → SQL Entry product owner → Vendor support.

## Prerequisites

1. **Active Directory Preparation**
   - gMSA created (example: `svc_sqlentry_gmsa`).
   - Target servers added to the gMSA's `PrincipalsAllowedToRetrieveManagedPassword` set.
   - Service Principal Names registered if Kerberos is required for downstream resources (e.g., SQL Server, Analysis Services).
2. **Server Readiness**
   - Windows Server 2012 R2 or later with gMSA feature enabled.
   - RSAT Active Directory PowerShell tools installed (`Add-WindowsFeature RSAT-AD-PowerShell`).
3. **Application Backups**
   - Export SQL Entry configuration backup and note database connection strings.
   - Ensure database snapshots or backups within last 24 hours.
4. **Permissions Review**
   - Identify directories requiring write access (e.g., `C:\Program Files\SolarWinds\SQLSentry`, data folders, custom log paths).
   - Document current service account and password for rollback (stored in vault).

## Pre-Execution Checklist

- [ ] Notify stakeholders and on-call teams about the change window.
- [ ] Confirm no active maintenance jobs depend on the legacy service account.
- [ ] Validate gMSA replication via `Test-ADServiceAccount` from at least one target host.
- [ ] Capture current service configuration (`Get-WmiObject Win32_Service`).
- [ ] Confirm remote PowerShell or console access to each host.

## Execution Steps

### 1. Verify gMSA Functionality

```powershell
Import-Module ActiveDirectory
Test-ADServiceAccount -Identity svc_sqlentry_gmsa
```

Expect `True`. If `False`, remediate AD configuration before proceeding.

### 2. Install gMSA on Host

On each SQL Entry server:

```powershell
Add-WindowsFeature RSAT-AD-PowerShell -IncludeAllSubFeature
Install-ADServiceAccount -Identity svc_sqlentry_gmsa
```

If installation fails, ensure the host is domain-joined and included in the gMSA allowed principals group.

### 3. Update Filesystem and Registry Permissions

Grant the gMSA appropriate rights to application directories and registry keys:

```powershell
$account = 'DOMAIN\svc_sqlentry_gmsa$'
$paths = @(
    'C:\Program Files\SolarWinds\SQL Sentry',
    'C:\ProgramData\SolarWinds\SQLSentry',
    'D:\SQLSentryData'   # adjust for custom paths
)

foreach ($path in $paths) {
    icacls $path /grant "$account:(OI)(CI)M" /T
}

# Example registry grant for logging key
reg.exe add "HKLM\SOFTWARE\SolarWinds\SQLSentry" /v Placeholder /t REG_SZ /d temp /f
icacls "C:\Windows\System32\config\SOFTWARE" /grant "$account:RX"
```

Validate with security before applying broader permissions; adjust access levels as needed.

### 4. Update Service Logon Accounts

Repeat for each SQL Entry service (`SQLSentryMonitoringService`, `SQLSentryPortalService`, and any associated schedulers):

```powershell
$services = @('SQLSentryMonitoringService','SQLSentryPortalService')
$gmsa = 'DOMAIN\svc_sqlentry_gmsa$'

foreach ($svc in $services) {
    Stop-Service -Name $svc -Force
    Set-Service -Name $svc -StartupType Automatic
    Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\$svc" -Name ObjectName -Value $gmsa
    Start-Service -Name $svc
}
```

If Services MMC is preferred, set `Log On As` to the gMSA and leave password fields blank.

### 5. Validate Scheduled Tasks or Jobs

Some environments run SQL Entry maintenance via Task Scheduler. Update any tasks referencing the legacy account:

```powershell
Get-ScheduledTask | Where-Object { $_.Principal.UserId -like '*<legacy-account>*' } | Set-ScheduledTask -Principal (New-ScheduledTaskPrincipal -UserId 'DOMAIN\svc_sqlentry_gmsa$' -LogonType ServiceAccount -RunLevel Highest)
```

Replace `<legacy-account>` with the previous account name.

### 6. Register Required SPNs

If SQL Entry connects to SQL Server using Kerberos, register SPNs for the gMSA:

```powershell
setspn -S MSSQLSvc/sqlentry-db.contoso.com:1433 DOMAIN\svc_sqlentry_gmsa$
setspn -S HTTP/sqlentry-portal.contoso.com DOMAIN\svc_sqlentry_gmsa$
```

Adjust hostnames/ports to match your environment. Resolve duplicate SPN errors before continuing.

## Validation

1. **Service status** – `Get-Service SQLSentry*` shows `Running`.
2. **Application portal** – Log into SQL Entry web portal; confirm dashboard loads and data updates.
3. **Monitoring jobs** – Validate target SQL instances receive fresh performance data (review agent sync timestamp).
4. **Event Viewer** – Check `Application` and `System` logs for new errors or logon failures after restart.
5. **Kerberos** – Run `klist` to confirm tickets issued to the gMSA if Kerberos is used.

Record validation results in the change ticket.

## Rollback Plan

1. Stop all SQL Entry services.
2. Restore service logon to the previous account using Services MMC or PowerShell (`Set-ItemProperty ... -Value 'DOMAIN\legacy_svc'`).
3. Reapply original filesystem/registry ACLs if modified.
4. Restart services and confirm application health following the validation steps.
5. Document rollback and escalate if issues persist.

## Post-Change Tasks

- Update CMDB entries and service documentation to reflect gMSA usage.
- Communicate completion to stakeholders and close the change record with validation evidence.
- Monitor application health dashboards for at least 60 minutes post-change.
- Schedule quarterly review of gMSA group membership and SPNs.

## Troubleshooting

- **Service fails to start (Error 1069)** – Verify `ObjectName` includes trailing `$`, ensure gMSA is installed, confirm `Log on as a service` right applied (should update automatically on Server 2012 R2+).
- **Portal cannot authenticate to repository database** – Check connection strings, ensure SQL permissions granted to gMSA, validate Kerberos SPNs.
- **Permissions denied on custom paths** – Reapply `icacls` with required access; audit event logs to identify missing rights.
- **Scheduled tasks still running as legacy account** – Use `schtasks /query /v` to verify changes and edit affected tasks manually if automated update fails.
- **Test-ADServiceAccount returns False** – Confirm host is in the managed password group and domain controllers have replicated (`repadmin /syncall`).

## References

- [Microsoft: Group Managed Service Accounts Overview](https://learn.microsoft.com/windows-server/security/group-managed-service-accounts/overview)
- [SolarWinds SQL Sentry Installation and Configuration Guide](https://documentation.solarwinds.com/en/success_center/sqlsentry/)
- Internal identity governance standards (`<link-to-internal-doc>`)
