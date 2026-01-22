# Project 1: Password Manager

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Type](https://img.shields.io/badge/Type-Project-orange)

## Overview

Build a command-line password manager that stores credentials securely in Vault. This project reinforces the concepts from Module 1: Vault CLI operations, KV secrets engine, and basic policies.

## Learning objectives

- Apply Vault CLI commands in a practical context
- Design a secret path structure
- Create policies for different access levels
- Handle secret versioning and updates

## Requirements

### Functional requirements

1. **Store credentials**
   - Store username/password pairs for different services
   - Support additional fields (URL, notes, tags)
   - Organize credentials by category

2. **Retrieve credentials**
   - Get credentials for a specific service
   - List all stored services
   - Search by category or tag

3. **Update credentials**
   - Update password for a service
   - Update additional fields
   - Track version history

4. **Delete credentials**
   - Soft delete (recoverable)
   - Permanent delete option

5. **Access control**
   - Read-only policy for viewing passwords
   - Admin policy for full management

### Technical requirements

- Use Vault KV v2 secrets engine
- Implement as shell scripts (bash)
- Support JSON output for integration
- Use meaningful custom metadata

## Project structure

```
password-manager/
├── scripts/
│   ├── pm-add.sh        # Add new credentials
│   ├── pm-get.sh        # Get credentials
│   ├── pm-list.sh       # List all services
│   ├── pm-update.sh     # Update credentials
│   ├── pm-delete.sh     # Delete credentials
│   └── pm-search.sh     # Search credentials
├── policies/
│   ├── pm-readonly.hcl  # Read-only policy
│   └── pm-admin.hcl     # Admin policy
├── setup.sh             # Initial setup
└── README.md            # Usage documentation
```

## Implementation guide

### Step 1: Define secret structure

Design your path structure:

```
secret/password-manager/
├── services/
│   ├── github/
│   ├── aws/
│   └── database/
└── metadata/
    └── categories
```

Each service stores:
```json
{
  "username": "user@example.com",
  "password": "SecretPassword123",
  "url": "https://github.com",
  "notes": "Personal account",
  "category": "development"
}
```

### Step 2: Create setup script

```bash
#!/bin/bash
# setup.sh - Initialize password manager

set -e

echo "Setting up Password Manager..."

# Verify Vault connection
vault status > /dev/null || { echo "Error: Vault not accessible"; exit 1; }

# Create policies
vault policy write pm-readonly policies/pm-readonly.hcl
vault policy write pm-admin policies/pm-admin.hcl

echo "Creating sample entries..."
vault kv put secret/password-manager/services/example \
    username="demo@example.com" \
    password="DemoPassword123" \
    url="https://example.com" \
    notes="Demo entry" \
    category="demo"

vault kv metadata put \
    -custom-metadata=created_by="setup" \
    -custom-metadata=service_type="demo" \
    secret/password-manager/services/example

echo "Setup complete!"
```

### Step 3: Implement add command

```bash
#!/bin/bash
# pm-add.sh - Add new credentials

usage() {
    echo "Usage: pm-add.sh <service-name> [options]"
    echo "Options:"
    echo "  -u, --username    Username (required)"
    echo "  -p, --password    Password (prompted if not provided)"
    echo "  -l, --url         Service URL"
    echo "  -n, --notes       Additional notes"
    echo "  -c, --category    Category for organization"
    exit 1
}

# Parse arguments
SERVICE=""
USERNAME=""
PASSWORD=""
URL=""
NOTES=""
CATEGORY="uncategorized"

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username) USERNAME="$2"; shift 2 ;;
        -p|--password) PASSWORD="$2"; shift 2 ;;
        -l|--url) URL="$2"; shift 2 ;;
        -n|--notes) NOTES="$2"; shift 2 ;;
        -c|--category) CATEGORY="$2"; shift 2 ;;
        -*) usage ;;
        *) SERVICE="$1"; shift ;;
    esac
done

# Validate
[[ -z "$SERVICE" ]] && usage
[[ -z "$USERNAME" ]] && { echo "Username required"; usage; }

# Prompt for password if not provided
if [[ -z "$PASSWORD" ]]; then
    read -sp "Enter password: " PASSWORD
    echo
fi

# Store in Vault
vault kv put "secret/password-manager/services/$SERVICE" \
    username="$USERNAME" \
    password="$PASSWORD" \
    url="$URL" \
    notes="$NOTES" \
    category="$CATEGORY"

# Add metadata
vault kv metadata put \
    -custom-metadata="category=$CATEGORY" \
    -custom-metadata="created=$(date -Iseconds)" \
    "secret/password-manager/services/$SERVICE"

echo "Credentials for '$SERVICE' stored successfully."
```

### Step 4: Implement get command

```bash
#!/bin/bash
# pm-get.sh - Retrieve credentials

usage() {
    echo "Usage: pm-get.sh <service-name> [options]"
    echo "Options:"
    echo "  -f, --field       Get specific field only"
    echo "  -j, --json        Output as JSON"
    echo "  -v, --version     Get specific version"
    exit 1
}

SERVICE=""
FIELD=""
JSON=false
VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--field) FIELD="$2"; shift 2 ;;
        -j|--json) JSON=true; shift ;;
        -v|--version) VERSION="$2"; shift 2 ;;
        -*) usage ;;
        *) SERVICE="$1"; shift ;;
    esac
done

[[ -z "$SERVICE" ]] && usage

# Build command
CMD="vault kv get"
[[ -n "$FIELD" ]] && CMD="$CMD -field=$FIELD"
[[ "$JSON" == true ]] && CMD="$CMD -format=json"
[[ -n "$VERSION" ]] && CMD="$CMD -version=$VERSION"

$CMD "secret/password-manager/services/$SERVICE"
```

### Step 5: Create policies

**pm-readonly.hcl:**
```hcl
# Read-only access to password manager
path "secret/data/password-manager/services/*" {
  capabilities = ["read"]
}

path "secret/metadata/password-manager/services/*" {
  capabilities = ["read", "list"]
}
```

**pm-admin.hcl:**
```hcl
# Full admin access to password manager
path "secret/data/password-manager/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/password-manager/*" {
  capabilities = ["read", "list", "delete"]
}

path "secret/delete/password-manager/*" {
  capabilities = ["update"]
}

path "secret/undelete/password-manager/*" {
  capabilities = ["update"]
}

path "secret/destroy/password-manager/*" {
  capabilities = ["update"]
}
```

## Deliverables

1. **Working scripts** - All commands functional
2. **Policies** - Both read-only and admin policies
3. **Documentation** - README with usage examples
4. **Testing** - Demonstrate each command works

## Evaluation criteria

| Criterion | Points |
|-----------|--------|
| Functional requirements met | 40 |
| Policy implementation correct | 20 |
| Error handling | 15 |
| Code organization | 15 |
| Documentation | 10 |
| **Total** | 100 |

## Bonus challenges

1. **Password generation**: Add a `-g` flag to generate random passwords
2. **Export/import**: Export all credentials to encrypted file
3. **Expiration tracking**: Warn when passwords are old
4. **History view**: Show version history for a credential

## Testing your implementation

```bash
# Test add
./pm-add.sh github -u "me@example.com" -p "MyGitHubPass" -c "dev"

# Test get
./pm-get.sh github
./pm-get.sh github -f password
./pm-get.sh github -j

# Test list
./pm-list.sh
./pm-list.sh -c dev

# Test update
./pm-update.sh github -p "NewPassword123"

# Test delete
./pm-delete.sh github
./pm-delete.sh github --permanent

# Test with read-only user
PM_TOKEN=$(vault token create -policy=pm-readonly -format=json | jq -r '.auth.client_token')
VAULT_TOKEN=$PM_TOKEN ./pm-get.sh github      # Should work
VAULT_TOKEN=$PM_TOKEN ./pm-add.sh test -u x   # Should fail
```

## Submission

When complete:

1. Verify all scripts work
2. Test both policies
3. Document any design decisions
4. Submit the `password-manager/` directory

---

[← Back to Module 1](./README.md) | [Take Quiz →](./quiz-module-1.md)
