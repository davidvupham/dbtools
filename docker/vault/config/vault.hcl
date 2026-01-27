# HashiCorp Vault Server Configuration
# Production Hardening Best Practices Applied
# https://developer.hashicorp.com/vault/docs/concepts/production-hardening

# Listener Configuration
# IMPORTANT: TLS should be enabled in production
# For development/testing, TLS is disabled below
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1

  # Production TLS Configuration (uncomment and configure for production):
  # tls_disable      = 0
  # tls_cert_file    = "/vault/certs/vault.crt"
  # tls_key_file     = "/vault/certs/vault.key"
  # tls_min_version  = "tls13"

  # Security headers
  # tls_require_and_verify_client_cert = false
  # tls_client_ca_file                 = "/vault/certs/ca.crt"

  # Performance tuning
  # tls_prefer_server_cipher_suites = false
}

# Storage Backend Configuration
# File storage is simple but not suitable for HA production deployments
# Consider using Consul, Raft Integrated Storage, or cloud-native options for HA
storage "file" {
  path = "/vault/file"
}

# Alternative: Raft Integrated Storage (recommended for HA)
# storage "raft" {
#   path    = "/vault/file"
#   node_id = "vault1"
#
#   # Retry join for cluster formation
#   retry_join {
#     leader_api_addr = "http://vault2:8200"
#   }
# }

# Memory Lock Configuration
# disable_mlock = false is critical for security
# Prevents sensitive data from being swapped to disk
# In containers, ensure IPC_LOCK capability is granted
disable_mlock = false

# UI Configuration
ui = true

# API and Cluster Addresses
# These must be reachable by other Vault nodes and clients
api_addr     = "http://0.0.0.0:8200"
cluster_addr = "http://0.0.0.0:8201"

# Logging Configuration
# Use structured logging (json) for better parsing and monitoring
log_level  = "info"
log_format = "json"

# Performance and Operational Settings
default_lease_ttl = "168h"  # 7 days
max_lease_ttl     = "720h"  # 30 days

# Telemetry Configuration
# Enable metrics collection for monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname          = false

  # Uncomment to enable statsd/statsite
  # statsd_address = "localhost:8125"
}

# Auto-unseal Configuration (Production Best Practice)
# Eliminates manual unseal process and improves automation
# Examples for different cloud providers:

# AWS KMS Auto-unseal
# seal "awskms" {
#   region     = "us-east-1"
#   kms_key_id = "12345678-abcd-1234-abcd-123456789012"
# }

# Azure Key Vault Auto-unseal
# seal "azurekeyvault" {
#   tenant_id      = "46646709-b63e-4747-be42-516edeaf1e14"
#   client_id      = "03dc33fc-16d9-4b77-8152-3ec568f8af6e"
#   client_secret  = "DUJDS3..."
#   vault_name     = "hc-vault"
#   key_name       = "vault_key"
# }

# GCP Cloud KMS Auto-unseal
# seal "gcpckms" {
#   project     = "vault-project"
#   region      = "us-central1"
#   key_ring    = "vault-keyring"
#   crypto_key  = "vault-key"
# }
