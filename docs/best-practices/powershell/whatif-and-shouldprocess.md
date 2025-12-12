# PowerShell Best Practices: WhatIf and ShouldProcess

The `-WhatIf` switch is a safety feature that lets users preview what a command *would* do without actually making changes. PowerShell provides built-in support through `SupportsShouldProcess`.

## The Problem: Destructive Operations

Commands that modify state (create files, stop services, change configurations) can cause problems if run accidentally. Users need a way to:
- Preview changes before committing them
- Confirm risky operations interactively

## The Solution: SupportsShouldProcess

Add `SupportsShouldProcess = $true` to your `[CmdletBinding()]` attribute:

```powershell
function Remove-OldLogs {
    [CmdletBinding(SupportsShouldProcess = $true)]
    Param(
        [string]$Path
    )

    $files = Get-ChildItem $Path -Filter "*.log"

    foreach ($file in $files) {
        # Guard every destructive action with ShouldProcess
        if ($PSCmdlet.ShouldProcess($file.FullName, "Delete file")) {
            Remove-Item $file.FullName
        }
    }
}
```

### How ShouldProcess Works

The `$PSCmdlet.ShouldProcess()` method returns:
- `$true` → Proceed with the action
- `$false` → Skip the action (user used `-WhatIf` or said "No" to `-Confirm`)

**Signature**: `ShouldProcess(Target, Action)`
- **Target**: What you're operating on (e.g., filename, service name)
- **Action**: What you're doing to it (e.g., "Delete", "Start", "Modify")

## Usage Examples

```powershell
# Preview mode - shows what would happen
Remove-OldLogs -Path "C:\Logs" -WhatIf

# Output:
# What if: Performing the operation "Delete file" on target "C:\Logs\app.log".
# What if: Performing the operation "Delete file" on target "C:\Logs\error.log".
```

```powershell
# Confirmation mode - prompts for each action
Remove-OldLogs -Path "C:\Logs" -Confirm

# Output:
# Confirm
# Are you sure you want to perform this action?
# Performing the operation "Delete file" on target "C:\Logs\app.log".
# [Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "Y"):
```

---

## Local vs Remote Execution

The `$PSCmdlet` object (which provides `ShouldProcess()`) is **only available in advanced functions**—not in script blocks. This creates challenges when:
1. You store configuration logic in a script block variable
2. You execute logic remotely via `Invoke-Command`

### Why ShouldProcess Doesn't Work in Script Blocks

```powershell
# THIS DOES NOT WORK
$ConfigScript = {
    # $PSCmdlet is null here - we're not in an advanced function!
    if ($PSCmdlet.ShouldProcess("Service", "Start")) {  # ERROR!
        Start-Service MyService
    }
}
```

The script block runs in isolation—it has no connection to the parent function's `$PSCmdlet`.

### The Solution: Pass WhatIf State Explicitly

#### Pattern for Local Script Block Execution

```powershell
function Set-LocalConfig {
    [CmdletBinding(SupportsShouldProcess = $true)]
    Param()

    $ConfigScript = {
        Param($WhatIfMode)  # Accept WhatIf state as parameter

        if ($WhatIfMode) {
            Write-Host "What if: Would start service 'MyService'"
        }
        else {
            Start-Service MyService
        }
    }

    # Pass $WhatIfPreference (set automatically when -WhatIf is used)
    & $ConfigScript -WhatIfMode:$WhatIfPreference
}
```

#### Pattern for Remote Execution (Invoke-Command)

```powershell
function Set-RemoteConfig {
    [CmdletBinding(SupportsShouldProcess = $true)]
    Param(
        [string[]]$ComputerName,
        [pscredential]$Credential
    )

    $ConfigScript = {
        Param($WhatIfMode)

        if ($WhatIfMode) {
            Write-Host "What if: Would restart service 'AppService' on $env:COMPUTERNAME"
        }
        else {
            Restart-Service -Name "AppService"
        }
    }

    $InvokeParams = @{
        ComputerName = $ComputerName
        ScriptBlock  = $ConfigScript
        ArgumentList = @($WhatIfPreference)  # Pass WhatIf state
    }

    if ($Credential) { $InvokeParams.Credential = $Credential }

    Invoke-Command @InvokeParams
}
```

### How WhatIf Flows Through the Call Stack

```
┌─────────────────────────────────────────────────────────────────┐
│  User calls: Enable-GDSWindowsRemoting -WhatIf                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PowerShell automatically sets:                                 │
│    $WhatIfPreference = $true                                    │
│    $PSCmdlet.ShouldProcess() returns $false                     │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│  LOCAL EXECUTION        │           │  REMOTE EXECUTION       │
│                         │           │                         │
│  & $ConfigScript        │           │  Invoke-Command         │
│    -WhatIfMode:$true    │           │    -ArgumentList $true  │
└─────────────────────────┘           └─────────────────────────┘
          │                                       │
          ▼                                       ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│  Script block checks:   │           │  Script block checks:   │
│  if ($WhatIfMode) {     │           │  if ($WhatIfMode) {     │
│    # Output preview     │           │    # Output preview     │
│  }                      │           │  }                      │
└─────────────────────────┘           └─────────────────────────┘
```

### Key Automatic Variables

| Variable | Set By | Value When `-WhatIf` Used |
|----------|--------|---------------------------|
| `$WhatIfPreference` | PowerShell | `$true` |
| `$ConfirmPreference` | PowerShell | Affects `-Confirm` behavior |
| `$PSCmdlet` | PowerShell | Available in advanced functions only |

### When to Use Each Approach

| Approach | Use When |
|----------|----------|
| `$PSCmdlet.ShouldProcess()` | Direct function code (not in script blocks) |
| `if ($WhatIfMode) { ... }` | Script blocks, `Invoke-Command`, stored scripts |

---

## Best Practices Checklist

1. **Guard every destructive action** with `ShouldProcess()` or `$WhatIfMode` check
2. **Use descriptive Target and Action strings** for clear WhatIf output
3. **For script blocks**, pass `$WhatIfPreference` as a parameter named `$WhatIfMode`
4. **Skip validations in WhatIf mode** (e.g., connection tests that require real changes)
5. **Combine with `-Verbose`** for comprehensive previews
6. **Use consistent WhatIf message format**: `"What if: Performing the operation 'Action' on target 'Target'."`

## Real-World Example

See [Enable-GDSWindowsRemoting.ps1](file:///c:/Users/david/OneDrive/Documents/GitHub/dbtools/Powershell/Modules/GDS.Windows/Public/Enable-GDSWindowsRemoting.ps1) for a production implementation that:
- Passes `$WhatIfPreference` to an internal script block
- Guards 9 state-changing operations (service, listener, auth, firewall)
- Handles both local (`& $ConfigScript`) and remote (`Invoke-Command`) execution
- Skips connection verification in WhatIf mode
