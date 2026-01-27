# Getting Started with Vault CLI

**[← Back to Vault Tutorials](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 26, 2026
> **Maintainers:** Database Tools Team
> **Status:** Production

<div align="center">

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-How--To-green)

</div>

> **Goal:** Learn how to authenticate and perform basic secret operations using the Vault CLI.
> **Prerequisites:** 
> - A generic Vault instance that is operational and available.
> - Vault CLI installed locally (see [Installation Guide](../../../how-to/vault/install-vault-cli.md)).
> - Your specific access details (Namespace, Role, Auth Method).

## Table of Contents

- [1. Log in with SAML](#1-log-in-with-saml)
- [2. List secrets engines](#2-list-secrets-engines)
- [3. Write secrets](#3-write-secrets)
- [4. Read secrets](#4-read-secrets)
- [5. List secrets](#5-list-secrets)
- [Summary of Commands](#summary-of-commands)

## Steps

## 1. Log in with SAML

To log in using SAML with a specific namespace and role, use the `vault login` command with the `-method=saml` flag.

> [!IMPORTANT]
> **Enterprise Feature:** The SAML authentication method is a feature of **HashiCorp Vault Enterprise**. Ensure your Vault client and server are the appropriate version.

**Command Structure:**

```bash
export VAULT_ADDR="https://your-vault-url.com"
export VAULT_NAMESPACE="<namespace>"

vault login -method=saml role=<your-role>
```

**Example:**

Based on your provided details:
- **Namespace:** `abc`
- **Method:** `SAML`
- **Role:** `myteamrole`

Run the following command:

```bash
# Set your Vault address and namespace first
export VAULT_ADDR="https://vault.example.com" # Replace with your actual URL
export VAULT_NAMESPACE="abc"

# Perform the login
vault login -method=saml role=myteamrole
```

Depending on your environment, a browser window may open automatically. If not, the CLI will output a URL that you must **copy and paste** into your browser to complete the authentication. Once successful, Vault will return a token which is automatically stored in `~/.vault-token`.

[Back to Table of Contents](#table-of-contents)

## 2. List secrets engines

Before reading or writing secrets, it's helpful to know where secrets are stored. Limits are organized into "Secrets Engines" mounted at specific paths.

To see all enabled secrets engines:

```bash
vault secrets list
```

**Output Example:**

```text
Path          Type         Accessor              Description
----          ----         --------              -----------
cubbyhole/    cubbyhole    cubbyhole_12345       Per-token private secret storage
identity/     identity     identity_abc123       Identity store
secret/       kv           kv_12345678           key-value secret storage
sys/          system       system_567890         System endpoints used for control, policy and debugging
```

In this example, `secret/` is a Key-Value (KV) store where you can read and write secrets.

[Back to Table of Contents](#table-of-contents)

## 3. Write secrets

Most Vault setups use the Key-Value v2 (KV2) engine. To store a secret, use `vault kv put`.

**Command:**

```bash
# Syntax: vault kv put <path> <key>=<value>
vault kv put secret/myapp/config username="admin" password="supersecretpassword"
```

**Output:**

```text
Key              Value
---              -----
created_time     2023-10-27T10:00:00.000Z
deletion_time    n/a
destroyed        false
version          1
```

[Back to Table of Contents](#table-of-contents)

## 4. Read secrets

To retrieve the secret you just stored, use `vault kv get`.

**Command:**

```bash
# Syntax: vault kv get <path>
vault kv get secret/myapp/config
```

**Output:**

```text
====== Metadata ======
Key              Value
---              -----
created_time     2023-10-27T10:00:00.000Z
version          1

====== Data ======
Key         Value
---         -----
password    supersecretpassword
username    admin
```

To read just the value of a specific field (useful for scripts):

```bash
vault kv get -field=password secret/myapp/config
```

[Back to Table of Contents](#table-of-contents)

## 5. List secrets

To see what secrets exist at a specific path, use `vault kv list`. Note that this only lists the *keys* (names of secrets) at that path, effectively acting like `ls` for your secrets.

**Command:**

```bash
# Syntax: vault kv list <path>
vault kv list secret/myapp/
```

**Output:**

```text
Keys
----
config
database
```

[Back to Table of Contents](#table-of-contents)

## Summary of Commands

| Action | Command |
| :--- | :--- |
| **Login (SAML)** | `vault login -method=saml role=myteamrole` |
| **List Engines** | `vault secrets list` |
| **Write Secret** | `vault kv put secret/path key=value` |
| **List Secrets** | `vault kv list secret/path` |
| **Read Secret** | `vault kv get secret/path` |
