# GDS.Windows Module

The `GDS.Windows` module provides PowerShell functions for managing Windows Operating System components, following DSC v3 principles with idempotent operations.

## Dependencies

| Module | Purpose | Install Command |
|--------|---------|-----------------|
| **Carbon** | User Rights management | `Install-Module Carbon -Force -Scope CurrentUser` |
| **Pester** | Unit testing (dev only) | `Install-Module Pester -Force -Scope CurrentUser` |

## Design Decisions

### Why Carbon Instead of SecurityPolicyDsc?

The `Set-GDSWindowsUserRight` function uses the [Carbon](https://get-carbon.org) module instead of DSC's `SecurityPolicyDsc` because:

1. **No WinRM Required**: `SecurityPolicyDsc` requires WinRM to be enabled and configured, even for local operations. Carbon works without WinRM.
2. **Idempotent**: Carbon's `Grant-CPrivilege` and `Revoke-CPrivilege` are idempotent—safe to run multiple times without errors or side effects.
3. **Cross-PowerShell**: Works in both PowerShell 5.1 and PowerShell 7.

This follows DSC v3 principles (declarative, idempotent) while avoiding WinRM dependencies.

---

## Functions

### `Enable-GDSWindowsRemoting`

Configures Windows Remote Management (WinRM) with HTTPS for secure remote access. **Idempotent**.

This function configures a Windows host for secure remote management by:
- Enabling the WinRM service
- Creating a WinRM HTTPS listener
- Configuring firewall rules for WinRM HTTPS (port 5986)
- Optionally enabling Basic Authentication, CredSSP, or Local Account Token Filter

**Syntax:**

```powershell
Enable-GDSWindowsRemoting [-ComputerName <String[]>] [-Credential <PSCredential>]
    [-CertificateThumbprint <String>]
    [-EnableBasicAuth] [-EnableCredSSP] [-EnableLocalAccountTokenFilter] [-LogToEventLog]
```

**Parameters:**

- `-ComputerName`: Computer names to configure. Defaults to `localhost`.
- `-Credential`: Credentials for remote execution.
- `-CertificateThumbprint`: Thumbprint of an existing certificate to use.

- `-EnableBasicAuth`: Enable Basic authentication (disabled by default).
- `-EnableCredSSP`: Enable CredSSP authentication.

**Examples:**

```powershell
# Configure with an existing certificate (Thumbprint optional if only one valid cert exists)
Enable-GDSWindowsRemoting -CertificateThumbprint "ABC123..."

# Configure locally using auto-detected valid certificate
Enable-GDSWindowsRemoting

# Enable Basic Auth (Legacy/Dev scenarios)
Enable-GDSWindowsRemoting -EnableBasicAuth
```

---

### `Set-GDSWindowsUserRight`

Sets a specific User Right (Privilege) for a given account. **Idempotent**.

**Syntax:**

```powershell
Set-GDSWindowsUserRight -UserRight <String[]> -ServiceAccount <String> [-Ensure <String>]
```

**Parameters:**

- `-UserRight`: The user right (friendly name or constant, e.g., `'Log on as a service'` or `'SeServiceLogonRight'`).
- `-ServiceAccount`: The account to configure (e.g., `DOMAIN\User`, `NT SERVICE\MSSQLSERVER`).
- `-Ensure`: `Present` (default) to grant, `Absent` to revoke.

**Examples:**

```powershell
# Grant "Log on as a service" (idempotent)
Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql'

# Revoke "Lock pages in memory"
Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure Absent

# Grant multiple rights
Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'
```

### `Set-GDSSqlServiceUserRights`

Wrapper to configure standard SQL Server service account rights. **Idempotent**.

**Syntax:**

```powershell
Set-GDSSqlServiceUserRights -ServiceAccount <String> [-ServiceName <String>] [-Ensure <String>]
```

**Examples:**

```powershell
# Set rights for a specific account
Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql'

# Auto-detect from MSSQLSERVER service
Set-GDSSqlServiceUserRights
```

### `Get-GDSUserRightPolicyState`

Determines if specific User Rights are managed by Group Policy.

```powershell
Get-GDSUserRightPolicyState -UserRight 'SeServiceLogonRight'
```

---

## Testing

```powershell
# Install Pester (if not already installed)
Install-Module Pester -Force -Scope CurrentUser
```

### Run All Module Tests

```powershell
Invoke-Pester -Path ./Powershell/Modules/GDS.Windows/tests/ -Output Detailed
```

### Test a Specific Function

```powershell
# Test Enable-GDSWindowsRemoting
Invoke-Pester -Path ./Powershell/Modules/GDS.Windows/tests/Enable-GDSWindowsRemoting.Tests.ps1 -Output Detailed

# Test Set-GDSWindowsUserRight
Invoke-Pester -Path ./Powershell/Modules/GDS.Windows/tests/Set-GDSWindowsUserRight.Tests.ps1 -Output Detailed
```

### Run Tests with Code Coverage

Code coverage measures what percentage of your code is executed during tests. It helps identify untested code paths.

```powershell
Invoke-Pester -Path ./Powershell/Modules/GDS.Windows/tests/ -CodeCoverage ./Powershell/Modules/GDS.Windows/Public/*.ps1
```

The output shows which lines were hit, missed, and the overall coverage percentage for each file.
