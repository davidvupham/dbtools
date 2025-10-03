# gds-hvault Enhancement Recommendations

Based on research of the `hvac` library and HashiCorp Vault best practices, here are recommended enhancements for `gds_hvault`.

## Current Features
- ✅ AppRole authentication
- ✅ KV v1/v2 secret retrieval
- ✅ Basic error handling

## Recommended Enhancements

### 1. Token Management
Add support for token operations commonly needed in applications:

- **Token renewal**: Automatically renew tokens before expiration
- **Token caching**: Cache tokens to avoid repeated authentication
- **Token revocation**: Clean up tokens when done

### 2. Additional Authentication Methods
While AppRole is common for automation, consider adding:

- **Token-based auth**: Direct token usage (simplest for dev/testing)
- **Kubernetes auth**: For apps running in K8s
- **LDAP/Userpass**: For interactive use cases

### 3. Enhanced Secret Operations
Expand beyond just reading secrets:

- **Write secrets**: Create/update secrets (with proper permissions)
- **Delete secrets**: Remove secrets when needed
- **List secrets**: Discover available secrets
- **Secret versioning**: Work with KV v2 versions explicitly

### 4. Error Handling & Retry Logic
- **Exponential backoff**: Retry failed requests with backoff
- **Connection pooling**: Reuse HTTP connections
- **Timeout configuration**: Configurable timeouts
- **Better error messages**: More context in exceptions

### 5. Configuration Management
- **Config file support**: Load settings from file
- **Multiple Vault instances**: Support connecting to different Vaults
- **Namespace support**: Vault Enterprise namespace handling
- **Mount point customization**: Flexible secret engine paths

### 6. Security Features
- **Certificate verification**: Proper TLS/SSL handling
- **Client certificates**: mTLS support
- **Token wrapping**: Response wrapping for added security
- **Lease management**: Handle lease renewals automatically

### 7. Convenience Features
- **Context manager**: Use with `with` statement for auto-cleanup
- **Secret caching**: Optional local caching with TTL
- **Batch operations**: Fetch multiple secrets efficiently
- **Environment variable defaults**: Smart defaults from env vars

### 8. Observability
- **Logging**: Structured logging for troubleshooting
- **Metrics**: Track API calls, latency, errors
- **Health checks**: Verify Vault connectivity

## Priority Implementation Order

### Phase 1 (Essential)
1. Token caching and renewal
2. Better error handling with retries
3. Certificate verification
4. Structured logging

### Phase 2 (Useful)
1. Write/update/delete secrets
2. List secrets functionality
3. Config file support
4. Context manager

### Phase 3 (Advanced)
1. Additional auth methods
2. Namespace support
3. Batch operations
4. Metrics and monitoring

## Example Enhanced API

```python
from gds_hvault import VaultClient

# Initialize with more options
client = VaultClient(
    vault_addr="https://vault.example.com",
    role_id="my-role-id",
    secret_id="my-secret-id",
    mount_point="secret",
    verify_ssl=True,
    timeout=10,
    max_retries=3
)

# Context manager support
with client:
    # Read secret
    secret = client.read_secret("myapp/db")
    
    # Write secret
    client.write_secret("myapp/api", {"key": "value"})
    
    # List secrets
    secrets = client.list_secrets("myapp/")
    
    # Get specific version (KV v2)
    old_secret = client.read_secret("myapp/db", version=2)

# Token automatically revoked on exit
```

## References
- [hvac library](https://github.com/hvac/hvac)
- [Vault API documentation](https://www.vaultproject.io/api-docs)
- [AppRole auth method](https://www.vaultproject.io/docs/auth/approle)
- [KV secrets engine](https://www.vaultproject.io/docs/secrets/kv)
