# PowerShell Script Signing Tutorial

This tutorial explains what PowerShell script signing is, why it is important, and provides a step-by-step guide on how to sign a script using a self-signed certificate.

## What is Script Signing?

Script signing is a security feature in PowerShell that uses digital signatures to guarantee two things:

1. **Authenticity**: The script was created by a trusted publisher (the signer).
2. **Integrity**: The script has not been altered since it was signed.

A digital signature is an encrypted block of data appended to the script file. If even a single character in the script is changed after signing, the signature becomes invalid, and PowerShell will refuse to run it (depending on the execution policy).

## Why is it Needed?

### 1. Execution Policies

PowerShell's execution policy determines which scripts can be run. In many secure environments, the policy is set to `AllSigned` or `RemoteSigned`.

* **AllSigned**: Only scripts signed by a trusted publisher can run.
* **RemoteSigned**: Downloaded scripts must be signed. Local scripts can run unsigned.

To run scripts in these environments without lowering security settings, you must sign them.

### 2. Trust and Security

Signing prevents the execution of malicious scripts that might have been injected or modified by an attacker. It ensures that you are running exactly what you expect to run.

## Tutorial: Signing a Script with a Self-Signed Certificate

In a production environment, you would typically use a certificate from a public Certificate Authority (CA) or an internal corporate CA. For this tutorial, we will create a self-signed certificate to demonstrate the process.

### Prerequisites

* Windows OS with PowerShell (5.1 or Core).
* Administrator privileges (required to add certificates to the trusted store).

### Step 1: Create a Self-Signed Certificate

Run the following command in an elevated PowerShell prompt to create a code-signing certificate:

```powershell
$cert = New-SelfSignedCertificate -DnsName "MyLocalCodeSigning" -CertStoreLocation "Cert:\CurrentUser\My" -Type CodeSigningCert
```

### Step 2: Create a Sample Script

Create a simple script named `hello.ps1`:

```powershell
Write-Host "Hello, World! This script is signed."
```

### Step 3: Sign the Script

Use the `Set-AuthenticodeSignature` cmdlet to sign the script with the certificate we created:

```powershell
Set-AuthenticodeSignature -FilePath .\hello.ps1 -Certificate $cert
```

If successful, you will see a status of `Valid`. Open `hello.ps1` in a text editor, and you will see a large block of commented text at the bottom—this is the signature.

### Step 4: Verify the Signature

You can verify the signature of any script using `Get-AuthenticodeSignature`:

```powershell
Get-AuthenticodeSignature -FilePath .\hello.ps1
```

### Step 5: Trusting the Certificate

If you try to run the script now with an `AllSigned` policy, it might still fail because the computer doesn't trust your self-signed certificate yet.

To trust it, you need to move the certificate to the "Trusted Publishers" store.

1. **Export the certificate** (optional, or just move it directly via certmgr). Here is how to do it via PowerShell:

    ```powershell
    $rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store "Root", "CurrentUser"
    $rootStore.Open("ReadWrite")
    $rootStore.Add($cert)
    $rootStore.Close()

    $publisherStore = New-Object System.Security.Cryptography.X509Certificates.X509Store "TrustedPublisher", "CurrentUser"
    $publisherStore.Open("ReadWrite")
    $publisherStore.Add($cert)
    $publisherStore.Close()
    ```

    *Note: In a real scenario, you would distribute the public key of your certificate to the Trusted Publishers store of all target machines via Group Policy.*

2. **Run the script**:

    ```powershell
    .\hello.ps1
    ```

## Self-Signed vs. Certificate Authority (CA)

It is important to understand the difference between the certificate used in this tutorial and one you would use in a professional environment.

| Feature | Self-Signed Certificate | Certificate Authority (CA) |
| :--- | :--- | :--- |
| **Source** | Created by you on your local machine. | Issued by a trusted third party (e.g., Verisign, DigiCert) or an internal corporate CA. |
| **Trust** | Trusted **only** by the machine that created it (unless manually exported/imported). | Trusted by **all** computers that trust the CA (often all Windows machines by default). |
| **Cost** | Free. | Public certs cost money; Internal certs require infrastructure. |
| **Use Case** | Development, testing, personal scripts. | Production, distributing scripts to others, corporate environments. |

**Key Takeaway**: Self-signed certificates are great for learning and testing, but for scripts that will be shared or run on many machines, you should use a certificate from a CA to avoid having to manually configure trust on every single machine.

## Frequently Asked Questions

### Can the same certificate be used for multiple scripts?

**Yes.** You do not need a separate certificate for every script you write.

* **Reusability**: You typically issue a single "Code Signing Certificate" to a developer, a team, or a server. That one certificate is used to sign hundreds or thousands of different scripts.
* **Unique Signatures**: While the *certificate* is reused, the *signature block* (the commented text at the bottom of the file) is unique for every script. The signature is mathematically generated based on the script's exact contents and your private key.
* **Best Practice**: In a corporate environment, it is common to have a "Build Server" certificate that automatically signs all scripts before they are deployed to production.

## Automating Signing with GitHub Actions

You can automate the signing process using a CI/CD pipeline like GitHub Actions. This ensures that every script deployed to production is correctly signed without manual intervention.

### Prerequisites

1. **Certificate (PFX format)**: You need your code signing certificate exported as a `.pfx` file with a password.
2. **Base64 Encoding**: GitHub Secrets cannot store binary files directly. You must encode the `.pfx` file as a Base64 string.

    **PowerShell command to encode:**

    ```powershell
    $pfxPath = "C:\path\to\cert.pfx"
    $base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($pfxPath))
    Set-Clipboard -Value $base64
    ```

3. **GitHub Secrets**: Go to your repository settings -> Secrets and variables -> Actions, and add two secrets:
    * `SIGNING_CERT_BASE64`: Paste the Base64 string from the previous step.
    * `SIGNING_CERT_PASSWORD`: The password for the PFX file.

### Sample Workflow

Create a file at `.github/workflows/sign-scripts.yml`:

```yaml
name: Sign PowerShell Scripts

on:
  push:
    branches: [ "main" ]

jobs:
  sign-and-publish:
    runs-on: windows-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Certificate
        shell: powershell
        run: |
          # 1. Decode the Base64 secret to a temporary PFX file
          $pfxPath = "$env:RUNNER_TEMP\cert.pfx"
          $base64 = "${{ secrets.SIGNING_CERT_BASE64 }}"
          [IO.File]::WriteAllBytes($pfxPath, [Convert]::FromBase64String($base64))

          # 2. Import the certificate to the current user's store
          $password = ConvertTo-SecureString -String "${{ secrets.SIGNING_CERT_PASSWORD }}" -AsPlainText -Force
          Import-PfxCertificate -FilePath $pfxPath -CertStoreLocation Cert:\CurrentUser\My -Password $password

      - name: Sign Scripts
        shell: powershell
        run: |
          # 3. Find the certificate we just imported
          $cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

          if (-not $cert) {
            Write-Error "Code signing certificate not found."
            exit 1
          }

          # 4. Sign all .ps1 files in the repository
          Get-ChildItem -Path . -Filter *.ps1 -Recurse | ForEach-Object {
            Write-Host "Signing $($_.Name)..."
            Set-AuthenticodeSignature -FilePath $_.FullName -Certificate $cert
          }

      - name: Upload Signed Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: signed-scripts
          path: "**/*.ps1"
```

### Explanation

1. **Setup Certificate**: The workflow decodes the Base64 secret back into a `.pfx` file and imports it into the runner's certificate store.
2. **Sign Scripts**: It retrieves the imported certificate and loops through all `.ps1` files to sign them.
3. **Upload Artifacts**: The signed scripts are uploaded as build artifacts, ready for deployment.

## Summary

You have now learned how to create a code-signing certificate, sign a PowerShell script, and verify its signature. This process is essential for maintaining a secure automation environment.
