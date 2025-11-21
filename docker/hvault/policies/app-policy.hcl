# Application Policy
# Provides read/write access to application-specific secrets
# Adjust paths according to your application requirements

# Read and write application secrets in KV v2
path "secret/data/app/*" {
  capabilities = ["create", "read", "update", "delete"]
}

path "secret/metadata/app/*" {
  capabilities = ["list", "read", "delete"]
}

# Read database credentials
path "database/creds/*" {
  capabilities = ["read"]
}

# Use transit encryption
path "transit/encrypt/*" {
  capabilities = ["update"]
}

path "transit/decrypt/*" {
  capabilities = ["update"]
}

# Allow token self-inspection and renewal
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/revoke-self" {
  capabilities = ["update"]
}
