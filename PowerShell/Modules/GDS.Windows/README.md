# GDS.Windows Module

The `GDS.Windows` module provides PowerShell functions for interacting with and managing Windows Operating System components, utilizing PowerShell DSC v3 resources where applicable.

## Functions

### `Set-GDSWindowsUserRight`

Sets a specific User Right (Privilege) for a given account using DSC v3 (`PSDscResources`).

**Syntax:**

```powershell
Set-GDSWindowsUserRight -UserRight <String[]> -ServiceAccount <String> [-Ensure <String>]
```

**Parameters:**

- `-UserRight`: The constant name of the user right (e.g., `SeServiceLogonRight`, `SeLockMemoryPrivilege`).
- `-ServiceAccount`: The account to configure (e.g., `DOMAIN\User`, `NT SERVICE\MSSQLSERVER`).
- `-Ensure`: `Present` (default) to grant the right, `Absent` to revoke it.

**Examples:**

```powershell
# Grant "Log on as a service" to a service account
Set-GDSWindowsUserRight -UserRight 'Log on as a service' -ServiceAccount 'CONTOSO\svc_sql'

# Revoke "Lock pages in memory"
Set-GDSWindowsUserRight -UserRight 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql' -Ensure Absent

# Grant multiple user rights (comma-separated string array)
Set-GDSWindowsUserRight -UserRight 'Log on as a service', 'Lock pages in memory' -ServiceAccount 'CONTOSO\svc_sql'

# Grant multiple user rights (using array variable)
$rights = @('Log on as a service', 'Log on as a batch job')
Set-GDSWindowsUserRight -UserRight $rights -ServiceAccount 'CONTOSO\svc_sql'
```

### `Set-GDSSqlServiceUserRights`

Wrapper function to configure standard SQL Server service account rights (Log on as a service, Lock pages in memory, Perform volume maintenance tasks).

**Syntax:**

```powershell
Set-GDSSqlServiceUserRights -ServiceAccount <String> [-ServiceName <String>] [-Ensure <String>]
```

**Parameters:**

- `-ServiceAccount`: The account to configure. If omitted, attempts to find the account from `-ServiceName`.
- `-ServiceName`: The service name to look up if `-ServiceAccount` is not provided (default: `MSSQLSERVER`).
- `-Ensure`: `Present` (default) or `Absent`.

**Examples:**

```powershell
# Set rights for a specific account
Set-GDSSqlServiceUserRights -ServiceAccount 'CONTOSO\svc_sql'

# Auto-detect account from default MSSQLSERVER service and set rights
Set-GDSSqlServiceUserRights
```

### `Get-GDSUserRightPolicyState`

Determines if specific User Rights are managed by Group Policy.

**Syntax:**

```powershell
Get-GDSUserRightPolicyState -UserRight <String[]>
```

---

## Testing

This module uses [Pester](https://pester.dev/) for unit testing. The tests mock the underlying system calls and DSC resource invocations to ensure logic correctness without modifying the system.

### Prerequisites

1. **Pester Module**: Ensure Pester 5+ is installed.

    ```powershell
    Install-Module Pester -Force -Scope CurrentUser
    ```

2. **PSDscResources**: The `Set-GDSWindowsUserRight` function depends on `PSDscResources`.

    ```powershell
    Install-Module PSDscResources -Force -Scope CurrentUser
    ```

### Running Tests

To run the tests for this module, execute the following command from the repository root or the module directory:

```powershell
# Run all tests in the GDS.Windows module
Invoke-Pester -Path ./PowerShell/Modules/GDS.Windows/tests/
```

Successful output will look like:

```text
Describing Set-GDSWindowsUserRight
  Context Parameters and Dependencies
    [+] Throws error if PSDscResources module is not available 24ms
  Context When calling Invoke-DscResource successfully
    [+] Calls Invoke-DscResource with correct arguments for Present 54ms
    [+] Calls Invoke-DscResource with correct arguments for Absent 18ms
```
