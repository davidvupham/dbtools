# PowerShell Best Practices

This directory contains standards and guidelines for writing effective, maintainable PowerShell scripts.

## Documents

| Document | Description |
|----------|-------------|
| [Advanced Functions](advanced-functions.md) | CmdletBinding, parameter validation, pipeline input, tool vs controller patterns |
| [Error Handling](error-handling.md) | Try/catch patterns, `-ErrorAction Stop`, terminating vs non-terminating errors |
| [Naming and Style](naming-and-style.md) | Verb-Noun naming, PascalCase, approved verbs, parameter naming standards |
| [Output, Streams, and Logging](output-streams-and-logging.md) | Separating data from status, Write-Host vs Write-Output vs Write-Verbose |
| [Security](security.md) | Credential handling, PSCredential, SecureString, code signing |
| [WhatIf and ShouldProcess](whatif-and-shouldprocess.md) | Preview mode for destructive operations, local and remote execution patterns |

## Quick Reference

### Function Template

```powershell
function Verb-Noun {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [ValidateNotNullOrEmpty()]
        [string[]]$ComputerName,

        [System.Management.Automation.PSCredential]
        [System.Management.Automation.Credential()]
        $Credential
    )

    process {
        foreach ($Computer in $ComputerName) {
            try {
                if ($PSCmdlet.ShouldProcess($Computer, "Perform action")) {
                    # Action here
                    Write-Verbose "Processing $Computer"
                }
            }
            catch {
                Write-Warning "Failed on $Computer: $_"
            }
        }
    }
}
```

### Key Principles

1. **Use `[CmdletBinding()]`** on all functions
2. **Separate status from data** - Use Write-Host for status, pipeline for data
3. **Use `-ErrorAction Stop`** inside try blocks
4. **Validate parameters early** with validation attributes
5. **Use PSCredential** for credentials, never plain strings
6. **Support `-WhatIf`** for destructive operations
7. **Use approved verbs** - Run `Get-Verb` to see the list
8. **Use full command and parameter names** in scripts

## External Resources

- [Microsoft: Cmdlet Development Guidelines](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/strongly-encouraged-development-guidelines)
- [Microsoft: Functions](https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/09-functions)
- [PowerShell Practice and Style Guide](https://poshcode.gitbook.io/powershell-practice-and-style)
