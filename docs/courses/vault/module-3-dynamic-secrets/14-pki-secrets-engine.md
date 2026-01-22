# PKI Secrets Engine

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Lesson](https://img.shields.io/badge/Lesson-14-purple)

## Learning objectives

- Set up a PKI secrets engine as a certificate authority
- Create an intermediate CA
- Issue TLS certificates
- Configure certificate roles

## Overview

The PKI secrets engine generates X.509 certificates dynamically. It can act as a root CA or intermediate CA, issuing certificates on demand.

## PKI hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PKI HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌─────────────────────┐                              │
│                    │      Root CA        │  (offline, long TTL)         │
│                    │   pki/              │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│                               │ Signs                                    │
│                               ▼                                          │
│                    ┌─────────────────────┐                              │
│                    │  Intermediate CA    │  (online, medium TTL)        │
│                    │   pki_int/          │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│              ┌────────────────┼────────────────┐                        │
│              │                │                │                        │
│              ▼                ▼                ▼                        │
│       ┌──────────┐     ┌──────────┐     ┌──────────┐                   │
│       │  Server  │     │  Server  │     │  Client  │  (short TTL)      │
│       │   Cert   │     │   Cert   │     │   Cert   │                   │
│       └──────────┘     └──────────┘     └──────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Configuration

### Set up root CA

```bash
# Enable PKI for root
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki

# Generate root certificate
vault write -format=json pki/root/generate/internal \
    common_name="example.com" \
    ttl=87600h

# Configure URLs
vault write pki/config/urls \
    issuing_certificates="$VAULT_ADDR/v1/pki/ca" \
    crl_distribution_points="$VAULT_ADDR/v1/pki/crl"
```

### Set up intermediate CA

```bash
# Enable PKI for intermediate
vault secrets enable -path=pki_int pki
vault secrets tune -max-lease-ttl=43800h pki_int

# Generate CSR
vault write -format=json pki_int/intermediate/generate/internal \
    common_name="example.com Intermediate Authority" \
    | jq -r '.data.csr' > intermediate.csr

# Sign with root
vault write -format=json pki/root/sign-intermediate \
    csr=@intermediate.csr \
    format=pem_bundle \
    ttl="43800h" \
    | jq -r '.data.certificate' > intermediate.cert

# Set signed certificate
vault write pki_int/intermediate/set-signed \
    certificate=@intermediate.cert
```

### Create role

```bash
vault write pki_int/roles/web-server \
    allowed_domains="example.com" \
    allow_subdomains=true \
    max_ttl="720h"
```

## Issue certificates

```bash
vault write pki_int/issue/web-server \
    common_name="app.example.com" \
    ttl="24h"

# Output includes:
# - certificate
# - private_key
# - ca_chain
```

## Key takeaways

1. **Use intermediate CA for issuing** - Protect root CA
2. **Short TTLs for certificates** - Easier rotation
3. **Automate certificate issuance** - No manual CSR process
4. **Roles define what can be issued**

---

[← Previous: AWS Secrets](./13-aws-secrets-engine.md) | [Back to Module 3](./README.md) | [Next: Transit →](./15-transit-secrets-engine.md)
