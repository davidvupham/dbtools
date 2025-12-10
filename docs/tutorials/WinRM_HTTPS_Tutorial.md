# Tutorial: Enabling WinRM over HTTPS with Certificates

This tutorial explains the concepts and steps required to secure Windows Remoting (WinRM) using HTTPS and SSL/TLS certificates.

## Prerequisites
- A Windows machine (Server or Desktop)
- Administrative privileges (Run as Administrator)
- PowerShell 3.0 or later

## Use Case
By default, WinRM uses Kerberos for authentication and encryption within a domain. However, for non-domain joined machines or extra security compliance, you may want to enforce HTTPS (SSL/TLS).

## The 3 Key Components
To enable WinRM over HTTPS (Port 5986), you need:
1.  **Certificate**: Identity proof for the server.
2.  **Listener**: WinRM configuration binding the certificate to port 5986.
3.  **Firewall**: Rule allowing inbound traffic on port 5986.

## Step-by-Step Guide

### 1. Check for Existing Certificates
Before creating a new one, check if your machine already has a valid "Server Authentication" certificate.

```powershell
Get-ChildItem Cert:\LocalMachine\My | Where-Object {
    $_.NotAfter -gt (Get-Date) # Not expired
} | Select-Object Subject, Thumbprint, NotAfter, @{n="EKU";e={$_.EnhancedKeyUsageList.FriendlyName}}
```

**What to look for:**
- **Subject**: Matches your computer name.
- **EKU**: Contains "Server Authentication".
- **NotAfter**: Future date.

### 2. Generate a Certificate (If needed)
If you are in a test environment, you can create a self-signed certificate. **For production, use a certificate from your Trusted CA.**

```powershell
# Create a new Self-Signed Certificate
$cert = New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My
```

### 3. Create the WinRM HTTPS Listener
This configures the WinRM service to listen on HTTPS using the certificate.

```powershell
# Get the certificate thumbprint
$Thumbprint = $cert.Thumbprint

# Create the HTTPS listener
New-Item -Path WSMan:\localhost\Listener -Transport HTTPS -Address * -CertificateThumbprint $Thumbprint -Force
```

### 4. Configure Firewall
Allow traffic on port 5986.

```powershell
New-NetFirewallRule -Name "WinRM-HTTPS" -DisplayName "Allow WinRM HTTPS" -Protocol TCP -LocalPort 5986 -Action Allow -Profile Any
```

## Automating this with `Enable-GDSWindowsRemoting.ps1`
The `Enable-GDSWindowsRemoting.ps1` script in this repository automates these steps for you.

### Option A: Auto-Detect or Generate Self-Signed (Default)
This is useful for new deployments or dev environments.
```powershell
Enable-GDSWindowsRemoting -ForceNewSSLCert
```

### Option B: Use an Existing Certificate (Production)
If you already have a trusted certificate (e.g., from an internal CA) installed in `Cert:\LocalMachine\My`:

1.  **Find the Thumbprint**:
    ```powershell
    Get-ChildItem Cert:\LocalMachine\My | Format-Table Subject, Thumbprint
    ```
2.  **Run the script with the Thumbprint**:
    ```powershell
    Enable-GDSWindowsRemoting -CertificateThumbprint "A1B2C3D4E5FA6B7C8D..."
    ```
    *Note: The script will validate that the certificate exists before proceeding.*
