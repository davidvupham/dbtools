# Testing SecurityPolicyDsc with PowerShell 7

## Context

The `Set-GDSWindowsUserRight` function currently references `PSDscResources` for the `UserRightsAssignment` resource. However, **`PSDscResources` does NOT contain `UserRightsAssignment`**. The correct module is **`SecurityPolicyDsc`**.

This document provides steps to verify that `SecurityPolicyDsc` works with PowerShell 7 before updating the code.

## Prerequisites

- Windows Server or Windows 10/11
- PowerShell 7.x installed
- Administrator privileges

## Test Steps

### Step 1: Verify PowerShell Version

```powershell
$PSVersionTable.PSVersion
# Expected: Major version 7
```

### Step 2: Install SecurityPolicyDsc Module

```powershell
Install-Module -Name SecurityPolicyDsc -Force -Scope CurrentUser
```

### Step 3: Verify Module Installation

```powershell
Get-Module -ListAvailable -Name SecurityPolicyDsc
# Expected: Shows SecurityPolicyDsc module info
```

### Step 4: List Available DSC Resources

```powershell
Get-DscResource -Module SecurityPolicyDsc
# Expected: Should list UserRightsAssignment among others
```

### Step 5: Test Invoke-DscResource (Read-Only Test)

Use the `Get` method to test if `Invoke-DscResource` works with `SecurityPolicyDsc` in PS7:

```powershell
# Test reading current state (non-destructive)
Invoke-DscResource -Name UserRightsAssignment -ModuleName SecurityPolicyDsc -Method Get -Property @{
    Policy   = 'Log_on_as_a_service'
    Identity = 'NT SERVICE\MSSQLSERVER'
}
```

**Expected Result**: Returns an object with `Policy`, `Identity`, and current state. No error.

### Step 6: Test Set (Optional - Requires Admin)

> [!CAUTION]
> This will modify system settings. Only run if you understand the implications.

```powershell
# Grant "Log on as a service" to a test account
Invoke-DscResource -Name UserRightsAssignment -ModuleName SecurityPolicyDsc -Method Set -Property @{
    Policy   = 'Log_on_as_a_service'
    Identity = 'YOURDOMAINHERE\TestServiceAccount'
    Ensure   = 'Present'
}
```

## Expected Outcomes

| Step | Expected Result |
|------|-----------------|
| 1 | PowerShell 7.x |
| 2 | Module installs without error |
| 3 | Module listed |
| 4 | `UserRightsAssignment` resource listed |
| 5 | Returns object, no error |
| 6 | Sets right, no error (if run) |

## If Tests Pass

Update `Set-GDSWindowsUserRight.ps1` to:

1. Change module check from `PSDscResources` to `SecurityPolicyDsc`
2. Change `Invoke-DscResource` call to use `-ModuleName SecurityPolicyDsc`

## If Tests Fail

Document the error and consider:

1. Using PowerShell 5.1 compatibility mode
2. Using `secedit.exe` directly as a fallback
3. Using the Windows Security Policy COM objects

## Files to Update After Verification

- `PowerShell/Modules/GDS.Windows/Public/Set-GDSWindowsUserRight.ps1`
- `PowerShell/Modules/GDS.Windows/Public/Set-GDSSqlServiceUserRights.ps1`
- `PowerShell/Modules/GDS.Windows/README.md`
- `PowerShell/Modules/GDS.Windows/tests/Set-GDSWindowsUserRight.Tests.ps1`

## Conversation Context

This testing is part of validating the implementation of `Set-GDSWindowsUserRight`, a function that uses DSC v3 to set Windows User Rights (like "Log on as a service") for service accounts. The function was created to support SQL Server service account configuration.
