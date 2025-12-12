# PowerShell Best Practices: Error Handling

Robust error handling is essential for reliable PowerShell scripts. This document covers patterns for catching, handling, and communicating errors effectively.

## Understanding PowerShell Errors

PowerShell distinguishes between two types of errors:

| Error Type | Behavior | Caught by Try/Catch? |
|------------|----------|---------------------|
| **Terminating** | Stops pipeline execution | Yes |
| **Non-Terminating** | Reports error, continues pipeline | No (by default) |

Most cmdlet errors are **non-terminating** by default, which means `try/catch` blocks won't catch them unless you explicitly convert them.

## Core Best Practices

### Use `-ErrorAction Stop` for Trappable Exceptions

When calling cmdlets inside a `try` block, use `-ErrorAction Stop` to convert non-terminating errors into terminating ones:

```powershell
# BEST PRACTICE
function Test-Connection {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string[]]$ComputerName
    )

    foreach ($Computer in $ComputerName) {
        try {
            Test-WSMan -ComputerName $Computer -ErrorAction Stop
            Write-Host "Connected to $Computer" -ForegroundColor Green
        }
        catch {
            Write-Warning "Unable to connect to: $Computer"
        }
    }
}
```

```powershell
# ANTI-PATTERN - catch block never executes
try {
    Test-WSMan -ComputerName "UnreachableServer"  # Non-terminating error
}
catch {
    Write-Warning "This never runs!"  # Unreachable code
}
```

### Set `$ErrorActionPreference` for Non-Cmdlets

When calling .NET methods or external tools that don't support `-ErrorAction`, set `$ErrorActionPreference` locally:

```powershell
function Invoke-DotNetOperation {
    [CmdletBinding()]
    param()

    # Save and set preference
    $originalEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Stop'

    try {
        [System.IO.File]::ReadAllText("C:\NonExistent.txt")
    }
    catch {
        Write-Warning "File operation failed: $_"
    }
    finally {
        # Always restore
        $ErrorActionPreference = $originalEAP
    }
}
```

> [!CAUTION]
> Never modify `$ErrorActionPreference` at the global scope. Always save and restore the original value.

### Put the Entire Transaction in Try Block

Avoid using flags to handle errors. Put all dependent operations in the same try block:

```powershell
# ANTI-PATTERN - flag-based error handling
try {
    $continue = $true
    Connect-Database -ErrorAction Stop
}
catch {
    $continue = $false
}

if ($continue) {
    Get-Data
    Process-Data
    Save-Results
}
```

```powershell
# BEST PRACTICE - transaction in try block
try {
    Connect-Database -ErrorAction Stop
    Get-Data
    Process-Data
    Save-Results
}
catch {
    Write-Error "Database operation failed: $_"
}
```

### Capture Error Information Early

Copy `$_` or `$Error[0]` immediately within a catch block, as subsequent operations can overwrite them:

```powershell
try {
    Get-Service -Name "NonExistent" -ErrorAction Stop
}
catch {
    # Capture immediately
    $errorRecord = $_
    $errorMessage = $_.Exception.Message

    # Now safe to run other commands
    Write-EventLog -LogName Application -Source "MyScript" -EntryType Error -EventId 1 -Message $errorMessage

    # Use captured error for further processing
    throw $errorRecord
}
```

## Patterns to Avoid

### Don't Use `$?` for Error Checking

The `$?` variable only indicates if the last command "succeeded" from its own perspective, not whether an error occurred:

```powershell
# ANTI-PATTERN
Get-Process -Name "NonExistent"
if (-not $?) {
    Write-Warning "Something went wrong"  # Unreliable
}
```

### Don't Test for Null as Error Condition

While sometimes necessary, testing for null is a logically contorted approach:

```powershell
# ANTI-PATTERN
$user = Get-ADUser -Identity "NonExistent"
if ($user) {
    $user | Set-ADUser -Description "Updated"
}
else {
    Write-Warning "User not found"
}
```

```powershell
# BEST PRACTICE
try {
    $user = Get-ADUser -Identity "NonExistent" -ErrorAction Stop
    $user | Set-ADUser -Description "Updated"
}
catch {
    Write-Warning "User operation failed: $_"
}
```

## Error Handling Checklist

1. **Use `-ErrorAction Stop`** on all cmdlets inside `try` blocks
2. **Don't modify global `$ErrorActionPreference`** - set it locally and restore
3. **Put dependent operations in the same `try` block** - avoid flag-based logic
4. **Capture error info immediately** in catch blocks before running other commands
5. **Avoid `$?`** for error detection - use `try/catch` instead
6. **Use `Write-Warning`** for recoverable errors, `Write-Error` or `throw` for fatal ones
7. **Be specific in error messages** - include context like computer name, file path, or operation

## Related Documentation

- [Output, Streams, and Logging](output-streams-and-logging.md) - How to properly report errors to users
- [WhatIf and ShouldProcess](whatif-and-shouldprocess.md) - Preview operations before they might fail
