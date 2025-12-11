# How-To: Import a Certificate to Windows

This guide covers how to request, obtain, and import a certificate into the Windows Certificate Store. This applies to certificates used for code signing, SSL/TLS, WinRM, document signing, and other purposes.

---

## 1. Certificate Sources

A valid Code Signing certificate can come from:

1.  **Public Certificate Authority (CA)**: (e.g., DigiCert, Sectigo, GlobalSign). Trusted by default on almost all Windows systems. Recommended for external distribution.
2.  **Internal Enterprise CA** (AD CS): Often running on Windows Server, but can be any internal PKI. Trusted only by domain-joined machines.
3.  **Self-Signed Certificate**: Generated locally using PowerShell. **Only for testing/development.** You must manually install this cert into the "Trusted Publishers" store on any machine running the script.

**Key Requirement**: The certificate must have the **Code Signing** Extended Key Usage (OID `1.3.6.1.5.5.7.3.3`).

---

## 2. Requesting a Certificate (CSR Details)

If you are requesting a certificate from your security team or a Public CA, use these values:

*   **Common Name (CN)**: This represents the **Publisher's Identity**, not a server name.
    *   *Examples*: "GDS DevOps Team", "Contoso IT".
    *   *Why it matters*: This name appears in the User Account Control (UAC) prompt or PowerShell trust error: *"Do you trust software signed by 'GDS DevOps Team'?"*
*   **Subject Alternative Name (SAN)**: **Not required** for code signing.
    *   *If strictly required by your CA software*: Use your **Email Address** (UPN) or repeat the Common Name.
*   **Key Type**: RSA 2048-bit (minimum) or 4096-bit.
*   **Extended Key Usage (EKU)**: Must include **Code Signing** (`1.3.6.1.5.5.7.3.3`).
*   **Key Usage**: Digital Signature.

---

## 3. Importing the Certificate

The Windows Certificate Store requires a single file containing both the Public and Private keys (usually **`.pfx`** or **`.p12`**).

### Scenario A: You have a `.pfx` or `.p12` file
1.  **Double-click** the file to open the Certificate Import Wizard.
2.  Select **Current User** -> **Personal** store.
3.  Enter the password when prompted.

### Scenario B: You have separate files (.crt/.cert, .key, .pass)
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

| Parameter | Description |
|-----------|-------------|
| `pkcs12` | OpenSSL subcommand for working with PKCS#12 files (`.pfx`/`.p12`). |
| `-export` | Create a `.pfx` file (bundle cert + key). |
| `-out "..."` | Output file path for the resulting `.pfx`. |
| `-inkey "..."` | Path to your **Private Key** file. |
| `-in "..."` | Path to your **Certificate** file. |
| `-passin file:...` | Read the `.key` file's password from the specified file. |

> [!NOTE]
> OpenSSL will prompt you for a **new password** to protect the output `.pfx` file. This is the password you'll enter when importing into Windows.

**Steps:**
1.  Run one of the commands above. (Note: The `.csr` file is not needed for this step).
2.  Follow the steps in **Scenario A** using the newly created `MyCodeSigning.pfx`.

---

## 4. Verify Import

After import, open `certmgr.msc`, go to `Personal > Certificates`, and double-click your certificate. You **MUST** see a small key icon with the message:
*"You have a private key that corresponds to this certificate."*
If you do not see this, the Private Key is missing, and signing will fail.

---

## Next Steps

Once your certificate is imported, you can use it for:
- **Code Signing**: See [Sign and Deploy PowerShell Modules](powershell/sign-and-deploy-modules.md)
- **WinRM over HTTPS**: See [Configure WinRM HTTPS](Configure-WinRM-HTTPS.md)
- **SSL/TLS**: Configure your application to use the certificate from the store
