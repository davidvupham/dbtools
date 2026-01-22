# Module 3 Quiz: Dynamic Secrets

**[← Back to Module 3](./README.md)**

## Questions

### Question 1

What is the main benefit of dynamic secrets over static secrets?

<details>
<summary>Answer</summary>

**Limited blast radius** - Dynamic secrets have short TTLs and are unique per request, so compromised credentials expire quickly and can be traced to a specific client.

</details>

### Question 2

What components make up a Vault lease?

<details>
<summary>Answer</summary>

- `lease_id`: Unique identifier
- `lease_duration`: Time until expiration
- `renewable`: Whether it can be extended

</details>

### Question 3

In the database secrets engine, what SQL template variables are available?

<details>
<summary>Answer</summary>

- `{{name}}`: Username to create
- `{{password}}`: Generated password
- `{{expiration}}`: Timestamp when credentials expire

</details>

### Question 4

What is the difference between `iam_user` and `assumed_role` in AWS secrets?

<details>
<summary>Answer</summary>

- `iam_user`: Creates an actual IAM user (persistent until revoked)
- `assumed_role`: Uses STS AssumeRole for temporary credentials (no IAM user created)

</details>

### Question 5

Why use an intermediate CA instead of issuing from root CA?

<details>
<summary>Answer</summary>

**Security isolation** - The root CA can be kept offline/secure. If the intermediate CA is compromised, only that intermediate needs to be revoked, not the entire PKI.

</details>

### Question 6

What does the Transit engine's `rewrap` operation do?

<details>
<summary>Answer</summary>

**Re-encrypts ciphertext with the latest key version** without exposing the plaintext. Useful for key rotation compliance.

</details>

---

[← Back to Module 3](./README.md) | [Start Module 4 →](../module-4-applied/README.md)
