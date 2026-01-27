# Read-Only Policy
# Provides read-only access to secrets and configurations
# Suitable for monitoring, auditing, or read-only applications

# Read secret engines configuration
path "sys/mounts" {
  capabilities = ["read"]
}

# Read auth methods configuration
path "sys/auth" {
  capabilities = ["read"]
}

# Read policies
path "sys/policies" {
  capabilities = ["read"]
}

path "sys/policies/*" {
  capabilities = ["read"]
}

# Read health status
path "sys/health" {
  capabilities = ["read"]
}

# Read secrets from KV v2 (secret/)
path "secret/data/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/*" {
  capabilities = ["read", "list"]
}

# Read secrets from KV v2 (kv/)
path "kv/data/*" {
  capabilities = ["read", "list"]
}

path "kv/metadata/*" {
  capabilities = ["read", "list"]
}

# Allow token self-inspection
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Allow token renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}
