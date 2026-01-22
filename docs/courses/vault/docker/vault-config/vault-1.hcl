# Vault Server Configuration - Node 1 (Primary)
# Used for HA cluster labs in Module 4 Track C

ui = true
disable_mlock = true

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}

storage "raft" {
  path    = "/vault/data"
  node_id = "vault-1"
}

api_addr     = "http://vault-1:8200"
cluster_addr = "http://vault-1:8201"

# Audit logging
# Enable via CLI: vault audit enable file file_path=/vault/logs/audit.log
