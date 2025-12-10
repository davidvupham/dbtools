# Runbook: Enabling WinRM HTTPS

**Objective**: Configure Windows Remote Management (WinRM) to accept HTTPS connections on Port 5986 using a standard SSL certificate.

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

### 2. Configure WinRM Service
**Goal**: Ensure WinRM is running and Listener is active.

**Procedure**:
```powershell
# 1. Start Service
Start-Service WinRM

# 2. Check for Listener
Get-ChildItem WSMan:\localhost\Listener | Where-Object { $_.Keys -like "TRANSPORT=HTTPS" }
```
- If no output -> **Action**: Create Listener.
  ```powershell
  # Replace THUMBPRINT with the actual thumbprint from Step 1
  New-Item -Path WSMan:\localhost\Listener -Transport HTTPS -Address * -CertificateThumbprint <THUMBPRINT> -Force
  ```

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
