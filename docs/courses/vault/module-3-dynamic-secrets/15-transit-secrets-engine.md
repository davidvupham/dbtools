# Transit Secrets Engine

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Lesson](https://img.shields.io/badge/Lesson-15-purple)

## Learning objectives

- Use Transit for encryption-as-a-service
- Manage encryption keys
- Implement key rotation
- Understand convergent encryption

## Overview

The Transit secrets engine handles cryptographic functions without exposing encryption keys. Applications send data to Vault for encryption/decryption.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TRANSIT ENCRYPTION FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ENCRYPTION                                                            │
│   ┌─────────┐    plaintext="secret"    ┌─────────┐                     │
│   │   App   │ ─────────────────────▶   │  Vault  │                     │
│   │         │                          │ Transit │                     │
│   │         │ ◀─────────────────────   │         │                     │
│   └─────────┘    "vault:v1:abc..."     └─────────┘                     │
│                                                                          │
│   • App never sees encryption key                                       │
│   • Vault handles all crypto                                            │
│   • Ciphertext includes version                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Configuration

### Enable Transit

```bash
vault secrets enable transit
```

### Create encryption key

```bash
# Create a key
vault write -f transit/keys/my-key

# Create with specific type
vault write transit/keys/my-key type=aes256-gcm96
```

## Operations

### Encrypt

```bash
# Plaintext must be base64 encoded
vault write transit/encrypt/my-key \
    plaintext=$(echo -n "secret data" | base64)

# Output:
# ciphertext    vault:v1:8SDd3WHDOjf7mq69...
```

### Decrypt

```bash
vault write transit/decrypt/my-key \
    ciphertext="vault:v1:8SDd3WHDOjf7mq69..."

# Output (base64):
# plaintext    c2VjcmV0IGRhdGE=

# Decode:
echo "c2VjcmV0IGRhdGE=" | base64 -d
# secret data
```

### Key rotation

```bash
# Rotate to new key version
vault write -f transit/keys/my-key/rotate

# Old ciphertext still decryptable
# New encryptions use latest version

# Rewrap old ciphertext with new key
vault write transit/rewrap/my-key \
    ciphertext="vault:v1:old..."

# Output: vault:v2:new...
```

## Key takeaways

1. **Encryption without key exposure** - Keys never leave Vault
2. **Key versioning** - Ciphertext tagged with key version
3. **Rotation without re-encryption** - Old data still decryptable
4. **Rewrap for compliance** - Update ciphertext to latest key

---

## Module 3 complete!

Congratulations! Complete:
1. [Project 3: DB Connection Manager](./project-3-db-connection-manager.md)
2. [Module 3 Quiz](./quiz-module-3.md)

[← Previous: PKI](./14-pki-secrets-engine.md) | [Back to Module 3](./README.md) | [Project 3 →](./project-3-db-connection-manager.md)
