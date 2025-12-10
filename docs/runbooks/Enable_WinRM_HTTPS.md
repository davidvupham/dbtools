# Runbook: Enabling WinRM HTTPS

**Objective**: Configure Windows Remote Management (WinRM) to accept HTTPS connections on Port 5986.
- [How-to Guide: Configure WinRM HTTPS](../how-to/Configure-WinRM-HTTPS.md)
- [Explanation: Certificates & CSRs](../explanation/Windows-Certificates-and-CSRs.md)

## Pre-Flight Checks
- [ ] User has LOCAL Administrator privileges.
- [ ] PowerShell version is 5.1 or higher (recommended).
- [ ] Machine has a valid "Server Authentication" certificate OR permission to generate a self-signed one.

## Execution Steps

### 1. Verify/Obtain Certificate
**Goal**: Ensure a valid certificate exists in `Cert:\LocalMachine\My`.

**Procedure**:
Run the following check:
```powershell
$certs = Get-ChildItem Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*$env:COMPUTERNAME*" -and $_.NotAfter -gt (Get-Date) }
if ($certs) { Write-Host "Certificate Found: $($certs[0].Thumbprint)" } else { Write-Warning "No Certificate Found" }
```
- If "No Certificate Found" -> **Action**: Request a certificate from CA or generate Self-Signed (Dev only).
- If "Certificate Found" -> **Action**: Note the thumbprint and proceed to Step 2 using the `-CertificateThumbprint` parameter.

### 2. Configure WinRM Service
**Goal**: Ensure WinRM is running and Listener is active.

**Procedure**:
Use the `Enable-GDSWindowsRemoting.ps1` script to handle the configuration automatically.

**Scenario A: Certificate Found in Step 1**
```powershell
Enable-GDSWindowsRemoting -ComputerName localhost -CertificateThumbprint "THUMBPRINT_FROM_STEP_1"
```

**Scenario B: No Certificate (Generate Self-Signed)**
```powershell
Enable-GDSWindowsRemoting -ComputerName localhost -ForceNewSSLCert
```

*This script will ensure the service is running, the HTTPS listener is created with the correct thumbprint, and the firewall rules are set.*

### 3. Verify Firewall
**Goal**: Ensure port 5986 is open.

**Procedure**:
```powershell
Get-NetFirewallRule -DisplayName "Allow WinRM HTTPS" -ErrorAction SilentlyContinue
```
- If attempting to connect and failing -> **Action**: Create Rule.
  ```powershell
  New-NetFirewallRule -DisplayName "Allow WinRM HTTPS" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow
  ```

## Verification
1.  **Local Loopback Check**:
    ```powershell
    $opt = New-PSSessionOption -SkipCACheck -SkipCNCheck
    Test-WSMan -ComputerName localhost -UseSSL -SessionOption $opt
    ```
    *Expected Output*: details about the ProtocolVersion and ProductVersion.

2.  **Remote Connection Check**:
    From a remote machine:
    ```powershell
    Enter-PSSession -ComputerName <TARGET_IP> -UseSSL -Credential (Get-Credential)
    ```

## Rollback / Cleanup
To remove the configuration:
```powershell
# Remove Listener
Remove-Item WSMan:\localhost\Listener\Listener_1399852236 # (ID may vary, check Get-ChildItem)

# Remove Firewall Rule
Remove-NetFirewallRule -DisplayName "Allow WinRM HTTPS"
```
