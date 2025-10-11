# Snowflake Connectivity Testing Guide

## Overview
This guide is part of the DBTools workspace. The monitoring script includes comprehensive connectivity testing to detect network issues, account availability, and authentication problems before attempting replication monitoring.

## Best Practices for Snowflake Connectivity Testing

### 1. **Lightweight Test Queries**
The connectivity test uses minimal resource queries:
- `SELECT 1` - Basic connectivity test
- `CURRENT_ACCOUNT()`, `CURRENT_USER()`, etc. - Account information retrieval

### 2. **Timeout Configuration**
- Default timeout: 30 seconds
- Configurable via `--connectivity-timeout` parameter
- Separate timeouts for login and network operations

### 3. **Comprehensive Diagnostics**
The test provides detailed information:
- Response time measurement
- Account information (name, user, role, warehouse, region, version)
- Error details for troubleshooting

## Usage Examples

### 1. Test Connectivity Only
```bash
# Basic connectivity test
python monitor_snowflake_replication.py myaccount --test-connectivity

# With custom timeout
python monitor_snowflake_replication.py myaccount --test-connectivity --connectivity-timeout 60
```

### 2. Integrated Monitoring (Default)
The connectivity test is automatically performed before each monitoring cycle:

```bash
# Continuous monitoring with connectivity checks
python monitor_snowflake_replication.py myaccount

# One-time monitoring with connectivity check
python monitor_snowflake_replication.py myaccount --once
```

### 3. Environment Variables Setup
```bash
# Set Snowflake credentials
export SNOWFLAKE_USER="monitor_user"
export SNOWFLAKE_ACCOUNT="myaccount"

# Set Vault configuration for RSA key authentication
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_SECRET_PATH="data/snowflake"
export VAULT_MOUNT_POINT="secret"

# Test connectivity
python monitor_snowflake_replication.py myaccount --test-connectivity
```

## Connectivity Test Results

### Success Example
```
INFO - Starting connectivity check for account: myaccount
INFO - ✓ Connectivity test PASSED for myaccount (response time: 1250.45ms)
INFO -   - Account: MYACCOUNT
INFO -   - User: MONITOR_USER
INFO -   - Role: MONITOR_ROLE
INFO -   - Warehouse: COMPUTE_WH
INFO -   - Region: AWS_US_WEST_2
INFO -   - Version: 8.23.1
```

### Failure Example
```
ERROR - ✗ Connectivity test FAILED for myaccount (response time: 30000.00ms)
ERROR -   Error: 250001 (08001): Failed to connect to DB: myaccount.snowflakecomputing.com:443
```

## What the Connectivity Test Detects

### 1. **Network Issues**
- DNS resolution problems
- Firewall blocking
- Internet connectivity issues
- Proxy configuration problems

### 2. **Authentication Problems**
- Invalid credentials
- Expired RSA keys
- Vault connectivity issues
- Permission problems

### 3. **Snowflake Service Issues**
- Account suspension
- Service outages
- Maintenance windows
- Regional availability

### 4. **Configuration Problems**
- Incorrect account names
- Wrong region endpoints
- Missing warehouse/role assignments

## Monitoring Integration

### Automatic Connectivity Checks
- Performed before each monitoring cycle
- Skips replication monitoring if connectivity fails
- Sends email alerts for connectivity issues

### Email Alerts
Connectivity failures trigger immediate email notifications including:
- Account name and error details
- Response time and timestamp
- Suggested troubleshooting steps

### Exit Codes
- `0`: Success (connectivity test passed)
- `1`: Failure (connectivity test failed or other error)

## Troubleshooting Common Issues

### 1. **DNS Resolution Errors**
```
Error: [Errno -2] Name or service not known
```
**Solution**: Check account name format and network connectivity

### 2. **Connection Timeout**
```
Error: timed out
```
**Solution**: Increase timeout, check firewall/proxy settings

### 3. **Authentication Errors**
```
Error: 250001 (08001): Failed to connect to DB
```
**Solution**: Verify credentials, check RSA key validity

### 4. **SSL/TLS Errors**
```
Error: SSL connection error
```
**Solution**: Check certificate validity, proxy SSL settings

## Performance Considerations

### Response Time Thresholds
- **< 2 seconds**: Excellent
- **2-5 seconds**: Good
- **5-10 seconds**: Acceptable
- **> 10 seconds**: Investigate network issues

### Resource Usage
- Minimal compute credits consumed
- No warehouse required for basic connectivity
- Lightweight metadata queries only

## Integration with External Monitoring

### Health Check Endpoint
The connectivity test can be used as a health check:

```bash
#!/bin/bash
# Health check script for monitoring systems
python monitor_snowflake_replication.py myaccount --test-connectivity
if [ $? -eq 0 ]; then
    echo "Snowflake connectivity: OK"
else
    echo "Snowflake connectivity: FAILED"
    exit 1
fi
```

### Kubernetes Liveness Probe
```yaml
livenessProbe:
  exec:
    command:
    - python
    - monitor_snowflake_replication.py
    - myaccount
    - --test-connectivity
    - --connectivity-timeout
    - "10"
  initialDelaySeconds: 30
  periodSeconds: 300
```

This comprehensive connectivity testing ensures reliable monitoring and early detection of issues before they affect replication monitoring operations.