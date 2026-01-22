# Module 2 Quiz: Authentication and Access Control

**[← Back to Module 2](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-2_Authentication-blue)
![Type](https://img.shields.io/badge/Type-Quiz-yellow)

## Instructions

- Answer all 15 questions
- Click on the answer to reveal the solution
- Aim for 80% or higher to pass

---

### Question 1

What are the three main token types in Vault?

<details>
<summary>Show Answer</summary>

**Service, Batch, and Periodic tokens**

- Service: Default, persisted, renewable
- Batch: Lightweight, not persisted, high performance
- Periodic: Can be renewed indefinitely

</details>

---

### Question 2

When a parent token is revoked, what happens to its child tokens?

<details>
<summary>Show Answer</summary>

**All child tokens are also revoked (cascading revocation)**

This is automatic unless the child tokens are orphans. Use `vault token create -orphan` to create tokens that survive parent revocation.

</details>

---

### Question 3

What are the two credentials required for AppRole authentication?

<details>
<summary>Show Answer</summary>

**Role ID and Secret ID**

- Role ID: Static identifier (like a username)
- Secret ID: Dynamic credential (like a password)

</details>

---

### Question 4

What does `secret_id_num_uses=1` configure in an AppRole role?

<details>
<summary>Show Answer</summary>

**The secret ID can only be used once**

After a single successful authentication, the secret ID is invalidated. This is a security best practice for production.

</details>

---

### Question 5

Which auth method is recommended for CI/CD pipelines?

<details>
<summary>Show Answer</summary>

**AppRole**

AppRole is designed for machine-to-machine authentication. For Kubernetes, use Kubernetes auth. For AWS, use AWS auth.

</details>

---

### Question 6

How do LDAP groups map to Vault access control?

<details>
<summary>Show Answer</summary>

**LDAP groups are mapped to Vault policies via group mappings**

```bash
vault write auth/ldap/groups/engineers policies="eng-policy"
```

When an LDAP user authenticates, Vault looks up their groups and attaches the mapped policies.

</details>

---

### Question 7

What is the purpose of a token accessor?

<details>
<summary>Show Answer</summary>

**A non-sensitive reference to a token for management operations**

Accessors can be used to look up or revoke tokens without knowing the actual token value. They appear in audit logs for security.

</details>

---

### Question 8

In templated policies, what does `{{identity.entity.name}}` resolve to?

<details>
<summary>Show Answer</summary>

**The name of the authenticated user's entity**

This allows policies like:
```hcl
path "secret/data/users/{{identity.entity.name}}/*"
```
Which gives each user access to their own path.

</details>

---

### Question 9

What is the difference between internal and external groups?

<details>
<summary>Show Answer</summary>

**Internal groups** are manually managed in Vault.

**External groups** are linked to groups from auth methods (LDAP, OIDC) via group aliases.

External groups sync membership from the external source.

</details>

---

### Question 10

How do you create a token that can be renewed forever?

<details>
<summary>Show Answer</summary>

**Create a periodic token with the `-period` flag**

```bash
vault token create -period=24h -policy=my-policy
```

Each renewal resets the TTL to the period value. The token never expires as long as it's renewed before the period ends.

</details>

---

### Question 11

What does response wrapping protect against?

<details>
<summary>Show Answer</summary>

**Man-in-the-middle attacks during secret delivery**

Wrapping encrypts the response with a one-time-use token. Only the intended recipient (with the wrapping token) can unwrap it.

</details>

---

### Question 12

In a policy, what does `required_parameters` do?

<details>
<summary>Show Answer</summary>

**Requires certain keys to be present in write operations**

```hcl
path "secret/data/apps/*" {
  capabilities = ["create", "update"]
  required_parameters = ["owner", "environment"]
}
```

Writes without these parameters will fail.

</details>

---

### Question 13

What is an entity alias?

<details>
<summary>Show Answer</summary>

**A link between an auth method identity and a Vault entity**

One entity can have multiple aliases (e.g., userpass "alice" and LDAP "alice@corp"). This allows a single identity across multiple auth methods.

</details>

---

### Question 14

How are policies from multiple groups combined for a token?

<details>
<summary>Show Answer</summary>

**Additively (union of all policies)**

If a user belongs to groups with policies A, B, and C, their token gets all capabilities from all three policies (unless `deny` is present).

</details>

---

### Question 15

What command checks what capabilities a token has on a path?

<details>
<summary>Show Answer</summary>

```bash
vault token capabilities <token> <path>
```

Or for the current token:
```bash
vault token capabilities <path>
```

Returns the list of capabilities (read, create, update, delete, list, etc.).

</details>

---

## Scoring

| Score | Result |
|-------|--------|
| 12-15 correct (80-100%) | Pass - Ready for Module 3 |
| 9-11 correct (60-79%) | Review weak areas, then proceed |
| Below 9 (< 60%) | Review Module 2 lessons |

---

[← Back to Module 2](./README.md) | [Start Module 3 →](../module-3-dynamic-secrets/README.md)
