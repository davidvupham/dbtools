# Issue: Endpoint or Certificate Issues

**[← Back to AG Troubleshooting Index](../troubleshoot-availability-groups.md)**

## Symptoms
- Replicas show `DISCONNECTED` state
- Error 1418 or 35250 in error logs

## Diagnostic Steps

### 1. Check Endpoint Status
```sql
:r ../scripts/sql/check-endpoint-status.sql
```

### 2. Check Certificates
Ensure certificates haven't expired.
```sql
:r ../scripts/sql/check-certificate-expiry.sql
```

## Resolution
1. **Start Endpoint:** `ALTER ENDPOINT [Hadr_endpoint] STATE = STARTED;`
2. **Rotate Certificates:** If expired, create new certificates and exchange them across all replicas.
