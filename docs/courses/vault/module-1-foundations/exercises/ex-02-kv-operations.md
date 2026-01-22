# Exercise 02: KV Operations

**[← Back to Module 1](../README.md)**

## Goal

Master CRUD operations with the KV v2 secrets engine.

## Prerequisites

- Vault dev server running
- Root token access

## Exercises

### Exercise 2.1: Create secrets

1. Create a secret at `secret/exercise/app1` with:
   - `db_host`: `localhost`
   - `db_port`: `5432`
   - `db_user`: `admin`
   - `db_pass`: `secretpassword`

2. Create a secret at `secret/exercise/app2` with:
   - `api_key`: `sk-test-123456`
   - `api_secret`: `shh-this-is-secret`

### Exercise 2.2: Read secrets

1. Read the full secret at `secret/exercise/app1`
2. Read only the `db_pass` field
3. Read the secret as JSON and extract just the data portion
4. List all secrets under `secret/exercise/`

### Exercise 2.3: Update secrets

1. Update `secret/exercise/app1` to change `db_pass` to `newpassword123`
2. Use `vault kv patch` to only update one field without replacing others
3. What is the new version number?

### Exercise 2.4: Versioning

1. Read version 1 of `secret/exercise/app1`
2. Read version 2 of `secret/exercise/app1`
3. Compare the `db_pass` values
4. Get the metadata to see all versions

### Exercise 2.5: Delete and recover

1. Soft delete `secret/exercise/app2`
2. Try to read it (should fail)
3. Check metadata (should show deletion_time)
4. Undelete it
5. Verify you can read it again
6. Permanently destroy version 1

## Deliverable

Commands and outputs demonstrating each operation.

---

[View Solution →](../solutions/sol-02-kv-operations.md)
