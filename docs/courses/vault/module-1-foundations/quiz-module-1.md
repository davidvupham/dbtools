# Module 1 Quiz: Foundations

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Type](https://img.shields.io/badge/Type-Quiz-yellow)

## Instructions

- Answer all 15 questions
- Each question is worth equal points
- Click on the answer to reveal the solution
- Aim for 80% or higher to pass

---

## Questions

### Question 1: Secrets definition

What qualifies as a "secret" in the context of secrets management?

- A) Only passwords
- B) Only API keys
- C) Any sensitive data that grants access to systems or data
- D) Only encryption keys

<details>
<summary>Show Answer</summary>

**C) Any sensitive data that grants access to systems or data**

Secrets include passwords, API keys, tokens, certificates, encryption keys, and any other sensitive information that could grant unauthorized access if exposed.

</details>

---

### Question 2: Hardcoded secrets risk

Why are hardcoded secrets in source code dangerous?

- A) They make the code run slower
- B) They remain in Git history even after deletion
- C) They increase file size
- D) They prevent code compilation

<details>
<summary>Show Answer</summary>

**B) They remain in Git history even after deletion**

Even after removing hardcoded secrets, they persist in Git commit history forever. Anyone with repository access can find them using `git log -p`.

</details>

---

### Question 3: Vault architecture

Which layer in Vault's architecture encrypts all data before it reaches storage?

- A) HTTP API
- B) Auth Methods
- C) Barrier
- D) Secrets Engines

<details>
<summary>Show Answer</summary>

**C) Barrier**

The Barrier layer encrypts all data using AES-256-GCM before it leaves Vault for the storage backend. The storage backend only ever sees encrypted data.

</details>

---

### Question 4: Seal/Unseal

What happens when Vault is in a "sealed" state?

- A) All secrets are deleted
- B) The master key is encrypted and secrets cannot be accessed
- C) Only root users can access secrets
- D) Audit logging is disabled

<details>
<summary>Show Answer</summary>

**B) The master key is encrypted and secrets cannot be accessed**

When sealed, Vault's master key is encrypted. Without the master key in memory, Vault cannot decrypt any data, so no secrets can be read or written.

</details>

---

### Question 5: Shamir's Secret Sharing

With the default Shamir configuration (5 shares, threshold 3), what is required to unseal Vault?

- A) All 5 keys
- B) Any 3 of the 5 keys
- C) Only the root token
- D) The master key directly

<details>
<summary>Show Answer</summary>

**B) Any 3 of the 5 keys**

Shamir's Secret Sharing splits the master key into 5 shares, and any 3 can reconstruct it. This prevents any single person from having complete access.

</details>

---

### Question 6: Storage backends

Which storage backend is recommended for most Vault deployments?

- A) In-memory
- B) Consul
- C) Raft (Integrated Storage)
- D) PostgreSQL

<details>
<summary>Show Answer</summary>

**C) Raft (Integrated Storage)**

Raft is HashiCorp's recommended storage backend. It provides built-in high availability, requires no external dependencies, and is simpler to deploy than alternatives.

</details>

---

### Question 7: Dev mode

Which of the following is TRUE about Vault's development mode?

- A) It's suitable for production with proper configuration
- B) Data persists after restart
- C) It's auto-unsealed and uses in-memory storage
- D) It requires TLS certificates

<details>
<summary>Show Answer</summary>

**C) It's auto-unsealed and uses in-memory storage**

Dev mode is auto-unsealed, uses in-memory storage (data lost on restart), disables TLS, and uses a known root token. It's for development only, never production.

</details>

---

### Question 8: KV versions

What is a key difference between KV v1 and KV v2?

- A) KV v1 supports versioning, KV v2 does not
- B) KV v2 supports versioning and soft delete
- C) KV v1 is newer than KV v2
- D) KV v2 can only store strings

<details>
<summary>Show Answer</summary>

**B) KV v2 supports versioning and soft delete**

KV v2 adds versioning (automatic history of changes), soft delete (recoverable deletion), metadata support, and check-and-set operations.

</details>

---

### Question 9: KV v2 paths

When using KV v2 mounted at `secret/`, what is the correct API path to read a secret at `myapp/config`?

- A) `/v1/secret/myapp/config`
- B) `/v1/secret/data/myapp/config`
- C) `/v1/kv/myapp/config`
- D) `/v1/kv/data/myapp/config`

<details>
<summary>Show Answer</summary>

**B) `/v1/secret/data/myapp/config`**

KV v2 uses `/data/` for secret data and `/metadata/` for metadata. The CLI hides this, but the API path must include `data/`.

</details>

---

### Question 10: Soft delete

What is the difference between `vault kv delete` and `vault kv destroy` in KV v2?

- A) They are the same operation
- B) `delete` is soft delete (recoverable), `destroy` is permanent
- C) `destroy` deletes metadata, `delete` deletes data
- D) `delete` requires sudo, `destroy` does not

<details>
<summary>Show Answer</summary>

**B) `delete` is soft delete (recoverable), `destroy` is permanent**

`vault kv delete` performs a soft delete that can be recovered with `vault kv undelete`. `vault kv destroy` permanently removes data that cannot be recovered.

</details>

---

### Question 11: Policy default

What is Vault's default authorization behavior?

- A) Allow everything by default
- B) Deny everything by default
- C) Allow read, deny write by default
- D) Depends on the storage backend

<details>
<summary>Show Answer</summary>

**B) Deny everything by default**

Vault follows a deny-by-default model. Without explicit policy grants, all operations are denied (except for some basic paths in the `default` policy).

</details>

---

### Question 12: Capabilities

Which capability is needed to create new secrets at a path?

- A) `read`
- B) `write`
- C) `create`
- D) `new`

<details>
<summary>Show Answer</summary>

**C) `create`**

The capability `create` allows creating new data at a path. Note: `write` is not a valid capability; the actual capabilities are `create`, `read`, `update`, `delete`, `list`, `sudo`, and `deny`.

</details>

---

### Question 13: Deny capability

What happens when a token has multiple policies, and one policy grants `read` while another has `deny` for the same path?

- A) `read` wins because it was granted first
- B) `deny` always takes precedence
- C) The last policy evaluated wins
- D) An error is returned

<details>
<summary>Show Answer</summary>

**B) `deny` always takes precedence**

The `deny` capability always overrides all other capabilities, regardless of what other policies grant. This allows creating explicit deny rules.

</details>

---

### Question 14: Policy paths

Which policy path correctly grants read access to ALL secrets under `secret/myapp/` in KV v2?

- A) `path "secret/myapp/*"`
- B) `path "secret/data/myapp/*"`
- C) `path "secret/+/myapp/*"`
- D) `path "kv/data/myapp/*"`

<details>
<summary>Show Answer</summary>

**B) `path "secret/data/myapp/*"`**

For KV v2, you must include `data/` in policy paths. The path `secret/myapp/*` would not match the actual API paths used.

</details>

---

### Question 15: Token policies

How are multiple policies on a token combined?

- A) Only the first policy is used
- B) Policies are merged (union), except deny overrides
- C) The most restrictive policy wins
- D) Policies are evaluated randomly

<details>
<summary>Show Answer</summary>

**B) Policies are merged (union), except deny overrides**

Multiple policies are additive - capabilities are combined. If policy A grants `read` and policy B grants `update`, the token has both. However, `deny` always overrides any grants.

</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 12-15 correct (80-100%) | Pass - Ready for Module 2 |
| 9-11 correct (60-79%) | Review weak areas, then proceed |
| Below 9 (< 60%) | Review Module 1 lessons before continuing |

---

## Review resources

If you scored below 80%, review these sections:

- **Questions 1-2**: [Lesson 01: Introduction](./01-introduction-to-secrets-management.md)
- **Questions 3-7**: [Lesson 02: Architecture](./02-vault-architecture.md) and [Lesson 03: Dev Environment](./03-vault-dev-environment.md)
- **Questions 8-10**: [Lesson 04: Secrets Engines](./04-secrets-engines-basics.md)
- **Questions 11-15**: [Lesson 05: Policies](./05-vault-policies-intro.md)

---

**Congratulations on completing Module 1!**

[← Back to Module 1](./README.md) | [Start Module 2 →](../module-2-authentication/README.md)
