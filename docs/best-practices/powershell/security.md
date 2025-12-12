# PowerShell Best Practices: Security

Security is critical when writing PowerShell scripts, especially those handling credentials, sensitive data, or production systems. This document covers secure coding patterns.

## Credential Management

### Always Use PSCredential

Never accept passwords as plain strings. Use `[PSCredential]` objects which store passwords as SecureStrings:

```powershell
# BEST PRACTICE - accept PSCredential
function Connect-Database {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Server,

        [Parameter(Mandatory)]
        [System.Management.Automation.PSCredential]
        [System.Management.Automation.Credential()]
        $Credential
    )

    # Password is encrypted in memory
    $connection = New-Object System.Data.SqlClient.SqlConnection
    $connection.ConnectionString = "Server=$Server;User Id=$($Credential.UserName)"
    # ...
}

# ANTI-PATTERN - plain text password
function Connect-Database {
    param(
        [string]$Server,
        [string]$Username,
        [string]$Password  # NEVER DO THIS
    )
}
```

### Use the Credential Attribute

The `[Credential()]` attribute enables automatic prompting when the user passes a username string:

```powershell
param(
    [System.Management.Automation.PSCredential]
    [System.Management.Automation.Credential()]
    $Credential
)

# User can call with:
# -Credential (Get-Credential)
# -Credential $savedCred
# -Credential "domain\user"  ← Prompts for password automatically
```

### Never Call Get-Credential Inside Functions

Let callers provide credentials so they can reuse them:

```powershell
# ANTI-PATTERN - prompts every time
function Do-Something {
    $cred = Get-Credential  # Ask inside
    # ...
}

# BEST PRACTICE - accept as parameter
function Do-Something {
    param([PSCredential]$Credential)
    # Caller decides how to provide
}

# Caller can reuse:
$cred = Get-Credential
Do-Something -Credential $cred
Do-AnotherThing -Credential $cred
```

## Secure String Handling

### Storing Credentials to Disk

Use `Export-Clixml` which encrypts SecureStrings using DPAPI (Data Protection API):

```powershell
# Save credential securely (only decryptable by same user on same machine)
Get-Credential | Export-Clixml -Path "$env:USERPROFILE\.creds\myservice.xml"

# Load saved credential
$Credential = Import-Clixml -Path "$env:USERPROFILE\.creds\myservice.xml"
```

> [!IMPORTANT]
> Credentials exported with `Export-Clixml` can only be decrypted by the same user account on the same computer where they were created.

### Converting SecureString for APIs

If you absolutely must pass a plain text password to a .NET API, do it inline without storing in a variable:

```powershell
# BEST PRACTICE - decrypt inline, never store
$ThirdPartyApi.SetPassword($Credential.GetNetworkCredential().Password)

# ANTI-PATTERN - plain text lingers in memory
$plainPassword = $Credential.GetNetworkCredential().Password
$ThirdPartyApi.SetPassword($plainPassword)
# $plainPassword still contains password
```

### Manual SecureString Decryption

When `GetNetworkCredential()` isn't available:

```powershell
function ConvertFrom-SecureStringToPlain {
    param([SecureString]$SecureString)

    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
    finally {
        # Critical: free the unmanaged memory
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    }
}
```

## Sensitive Data Protection

### Use SecureString for Non-Password Secrets

API keys, tokens, and other sensitive strings should also use SecureString:

```powershell
function Connect-CloudService {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [SecureString]$ApiKey
    )

    # Document how to provide the value
    <#
    .EXAMPLE
    $key = Read-Host -Prompt "API Key" -AsSecureString
    Connect-CloudService -ApiKey $key
    #>
}
```

### Saving Encrypted Strings to Disk

For automation scenarios where credentials must persist:

```powershell
# Save encrypted (DPAPI - user/machine specific)
$secureString = Read-Host -Prompt "Enter secret" -AsSecureString
ConvertFrom-SecureString -SecureString $secureString |
    Out-File -Path "$env:APPDATA\MyApp\secret.txt"

# Load and decrypt
$secureString = Get-Content -Path "$env:APPDATA\MyApp\secret.txt" |
    ConvertTo-SecureString
```

### Using AES for Portable Encryption

For secrets that need to be shared or used across machines:

```powershell
# Generate a key (store this securely!)
$key = New-Object Byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($key)
$key | Out-File -Path "C:\Secure\encryption.key"

# Encrypt with key
$secureString = Read-Host -Prompt "Secret" -AsSecureString
ConvertFrom-SecureString -SecureString $secureString -Key $key |
    Out-File -Path "encrypted-secret.txt"

# Decrypt with key
$key = Get-Content -Path "C:\Secure\encryption.key"
$secureString = Get-Content -Path "encrypted-secret.txt" |
    ConvertTo-SecureString -Key $key
```

> [!CAUTION]
> The encryption key must be protected with the same care as the secret itself. Consider using a key management service for production scenarios.

## Execution Policy and Code Signing

### Understand Execution Policies

Execution policies help prevent accidental script execution, but are not a security boundary:

| Policy | Effect |
|--------|--------|
| `Restricted` | No scripts allowed |
| `AllSigned` | Only signed scripts run |
| `RemoteSigned` | Downloaded scripts must be signed |
| `Unrestricted` | All scripts run (with warnings for remote) |
| `Bypass` | Nothing is blocked, no warnings |

### Sign Production Scripts

For production use, sign scripts with a code signing certificate:

```powershell
# Sign a script
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert
Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert

# Verify signature
Get-AuthenticodeSignature -FilePath ".\script.ps1"
```

## Security Checklist

1. **Use PSCredential** for all passwords and credentials
2. **Apply the `[Credential()]` attribute** for automatic prompting
3. **Never store passwords in plain text** in scripts or variables
4. **Use Export-Clixml** for persisting credentials to disk
5. **Decrypt secrets inline** when passing to APIs, don't store in variables
6. **Sign scripts** for production deployment
7. **Validate all input** to prevent injection attacks
8. **Use `-WhatIf`** for destructive operations (see [WhatIf and ShouldProcess](whatif-and-shouldprocess.md))
9. **Audit script activity** with PowerShell logging and transcription
10. **Least privilege** - run scripts with minimal required permissions

## Related Documentation

- [Advanced Functions](advanced-functions.md) - Parameter validation and secure patterns
- [Error Handling](error-handling.md) - Secure error handling practices
