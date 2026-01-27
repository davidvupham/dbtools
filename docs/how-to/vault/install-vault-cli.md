# Install Vault CLI

**[← Back to How-To Guides](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Database Tools Team
> **Status:** Production

<div align="center">

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-How--To-green)

</div>

> **Goal:** Install the HashiCorp Vault CLI on Linux systems.
> **Prerequisites:** 
> - `sudo` privileges on the target machine.
> - Internet access to reach HashiCorp repositories.

## Table of Contents

- [1. Install on RHEL/CentOS](#1-install-on-rhelcentos)
- [2. Install on Ubuntu/Debian](#2-install-on-ubuntudebian)
- [3. Install on Windows](#3-install-on-windows)
- [4. Verify Installation](#4-verify-installation)
- [Troubleshooting](#troubleshooting)

## Steps

## 1. Install on RHEL/CentOS

For Red Hat Enterprise Linux (RHEL), CentOS, and Fedora, use the `yum-config-manager` to add the official HashiCorp repository.

**Add the HashiCorp repository:**

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
```

**Install Vault Enterprise:**

```bash
sudo yum -y install vault-enterprise
```

[Back to Table of Contents](#table-of-contents)

## 2. Install on Ubuntu/Debian

For Ubuntu and Debian, allow usage of the HashiCorp GPG key and add the repository to your sources list.

**Add the GPG key and repository:**

```bash
# Install prerequisites
sudo apt-get update && sudo apt-get install -y gpg

# Download the signing key to a new keyring
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Verify the key's fingerprint
gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint

# Add the HashiCorp repo
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

**Install Vault Enterprise:**

```bash
sudo apt-get update
sudo apt-get install vault-enterprise
```

[Back to Table of Contents](#table-of-contents)

[Back to Table of Contents](#table-of-contents)

## 3. Install on Windows

There are two primary methods for installing Vault on Windows.

### Method A: Manual Download (Recommended for Enterprise)

To ensure you have the specific **Vault Enterprise** binary (with the `+ent` build tag):

1.  **Download:** Visit the [HashiCorp Releases](https://releases.hashicorp.com/vault/) page.
2.  **Select Version:** Choose your desired version (e.g., `1.15.2+ent`).
3.  **Download Zip:** Download the `vault_<version>+ent_windows_amd64.zip` file.
4.  **Extract:** Unzip the `vault.exe` binary to a permanent location (e.g., `C:\HashiCorp\Vault\`).
5.  **Update PATH:** Add that directory to your system's `Path` environment variable.

### Method B: Chocolatey

If you use Chocolatey, you can install the standard Vault CLI. 

> [!NOTE]
> The Chocolatey package typically installs the standard (OSS) binary. It is fully compatible with Enterprise servers for most client operations, but `vault --version` will not show the `+ent` suffix.

```powershell
# Open PowerShell as Administrator
choco install vault -y
```

[Back to Table of Contents](#table-of-contents)

## 4. Verify Installation

Check that Vault is installed and available in your path.

**Command:**

```bash
vault --version
```

**Expected Output:**

```text
Vault v1.21.2+ent (abc12345...), built 2026-01-22T12:00:00Z
```

**Enable Autocomplete (Optional):**

Enabling autocomplete allows you to press `TAB` to auto-fill commands and paths, significantly speeding up usage and reducing typos.

```bash
vault -autocomplete-install

exec $SHELL
```

[Back to Table of Contents](#table-of-contents)

## Troubleshooting

### Problem: "vault: command not found"

**Cause:** The installation directory (usually `/usr/bin/` or `/usr/local/bin/`) is not in your `$PATH`.

**Solution:** Add the binary location to your path or verify the installation command succeeded.

### Problem: GPG key error on Ubuntu

**Cause:** The keyring might be corrupted or the legacy `apt-key` method is conflicting.

**Solution:** Ensure you use the `signed-by` tag in your sources list as shown in step 2.

[Back to Table of Contents](#table-of-contents)

## See also

- [Getting Started with Vault CLI](../../tutorials/infrastructure/vault/getting-started-with-cli.md)
- [Vault CLI Reference](../../reference/vault/vault-cli.md)
