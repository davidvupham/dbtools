# How-To: Sign and Deploy PowerShell Modules

This guide covers signing PowerShell scripts and modules and deploying them to a system.

> [!IMPORTANT]
> **Prerequisite**: You must have a Code Signing certificate installed in your Windows Certificate Store.
> See [Import a Certificate to Windows](../import-certificate-to-windows.md) if you need to request or import one first.

---

## 1. Signing Process

### Option A: Use the Helper Script (Recommended)
We have provided a helper script to automate finding the best certificate and signing all files recursively.

```powershell
.\scripts\Sign-GDSModule.ps1 -ModulePath ".\Powershell\Modules\MyModule"
```

### Option B: Manual Steps
If you prefer to sign manually or understand the underlying commands:

#### Step 1: Get the Certificate
**Note:** Valid certificates often share the same Common Name (e.g., when renewed). **Always** select by Thumbprint or filter for the newest valid one.

```powershell
# Get all valid codesigning certs, sort by expiration date (newest last), and pick the latest
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
    Where-Object { $_.NotAfter -gt (Get-Date) } |
    Sort-Object NotAfter |
    Select-Object -Last 1

if (-not $cert) { throw "No valid Code Signing certificate found." }

Write-Host "Using Certificate: $($cert.Subject)"
Write-Host "Thumbprint:        $($cert.Thumbprint)"
```

#### Step 2: Sign the Files
Use the `Set-AuthenticodeSignature` cmdlet. You should sign **all** executable files in your module.

**Single File:**
```powershell
Set-AuthenticodeSignature -FilePath ".\MyScript.ps1" -Certificate $cert
```

**Entire Module (Recursive):**
```powershell
$filesToSign = Get-ChildItem -Path ".\Powershell\Modules\MyModule" -Include *.ps1,*.psm1,*.psd1,*.ps1xml -Recurse

foreach ($file in $filesToSign) {
    Set-AuthenticodeSignature -FilePath $file.FullName -Certificate $cert
}
```

> [!NOTE]
> It is best practice to include a **Timestamp Server** URL when signing. This ensures the signature remains valid even after the certificate expires.
>
> `Set-AuthenticodeSignature -FilePath $file -Certificate $cert -TimestampServer "http://timestamp.digicert.com"`

---

## 2. Verifying Signatures

After signing, verify the signature status.

```powershell
Get-AuthenticodeSignature -FilePath ".\Powershell\Modules\MyModule\MyModule.psd1"
```

**Status:**
*   `Valid`: Signed and trusted.
*   `UnknownError`: Often means the certificate is not trusted (e.g., self-signed cert not in Trusted Root/Publishers).
*   `HashMismatch`: The file was modified *after* signing. You must re-sign it.

---

## 3. Manual Deployment

Once signed, "deploying" a module manually means copying it to a location where PowerShell looks for modules (`$env:PSModulePath`).

### Locations
*   **Current User** (No Admin required):
    `$home\Documents\PowerShell\Modules`

*   **All Users** (Admin required):
    `C:\Program Files\PowerShell\Modules` (PowerShell Core / 6+)
    `C:\Program Files\WindowsPowerShell\Modules` (Windows PowerShell / 5.1)

### Deployment Steps

1.  **Prepare Directory**:
    ```powershell
    $destPath = "$home\Documents\PowerShell\Modules\MyModule"
    New-Item -ItemType Directory -Force -Path $destPath
    ```

2.  **Copy Files**:
    ```powershell
    Copy-Item -Path ".\Powershell\Modules\MyModule\*" -Destination $destPath -Recurse -Force
    ```

3.  **Import**:
    ```powershell
    Import-Module MyModule
    ```
