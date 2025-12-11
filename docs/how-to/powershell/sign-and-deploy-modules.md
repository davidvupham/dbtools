# How-To: Manually Sign and Deploy PowerShell Modules

This guide covers the manual process of signing PowerShell scripts and modules with a code signing certificate and deploying them to a system.

## 1. Certificate Requirements

**Does the certificate have to be from a Windows Server?**
**No.** A valid Code Signing certificate can come from multiple sources:

1.  **Public Certificate Authority (CA)**: (e.g., DigiCert, Sectigo, GlobalSign). These are trusted by default on almost all Windows systems. Recommended for external distribution.
2.  **Internal Enterprise CA** (AD CS): Often running on Windows Server, but can be any internal PKI. Trusted only by domain-joined machines.
3.  **Self-Signed Certificate**: Generated locally using PowerShell. **Only for testing/development.** You must manually install this cert into the "Trusted Publishers" store on any machine running the script.

**Key Requirement**: The certificate must have the **Code Signing** Extended Key Usage (OID `1.3.6.1.5.5.7.3.3`).

### Certificate Request Details (CSR)
If you are requesting a certificate from your security team or a Public CA, use these values:

*   **Common Name (CN)**: This represents the **Publisher's Identity**, not a server name.
    *   *Examples*: "GDS DevOps Team", "Contoso IT".
    *   *Why it matters*: This name appears in the User Account Control (UAC) prompt or PowerShell trust error: *"Do you trust software signed by 'GDS DevOps Team'?"*
*   **Subject Alternative Name (SAN)**: **Not required** for code signing.
    *   *If strictly required by your CA software*: Use your **Email Address** (UPN) or repeat the Common Name. Code signing certificates validate identity, not a network location (DNS).
*   **Key Type**: RSA 2048-bit (minimum) or 4096-bit.
*   **Extended Key Usage (EKU)**: Must include **Code Signing** (`1.3.6.1.5.5.7.3.3`).
*   **Key Usage**: Digital Signature.

### Importing the Certificate
The Windows Certificate Store requires a single file containing both the Public and Private keys (usually **`.pfx`** or **`.p12`**).

#### Scenario A: You have a `.pfx` or `.p12` file
1.  **Double-click** the file to open the Certificate Import Wizard.
2.  Select **Current User** -> **Personal** store.
3.  Enter the password when prompted.

#### Scenario B: You have separate files (.crt/.cert, .key, .pass)
You must **merge** them into a `.pfx` file.

**Option 1: Use our Helper Script (PowerShell 7+) - RECOMMENDED**
If you do not have OpenSSL, use the provided script which uses .NET to merge functionality.

```powershell
# You'll need the password from your .pass file
$pass = Get-Content ".\my.pass"
.\scripts\Merge-ToPfx.ps1 -CertFile ".\my.cert" -KeyFile ".\my.key" -KeyPassword $pass -OutputFile ".\MyCodeSigning.pfx"
```

**Option 2: Use OpenSSL (via Git Bash)**
If you have Git installed, you likely have `openssl.exe` at `C:\Program Files\Git\usr\bin\openssl.exe`.

```bash
# Uses the password from my.pass automatically
openssl pkcs12 -export -out "MyCodeSigning.pfx" -inkey "my.key" -in "my.cert" -passin file:.\my.pass
```

**Steps:**
1.  Run one of the commands above. (Note: The `.csr` file is not needed for this step).
2.  Follow the steps in **Scenario A** using the newly created `MyCodeSigning.pfx`.

#### Critical Check
After import, open `certmgr.msc`, go to `Personal > Certificates`, and double-click your certificte. You **MUST** see a small key icon with the message:
*"You have a private key that corresponds to this certificate."*
If you do not see this, the Private Key is missing, and signing will fail.

---

## 2. Signing Process

### Option A: Use the Helper Script (Recommended)
We have provided a helper script to automate finding the best certificate and signing all files recursively.

```powershell
.\scripts\Sign-GDSModule.ps1 -ModulePath ".\Powershell\Modules\MyModule"
```

### Option B: Manual Steps
If you prefer to sign manually or understand the underlying commands:

### Step 1: Get the Certificate
**Note:** valid certificates often share the same Common Name (e.g., when renewed). **Always** select by Thumbprint or filter for the newest valid one.

To see if you have a code signing certificate available in your personal store:

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

### Step 2: Sign the Files
Use the `Set-AuthenticodeSignature` cmdlet. You should sign **all** executable files in your module.

#### Single File
```powershell
Set-AuthenticodeSignature -FilePath ".\MyScript.ps1" -Certificate $cert
```

#### Entire Module (Recursive)
This snippet finds all relevant files in a directory and signs them.

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

## 3. Verifying Signatures

After signing, verify the valid signature status.

```powershell
Get-AuthenticodeSignature -FilePath ".\Powershell\Modules\MyModule\MyModule.psd1"
```

**Status:**
*   `Valid`: Signed and trusted.
*   `UnknownError`: Often means the certificate is not trusted (e.g., self-signed cert not in Trusted Root/Publishers).
*   `HashMismatch`: The file was modified *after* signing. You must re-sign it.

---

## 4. Manual Deployment

Once signed, "deploying" a module manually simply means copying it to a location where PowerShell looks for modules (`$env:PSModulePath`).

### Locations
*   **Current User** (No Admin required):
    `$home\Documents\PowerShell\Modules`
    *(e.g., `C:\Users\david\Documents\PowerShell\Modules`)*

*   **All Users** (Admin required):
    `C:\Program Files\PowerShell\Modules` (PowerShell Core / 6+)
    `C:\Program Files\WindowsPowerShell\Modules` (Windows PowerShell / 5.1)

### Deployment Steps

1.  **Prepare Directory**: ensure the destination folder exists.
    ```powershell
    $destPath = "$home\Documents\PowerShell\Modules\MyModule"
    New-Item -ItemType Directory -Force -Path $destPath
    ```

2.  **Copy Files**: Copy the **signed** files.
    ```powershell
    Copy-Item -Path ".\Powershell\Modules\MyModule\*" -Destination $destPath -Recurse -Force
    ```

3.  **Import**:
    ```powershell
    Import-Module MyModule
    ```
