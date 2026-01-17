# Security Demo: Hardened Container

This example demonstrates Docker security best practices.

## Files

- `Dockerfile` - A security-hardened Node.js container
- `docker-compose.yml` - Compose file with security options
- `server.js` - Simple HTTP server

## Security Features Demonstrated

1. **Non-root user** - Runs as `appuser` (UID 1000)
2. **Read-only filesystem** - `/` is read-only
3. **Dropped capabilities** - All capabilities dropped
4. **No privilege escalation** - `no-new-privileges` enabled
5. **Minimal base image** - Uses Alpine
6. **Health check** - Built-in health monitoring

## Usage

```bash
# Build and run
docker compose up -d

# Verify security settings
docker inspect security-demo-web-1 | jq '.[0].HostConfig.SecurityOpt'
docker exec security-demo-web-1 whoami  # Should print: appuser

# Test read-only (should fail)
docker exec security-demo-web-1 touch /test.txt
# touch: /test.txt: Read-only file system

# Clean up
docker compose down
```
