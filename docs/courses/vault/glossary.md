# Vault Glossary

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Vault-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick-reference.md) | [Troubleshooting](./troubleshooting.md)

## Core concepts

| Term | Definition |
|------|------------|
| **Vault** | HashiCorp's secrets management platform for storing, accessing, and distributing secrets |
| **Secret** | Any sensitive data: passwords, API keys, certificates, encryption keys, or database credentials |
| **Secrets Engine** | Component that stores, generates, or encrypts data (e.g., KV, Database, Transit, PKI) |
| **Auth Method** | Mechanism for authenticating users or applications to Vault (e.g., Token, AppRole, LDAP) |
| **Policy** | Rules defining what secrets a token can access and what operations it can perform |
| **Token** | Authentication credential issued by Vault after successful authentication |

## Secrets engines

| Term | Definition |
|------|------------|
| **KV (Key-Value)** | Secrets engine for storing arbitrary key-value pairs |
| **KV v1** | Simple key-value store without versioning |
| **KV v2** | Key-value store with versioning, soft delete, and metadata |
| **Database** | Secrets engine that generates dynamic database credentials |
| **Transit** | Encryption-as-a-service engine for encrypting/decrypting data without storing it |
| **PKI** | Secrets engine for generating X.509 certificates |
| **AWS** | Secrets engine for generating dynamic AWS credentials |
| **SSH** | Secrets engine for managing SSH credentials and certificates |

## Authentication

| Term | Definition |
|------|------------|
| **Token Auth** | Default auth method using Vault tokens directly |
| **AppRole** | Auth method for machines/applications using role ID and secret ID |
| **Userpass** | Auth method using username and password |
| **LDAP** | Auth method integrating with LDAP/Active Directory |
| **OIDC** | Auth method using OpenID Connect providers |
| **Kubernetes** | Auth method using Kubernetes service account tokens |
| **AWS IAM** | Auth method using AWS IAM credentials |

## Tokens and leases

| Term | Definition |
|------|------------|
| **Root Token** | Superuser token with unlimited access (created during initialization) |
| **Service Token** | Standard token for authenticating to Vault |
| **Batch Token** | Lightweight, non-persistent token for high-performance workloads |
| **Orphan Token** | Token without a parent (doesn't get revoked when parent is revoked) |
| **TTL (Time To Live)** | Duration a token or secret is valid before expiring |
| **Lease** | Metadata attached to dynamic secrets tracking TTL and renewal |
| **Lease ID** | Unique identifier for a lease, used for renewal and revocation |
| **Renewal** | Extending the TTL of a token or lease |
| **Revocation** | Immediately invalidating a token or lease |

## Policies

| Term | Definition |
|------|------------|
| **Capability** | Permission type: `create`, `read`, `update`, `delete`, `list`, `sudo`, `deny` |
| **Path** | The API path that a policy applies to (e.g., `secret/data/myapp/*`) |
| **Glob** | Wildcard pattern in paths (`*` matches any character sequence) |
| **Default Policy** | Built-in policy attached to all tokens (provides basic self-management) |
| **Root Policy** | Built-in superuser policy with all capabilities on all paths |

## Server operations

| Term | Definition |
|------|------------|
| **Seal** | State where Vault's master key is encrypted and Vault cannot decrypt secrets |
| **Unseal** | Process of providing unseal keys to decrypt the master key |
| **Unseal Key** | Key shard needed to unseal Vault (usually 3 of 5 required) |
| **Master Key** | Key used to decrypt the encryption key that protects all secrets |
| **Shamir's Secret Sharing** | Algorithm that splits the master key into multiple shards |
| **Auto-Unseal** | Using an external service (AWS KMS, Azure Key Vault) to automatically unseal |
| **Barrier** | Encryption layer that protects all data at rest |

## High availability

| Term | Definition |
|------|------------|
| **HA (High Availability)** | Running multiple Vault servers for redundancy |
| **Active Node** | The Vault server handling all requests in an HA cluster |
| **Standby Node** | Vault server waiting to take over if the active node fails |
| **Raft** | Integrated storage backend providing HA and persistent storage |
| **Consul** | HashiCorp's service mesh that can serve as Vault's storage backend |
| **Cluster** | Group of Vault servers working together for HA |
| **Leader Election** | Process of selecting which node becomes active |

## Dynamic secrets

| Term | Definition |
|------|------------|
| **Dynamic Secret** | Credential generated on-demand with automatic expiration |
| **Static Secret** | Manually created and stored credential (like in KV) |
| **Role** | Configuration defining how dynamic credentials are generated |
| **Connection** | Configuration for connecting to an external system (e.g., database) |
| **Rotation** | Automatically changing credentials periodically |

## Security features

| Term | Definition |
|------|------------|
| **Audit Device** | Logging mechanism for all Vault requests and responses |
| **Audit Log** | Record of all operations performed on Vault |
| **Response Wrapping** | Encrypting a response so only the intended recipient can access it |
| **Wrapped Token** | Single-use token that unwraps to reveal the actual response |
| **Cubbyhole** | Per-token private storage that only that token can access |
| **Namespace** | Logical isolation within Vault (Enterprise feature) |

## Transit encryption

| Term | Definition |
|------|------------|
| **Encryption Key** | Key used by Transit to encrypt/decrypt data |
| **Key Ring** | Collection of key versions for a named key |
| **Key Rotation** | Creating a new version of an encryption key |
| **Convergent Encryption** | Encryption where same plaintext produces same ciphertext |
| **Derived Key** | Key created from a named key using additional context |
| **Rewrap** | Re-encrypting ciphertext with the latest key version |

## PKI (certificates)

| Term | Definition |
|------|------------|
| **Root CA** | Top-level certificate authority in a PKI hierarchy |
| **Intermediate CA** | CA signed by root CA, used to issue end-entity certificates |
| **End-Entity Certificate** | Certificate issued to servers, services, or users |
| **CSR (Certificate Signing Request)** | Request for a certificate containing the public key |
| **CRL (Certificate Revocation List)** | List of revoked certificates |
| **OCSP** | Online Certificate Status Protocol for checking certificate validity |
| **Common Name (CN)** | Primary identifier in a certificate (often the domain name) |
| **SAN (Subject Alternative Name)** | Additional identifiers (domains, IPs) in a certificate |

## API and CLI

| Term | Definition |
|------|------------|
| **VAULT_ADDR** | Environment variable specifying the Vault server address |
| **VAULT_TOKEN** | Environment variable containing the authentication token |
| **HTTP API** | RESTful interface for all Vault operations |
| **Vault CLI** | Command-line interface for interacting with Vault |
| **SDK** | Software Development Kit for programmatic Vault access |

## Integration patterns

| Term | Definition |
|------|------------|
| **Vault Agent** | Daemon that handles authentication and secret caching |
| **Agent Sidecar** | Vault Agent running alongside an application in Kubernetes |
| **Template** | Consul Template-style file for rendering secrets to disk |
| **Injector** | Kubernetes mutating webhook that injects Vault Agent sidecars |
| **CSI Provider** | Container Storage Interface driver for mounting secrets as volumes |
| **Envconsul** | Tool for populating environment variables from Vault |

---

[← Back to Course Index](./README.md)
