# Exercise 03: Policies

**[← Back to Module 1](../README.md)**

## Goal

Write and apply Vault policies for access control.

## Prerequisites

- Vault dev server running
- Root token access

## Exercises

### Exercise 3.1: View built-in policies

1. List all policies
2. Read the `default` policy
3. What paths does the default policy grant access to?

### Exercise 3.2: Create a read-only policy

Create a policy named `readonly` that:
- Allows `read` on `secret/data/public/*`
- Allows `list` on `secret/metadata/public/*`
- Denies everything else (implicit)

### Exercise 3.3: Create a write policy

Create a policy named `writer` that:
- Allows `create`, `update`, `delete` on `secret/data/team/*`
- Allows `read`, `list` on `secret/metadata/team/*`
- Explicitly denies access to `secret/data/team/admin/*`

### Exercise 3.4: Test policies

1. Create test secrets:
   - `secret/public/info` with `message=hello`
   - `secret/team/config` with `setting=value`
   - `secret/team/admin/creds` with `password=secret`

2. Create tokens with each policy:
   ```bash
   READONLY_TOKEN=$(vault token create -policy=readonly -format=json | jq -r '.auth.client_token')
   WRITER_TOKEN=$(vault token create -policy=writer -format=json | jq -r '.auth.client_token')
   ```

3. Test what each token can do:
   - Can `readonly` read `secret/public/info`?
   - Can `readonly` write to `secret/public/info`?
   - Can `writer` read `secret/team/config`?
   - Can `writer` write to `secret/team/config`?
   - Can `writer` read `secret/team/admin/creds`?

### Exercise 3.5: Check capabilities

1. Use `vault token capabilities` to check what the `readonly` token can do at various paths
2. Do the same for the `writer` token
3. Compare with your expected results

## Deliverable

1. Your policy HCL files
2. Test results showing what works and what doesn't
3. Capability check outputs

---

[View Solution →](../solutions/sol-03-policies.md)
