# How-to: Configure WinRM over HTTPS

This how-to guide explains the steps required to secure Windows Remoting (WinRM) using HTTPS and SSL/TLS certificates.

For a deeper understanding of certificates, see [Windows Certificates and CSRs](../explanation/Windows-Certificates-and-CSRs.md).

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
The `Enable-GDSWindowsRemoting.ps1` script in this repository automates these steps.

### Option A: Auto-Detect (Recommended)
By default, the script attempts to find a valid existing "Server Authentication" certificate matching the computer name.
- **If found**: It uses the valid certificate (selecting the newest one if multiple exist).
- **If NOT found**: It falls back to generating a new self-signed certificate.

```powershell
Import-Module GDS.Windows
Enable-GDSWindowsRemoting
```

### Option B: Force New Self-Signed Certificate
Use this for development or test environments where you want to ensure a fresh, self-signed certificate is generated, ignoring any existing ones.

```powershell
Import-Module GDS.Windows
Enable-GDSWindowsRemoting -ForceNewSSLCert
```

### Option C: Use a Specific Certificate (Manual)
If you have multiple certificates and want to explicitly specify which one to use:

1.  **Find the Thumbprint**:
    ```powershell
    Get-ChildItem Cert:\LocalMachine\My | Format-Table Subject, Thumbprint
    ```
2.  **Run the script with the Thumbprint**:
    ```powershell
    Import-Module GDS.Windows
    Enable-GDSWindowsRemoting -CertificateThumbprint "A1B2C3D4E5FA6B7C8D..."
    ```
