# Exercise 01: CLI Basics

**[← Back to Module 1](../README.md)**

## Goal

Practice fundamental Vault CLI commands and understand the request-response flow.

## Prerequisites

- Vault dev server running
- `VAULT_ADDR` and `VAULT_TOKEN` configured

## Exercises

### Exercise 1.1: Server status

1. Check Vault's seal status and note all the fields returned
2. Extract just the `sealed` value using JSON output
3. What does each field mean?

### Exercise 1.2: Token information

1. Look up information about your current token
2. What policies does it have?
3. What is the token's TTL?

### Exercise 1.3: Secrets engines

1. List all enabled secrets engines
2. What path is the KV v2 engine mounted at?
3. Enable a new KV v2 engine at path `myengine/`
4. Verify it appears in the list
5. Disable it (warning: this deletes data)

### Exercise 1.4: Auth methods

1. List all enabled authentication methods
2. What is the default auth method?
3. Enable the userpass auth method
4. Verify it's enabled

### Exercise 1.5: Environment variables

1. Unset `VAULT_TOKEN` and try to run `vault status`
2. What happens?
3. Try `vault kv get secret/test` without the token
4. Set the token back and verify commands work

## Deliverable

Write commands and output for each exercise.

---

[View Solution →](../solutions/sol-01-cli-basics.md)
