# Vault Secret Rotation-Aware TTL Implementation Guide

## Overview

The gds-vault package now supports automatic TTL calculation based on Vault secret rotation schedules. This enhancement allows secrets to be automatically refreshed before their scheduled rotation time with a configurable buffer period, ensuring applications always have valid credentials.

## Key Features

### 1. Rotation Schedule Parsing
- **Cron Expression Support**: Parse standard 5-field cron expressions
- **Next Rotation Calculation**: Determine when secrets will next rotate
- **Buffer Time**: Configurable safety margin before rotation

### 2. Enhanced Caching
- **RotationAwareCache**: Full rotation schedule awareness
- **Enhanced TTLCache**: Backward-compatible rotation support
- **Automatic Refresh**: Secrets refresh before rotation time

### 3. Metadata Extraction
- **Vault Response Parsing**: Extract rotation metadata from Vault API responses
- **Multiple Formats**: Support KV v1, KV v2, and auth metadata locations
- **Graceful Fallback**: Fall back to standard TTL if no rotation schedule

## Implementation Details

### Core Components

#### 1. Rotation Utilities (`gds_vault/rotation.py`)

```python
from gds_vault.rotation import (
    CronParser,
    calculate_rotation_ttl,
    should_refresh_secret,
    parse_vault_rotation_metadata
)

# Parse cron schedule
cron = CronParser("0 2 * * *")  # Daily at 2 AM
next_run = cron.next_run_time()

# Calculate TTL until next rotation
ttl = calculate_rotation_ttl(
    last_rotation="2024-10-08T02:00:00Z",
    rotation_schedule="0 2 * * *",
    buffer_minutes=10
)

# Check if immediate refresh needed
needs_refresh = should_refresh_secret(
    last_rotation="2024-10-08T02:00:00Z",
    rotation_schedule="0 2 * * *",
    buffer_minutes=10
)
```

#### 2. RotationAwareCache Class

```python
from gds_vault import VaultClient, RotationAwareCache

# Create rotation-aware cache
cache = RotationAwareCache(
    max_size=100,
    buffer_minutes=10,  # Refresh 10 minutes before rotation
    fallback_ttl=300    # 5-minute fallback for non-rotating secrets
)

client = VaultClient(cache=cache)

# Secrets with rotation metadata are automatically managed
secret = client.get_secret('secret/data/database-creds')
```

#### 3. Enhanced TTLCache

```python
from gds_vault import VaultClient, TTLCache

# TTL cache now supports rotation metadata
cache = TTLCache(max_size=50, default_ttl=300)
client = VaultClient(cache=cache)

# Automatically uses rotation schedule if available
# Falls back to default TTL if no rotation metadata
secret = client.get_secret('secret/data/app-config')
```

### Vault Response Processing

The implementation automatically extracts rotation metadata from Vault responses:

```python
# Example Vault KV v2 response with rotation metadata
{
    "data": {
        "data": {
            "username": "app_user",
            "password": "secret123"
        },
        "metadata": {
            "created_time": "2024-10-08T02:00:00Z",
            "last_rotation": "2024-10-08T02:00:00Z",
            "rotation_schedule": "0 2 * * *"
        }
    }
}
```

The client automatically:
1. Extracts rotation metadata from the response
2. Calculates TTL based on the next rotation time
3. Applies the configured buffer time
4. Caches the secret with the calculated TTL

### TTL Calculation Logic

```python
def calculate_rotation_ttl(
    last_rotation: str,
    rotation_schedule: str,
    buffer_minutes: int = 10
) -> int:
    """
    Calculate TTL based on rotation schedule.
    
    Logic:
    1. Parse the cron schedule
    2. Calculate next rotation time from last rotation
    3. Subtract buffer time from next rotation
    4. Return TTL in seconds
    5. Return 0 if within buffer time (immediate refresh needed)
    """
```

## Usage Examples

### Basic Usage

```python
from gds_vault import VaultClient, RotationAwareCache

# Create client with rotation-aware caching
cache = RotationAwareCache(buffer_minutes=15)
client = VaultClient(cache=cache)

# Fetch secret - automatically managed based on rotation schedule
secret = client.get_secret('secret/data/database')

# Secret will be refreshed 15 minutes before next rotation
# No manual cache management needed
```

### Production Configuration

```python
from gds_vault import VaultClient, RotationAwareCache

# Production-ready configuration
cache = RotationAwareCache(
    max_size=100,        # Cache up to 100 secrets
    buffer_minutes=10,   # 10-minute safety buffer
    fallback_ttl=300     # 5-minute fallback for non-rotating secrets
)

client = VaultClient(
    cache=cache,
    timeout=30,          # 30-second timeout
    verify_ssl=True      # Always verify SSL
)

# All secrets are automatically managed:
# - Rotating secrets: TTL based on schedule
# - Non-rotating secrets: Use fallback TTL
# - Cache handles refresh automatically
```

### Manual Rotation Metadata

```python
from gds_vault.cache import RotationAwareCache

cache = RotationAwareCache()

# Manually set rotation metadata
rotation_metadata = {
    'last_rotation': '2024-10-08T02:00:00Z',
    'schedule': '0 2 * * *'  # Daily at 2 AM
}

cache.set(
    'secret/data/app',
    {'password': 'secret123'},
    rotation_metadata=rotation_metadata
)

# Check if needs refresh
needs_refresh = cache.force_refresh_check('secret/data/app')
```

## Common Rotation Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Hourly | `0 * * * *` | Every hour at minute 0 |
| Every 6 hours | `0 */6 * * *` | Every 6 hours |
| Daily | `0 2 * * *` | Daily at 2:00 AM |
| Weekly | `0 2 * * 0` | Weekly on Sunday at 2:00 AM |
| Monthly | `0 2 1 * *` | Monthly on 1st at 2:00 AM |
| Quarterly | `0 2 1 */3 *` | Quarterly on 1st at 2:00 AM |

## Error Handling

The implementation includes comprehensive error handling:

```python
# Graceful fallback for invalid schedules
try:
    ttl = calculate_rotation_ttl(last_rotation, schedule)
except ValueError as e:
    logger.warning(f"Invalid rotation schedule: {e}")
    ttl = fallback_ttl  # Use fallback TTL

# Cache handles rotation errors gracefully
cache = RotationAwareCache(fallback_ttl=300)
# If rotation calculation fails, uses fallback_ttl
```

## Migration Guide

### From Standard Caching

```python
# Old: Standard TTL cache
cache = TTLCache(max_size=50, default_ttl=600)
client = VaultClient(cache=cache)

# New: Rotation-aware cache (recommended)
cache = RotationAwareCache(
    max_size=50,
    buffer_minutes=10,
    fallback_ttl=600  # Same as old default_ttl
)
client = VaultClient(cache=cache)

# Or: Enhanced TTL cache (minimal change)
cache = TTLCache(max_size=50, default_ttl=600)
client = VaultClient(cache=cache)
# Now automatically uses rotation metadata if available
```

### Backward Compatibility

- All existing cache classes continue to work unchanged
- TTLCache now optionally supports rotation metadata
- No breaking changes to existing APIs
- New functionality is opt-in

## Best Practices

### Buffer Time Selection

```python
# Conservative: 15-30 minutes for critical systems
cache = RotationAwareCache(buffer_minutes=30)

# Standard: 10-15 minutes for most applications
cache = RotationAwareCache(buffer_minutes=10)

# Aggressive: 5 minutes for systems that can handle brief outages
cache = RotationAwareCache(buffer_minutes=5)
```

### Cache Size Tuning

```python
# Small applications: 10-50 secrets
cache = RotationAwareCache(max_size=50)

# Medium applications: 50-200 secrets
cache = RotationAwareCache(max_size=200)

# Large applications: 200+ secrets
cache = RotationAwareCache(max_size=500)
```

### Monitoring and Observability

```python
# Regular cache statistics monitoring
cache = RotationAwareCache()
stats = cache.get_stats()

print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Secrets with rotation: {stats['secrets_with_rotation']}")
print(f"Secrets needing refresh: {stats['secrets_needing_refresh']}")
print(f"Average remaining TTL: {stats['avg_remaining_ttl']:.1f}s")

# Cleanup expired secrets periodically
removed_count = cache.cleanup_expired()
print(f"Cleaned up {removed_count} expired secrets")
```

## Testing

The implementation includes comprehensive tests:

```bash
# Run rotation-aware tests
python -m pytest tests/test_rotation_aware.py -v

# Run all cache tests
python -m pytest tests/test_cache.py -v

# Run integration tests
python -m pytest tests/test_client.py -v
```

## Limitations and Considerations

### Cron Parsing Limitations
- Supports standard 5-field cron format only
- Complex expressions may need validation
- Consider using `croniter` library for advanced parsing

### Time Zone Considerations
- All times assumed to be in system timezone
- Vault rotation times should match system timezone
- UTC recommended for consistency

### Performance Considerations
- Rotation calculation is performed on cache set operations
- Minimal overhead for non-rotating secrets
- Cache cleanup should be run periodically

### Vault Integration
- Requires Vault to provide rotation metadata
- Metadata format may vary by Vault version
- Graceful fallback for missing metadata

## Future Enhancements

1. **Advanced Cron Parsing**: Integration with `croniter` for complex schedules
2. **Time Zone Support**: Explicit timezone handling
3. **Rotation History**: Track rotation history and patterns
4. **Predictive Refresh**: Preemptive refresh based on usage patterns
5. **Metrics Integration**: Built-in metrics and monitoring

## Conclusion

The rotation-aware TTL implementation provides automatic secret lifecycle management based on Vault rotation schedules. This ensures applications always have valid credentials while minimizing unnecessary Vault requests through intelligent caching.

The implementation is backward-compatible, production-ready, and includes comprehensive error handling and fallback mechanisms.