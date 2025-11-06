# Test Documentation - Rotation-Aware TTL Implementation

## Test Overview

This document provides comprehensive documentation for the test suite covering the rotation-aware TTL functionality in the gds-vault package.

## Test Architecture

### Test File Structure

```
tests/
├── test_rotation_aware.py          # Main rotation functionality tests
├── test_cache.py                   # Enhanced cache tests (existing)
├── test_client.py                  # Client integration tests (existing)
└── fixtures/                      # Test data and fixtures
    ├── rotation_schedules.py       # Sample cron schedules
    └── vault_responses.py          # Mock Vault API responses
```

### Test Categories

#### 1. Unit Tests (`TestRotationUtils`)
Tests for core rotation utility functions in isolation.

#### 2. Integration Tests (`TestRotationAwareCache`)
Tests for cache classes with rotation functionality.

#### 3. Compatibility Tests (`TestTTLCacheRotationSupport`)
Tests ensuring backward compatibility of enhanced components.

#### 4. End-to-End Tests
Full workflow tests from Vault response to cache expiration.

## Detailed Test Specifications

### 1. TestRotationUtils Class

#### `test_cron_parser_daily()`
**Purpose**: Verify daily cron schedule parsing accuracy

```python
def test_cron_parser_daily(self):
    """Test daily cron schedule parsing."""
    cron = CronParser("0 2 * * *")  # Daily at 2 AM

    # Test from midnight
    test_time = datetime(2024, 10, 8, 0, 0, 0)
    next_run = cron.next_run_time(test_time)

    # Should be 2 AM same day
    expected = datetime(2024, 10, 8, 2, 0, 0)
    self.assertEqual(next_run, expected)
```

**Test Scenarios**:
- From before daily rotation time → same day at rotation time
- From after daily rotation time → next day at rotation time
- Edge cases: leap years, month boundaries, DST transitions

**Expected Results**:
- Accurate next rotation time calculation
- Proper handling of edge cases
- Consistent behavior across time zones

#### `test_calculate_rotation_ttl()`
**Purpose**: Validate TTL calculation logic with buffer time

```python
def test_calculate_rotation_ttl(self):
    """Test TTL calculation based on rotation schedule."""
    current_time = datetime(2024, 10, 8, 15, 0, 0)  # 3 PM
    last_rotation = datetime(2024, 10, 8, 2, 0, 0)   # 2 AM same day

    ttl = calculate_rotation_ttl(
        last_rotation.isoformat(),
        "0 2 * * *",  # Daily at 2 AM
        buffer_minutes=10,
        current_time=current_time
    )

    # Next rotation is tomorrow at 2 AM (11 hours from 3 PM)
    # Minus 10 minutes buffer = 10h 50m = 39000 seconds
    expected_ttl = (11 * 60 - 10) * 60
    self.assertAlmostEqual(ttl, expected_ttl, delta=60)
```

**Test Matrix**:

| Last Rotation | Current Time | Schedule | Buffer | Expected TTL |
|---------------|--------------|----------|---------|--------------|
| 1 hour ago | Now | Daily | 10 min | ~22h 50m |
| 23 hours ago | Now | Daily | 10 min | 0 (refresh) |
| 30 min ago | Now | Hourly | 5 min | ~25 min |
| 6 days ago | Now | Weekly | 15 min | ~45 min |

**Validation Points**:
- Correct TTL calculation for various schedules
- Proper buffer time application
- Zero TTL when refresh needed immediately
- Handling of different datetime formats

#### `test_should_refresh_secret_within_buffer()`
**Purpose**: Test refresh logic when within buffer time

```python
def test_should_refresh_secret_within_buffer(self):
    """Test refresh check when within buffer time."""
    current_time = datetime(2024, 10, 9, 1, 55, 0)  # 1:55 AM
    last_rotation = datetime(2024, 10, 8, 2, 0, 0)   # Yesterday 2 AM

    should_refresh = should_refresh_secret(
        last_rotation.isoformat(),
        "0 2 * * *",  # Daily at 2 AM (5 min away)
        buffer_minutes=10,
        current_time=current_time
    )

    # Should refresh because we're within 10-minute buffer
    self.assertTrue(should_refresh)
```

**Buffer Time Test Cases**:

| Time Until Rotation | Buffer | Should Refresh |
|---------------------|--------|----------------|
| 15 minutes | 10 min | False |
| 8 minutes | 10 min | True |
| 0 minutes (past) | 10 min | True |
| 2 hours | 10 min | False |

#### `test_parse_vault_rotation_metadata()`
**Purpose**: Test extraction of rotation metadata from various Vault response formats

```python
def test_parse_vault_rotation_metadata(self):
    """Test parsing rotation metadata from Vault response."""
    # KV v2 response with metadata
    vault_response = {
        "data": {
            "data": {"password": "secret123"},
            "metadata": {
                "created_time": "2024-10-08T02:00:00Z",
                "last_rotation": "2024-10-08T02:00:00Z",
                "rotation_schedule": "0 2 * * *"
            }
        }
    }

    metadata = parse_vault_rotation_metadata(vault_response)

    self.assertIsNotNone(metadata)
    self.assertEqual(metadata["last_rotation"], "2024-10-08T02:00:00Z")
    self.assertEqual(metadata["schedule"], "0 2 * * *")
```

**Response Format Test Cases**:

1. **KV v2 Response**:
   ```json
   {
     "data": {
       "metadata": {
         "last_rotation": "2024-10-08T02:00:00Z",
         "rotation_schedule": "0 2 * * *"
       }
     }
   }
   ```

2. **Auth Response**:
   ```json
   {
     "auth": {
       "metadata": {
         "last_rotation_time": "2024-10-08T02:00:00Z",
         "schedule": "0 2 * * *"
       }
     }
   }
   ```

3. **Direct Metadata**:
   ```json
   {
     "metadata": {
       "rotation_time": "2024-10-08T02:00:00Z",
       "cron_schedule": "0 2 * * *"
     }
   }
   ```

**Edge Cases**:
- No metadata present → return None
- Partial metadata (missing schedule) → return None
- Multiple metadata locations → prefer data.metadata
- Invalid metadata format → return None gracefully

### 2. TestRotationAwareCache Class

#### `test_cache_without_rotation_metadata()`
**Purpose**: Verify fallback behavior when no rotation metadata is provided

```python
def test_cache_without_rotation_metadata(self):
    """Test caching without rotation metadata."""
    cache = RotationAwareCache(fallback_ttl=300)
    secret_data = {"password": "secret123"}

    cache.set("test-secret", secret_data)

    retrieved = cache.get("test-secret")
    self.assertEqual(retrieved, secret_data)

    # Should use fallback TTL
    stats = cache.get_stats()
    self.assertEqual(stats["secrets_with_rotation"], 0)
```

**Fallback Scenarios**:
- No rotation metadata provided
- Invalid rotation metadata format
- Rotation calculation errors
- Missing required fields in metadata

#### `test_cache_with_rotation_metadata()`
**Purpose**: Test full rotation-aware functionality

```python
def test_cache_with_rotation_metadata(self):
    """Test caching with rotation metadata."""
    cache = RotationAwareCache(buffer_minutes=10)
    secret_data = {"password": "secret123"}
    rotation_metadata = {
        "last_rotation": "2024-10-08T02:00:00Z",
        "schedule": "0 2 * * *"
    }

    cache.set(
        "test-secret",
        secret_data,
        rotation_metadata=rotation_metadata
    )

    # Verify caching
    retrieved = cache.get("test-secret")
    self.assertEqual(retrieved, secret_data)

    # Verify rotation info storage
    rotation_info = cache.get_rotation_info("test-secret")
    self.assertEqual(rotation_info, rotation_metadata)

    # Verify statistics
    stats = cache.get_stats()
    self.assertEqual(stats["secrets_with_rotation"], 1)
```

**Rotation Metadata Test Matrix**:

| Schedule | Last Rotation | Buffer | Expected Behavior |
|----------|---------------|--------|-------------------|
| `0 2 * * *` | 1 hour ago | 10 min | Cache normally |
| `0 2 * * *` | 23 hours ago | 10 min | Immediate refresh |
| `0 * * * *` | 30 min ago | 5 min | Cache with short TTL |
| Invalid cron | Any | 10 min | Use fallback TTL |

#### `test_force_refresh_check()`
**Purpose**: Test forced refresh detection logic

```python
def test_force_refresh_check(self):
    """Test force refresh checking."""
    cache = RotationAwareCache(buffer_minutes=15)

    # Setup secret that needs refresh soon
    current_time = datetime.now()

    # Rotation in 10 minutes (within 15-minute buffer)
    last_rotation = current_time - timedelta(hours=23, minutes=50)

    rotation_metadata = {
        "last_rotation": last_rotation.isoformat(),
        "schedule": "0 2 * * *"
    }

    cache.set("test-secret", {"key": "value"}, rotation_metadata=rotation_metadata)

    # Check refresh status
    needs_refresh = cache.force_refresh_check("test-secret")

    # Should indicate refresh needed
    self.assertTrue(needs_refresh)
```

#### `test_cache_stats()`
**Purpose**: Validate cache statistics accuracy

```python
def test_cache_stats(self):
    """Test cache statistics."""
    cache = RotationAwareCache(buffer_minutes=10)

    # Add secrets with different metadata
    secrets = [
        ("secret1", {"password": "abc"}, {"last_rotation": "2024-10-08T02:00:00Z", "schedule": "0 2 * * *"}),
        ("secret2", {"api_key": "xyz"}, None),  # No rotation
        ("secret3", {"token": "123"}, {"last_rotation": "2024-10-07T02:00:00Z", "schedule": "0 2 * * *"})
    ]

    for key, data, metadata in secrets:
        cache.set(key, data, rotation_metadata=metadata)

    stats = cache.get_stats()

    # Validate statistics
    self.assertEqual(stats["size"], 3)
    self.assertEqual(stats["secrets_with_rotation"], 2)
    self.assertIn("secrets_needing_refresh", stats)
    self.assertIn("avg_remaining_ttl", stats)
```

**Statistics Validation Points**:
- Total cache size accuracy
- Count of secrets with rotation schedules
- Count of secrets needing refresh
- Average remaining TTL calculation
- Buffer time and fallback TTL reporting

### 3. TestTTLCacheRotationSupport Class

#### `test_ttl_cache_with_rotation_metadata()`
**Purpose**: Verify enhanced TTLCache accepts rotation metadata

```python
def test_ttl_cache_with_rotation_metadata(self):
    """Test TTLCache with rotation metadata."""
    cache = TTLCache(max_size=10, default_ttl=300)
    secret_data = {"password": "secret123"}
    rotation_metadata = {
        "last_rotation": "2024-10-08T02:00:00Z",
        "schedule": "0 2 * * *"
    }

    # Should accept rotation metadata parameter
    cache.set(
        "test-secret",
        secret_data,
        rotation_metadata=rotation_metadata
    )

    retrieved = cache.get("test-secret")
    self.assertEqual(retrieved, secret_data)
```

#### `test_ttl_cache_backward_compatibility()`
**Purpose**: Ensure existing TTLCache usage continues to work

```python
def test_ttl_cache_backward_compatibility(self):
    """Test TTLCache normal operation without rotation metadata."""
    cache = TTLCache(max_size=10, default_ttl=60)
    secret_data = {"password": "secret123"}

    # Standard usage should work unchanged
    cache.set("test-secret", secret_data, ttl=120)

    retrieved = cache.get("test-secret")
    self.assertEqual(retrieved, secret_data)
```

## Test Data and Fixtures

### Sample Rotation Schedules

```python
# tests/fixtures/rotation_schedules.py
ROTATION_SCHEDULES = {
    "hourly": "0 * * * *",
    "every_6_hours": "0 */6 * * *",
    "daily": "0 2 * * *",
    "weekly": "0 2 * * 0",
    "monthly": "0 2 1 * *",
    "quarterly": "0 2 1 */3 *",
    "yearly": "0 2 1 1 *",
}

INVALID_SCHEDULES = [
    "invalid cron",
    "* * * *",           # Too few fields
    "* * * * * *",       # Too many fields
    "60 2 * * *",        # Invalid minute
    "0 25 * * *",        # Invalid hour
]
```

### Mock Vault Responses

```python
# tests/fixtures/vault_responses.py
KV_V2_WITH_ROTATION = {
    "data": {
        "data": {"username": "app", "password": "secret"},
        "metadata": {
            "created_time": "2024-10-08T02:00:00Z",
            "last_rotation": "2024-10-08T02:00:00Z",
            "rotation_schedule": "0 2 * * *",
            "version": 1
        }
    }
}

AUTH_WITH_ROTATION = {
    "auth": {
        "client_token": "hvs.CAESIF...",
        "lease_duration": 3600,
        "metadata": {
            "last_rotation_time": "2024-10-08T02:00:00Z",
            "schedule": "0 2 * * *"
        }
    }
}

NO_ROTATION_METADATA = {
    "data": {
        "data": {"api_key": "abc123"},
        "metadata": {
            "created_time": "2024-10-08T10:00:00Z",
            "version": 1
        }
    }
}
```

## Test Execution Strategies

### Continuous Integration

```yaml
# .github/workflows/test.yml
- name: Run Rotation Tests
  run: |
    python -m pytest tests/test_rotation_aware.py -v --cov=gds_vault.rotation
    python -m pytest tests/test_cache.py -k "rotation" -v
```

### Local Development

```bash
# Run all rotation tests
python -m pytest tests/test_rotation_aware.py -v

# Run with detailed output
python -m pytest tests/test_rotation_aware.py -vv -s

# Run specific test class
python -m pytest tests/test_rotation_aware.py::TestRotationUtils -v

# Run with coverage
python -m pytest tests/test_rotation_aware.py --cov=gds_vault --cov-report=html
```

### Performance Testing

```python
# tests/test_rotation_performance.py
import time
import pytest
from gds_vault.cache import RotationAwareCache

def test_rotation_calculation_performance():
    """Test rotation calculation performance."""
    cache = RotationAwareCache()

    # Test data
    secret_data = {"key": "value"}
    rotation_metadata = {
        "last_rotation": "2024-10-08T02:00:00Z",
        "schedule": "0 2 * * *"
    }

    # Measure performance
    start_time = time.time()

    for i in range(1000):
        cache.set(f"secret-{i}", secret_data, rotation_metadata=rotation_metadata)

    end_time = time.time()
    avg_time = (end_time - start_time) / 1000

    # Should be under 1ms per operation
    assert avg_time < 0.001, f"Average time {avg_time}s exceeds 1ms threshold"
```

## Test Coverage Requirements

### Minimum Coverage Targets

- **Rotation Utilities**: 95% line coverage
- **Cache Classes**: 90% line coverage
- **Client Integration**: 85% line coverage
- **Overall Package**: 90% line coverage

### Coverage Analysis

```bash
# Generate coverage report
python -m pytest tests/ --cov=gds_vault --cov-report=html --cov-report=term

# Coverage by module
python -m pytest --cov=gds_vault.rotation --cov-report=term-missing
python -m pytest --cov=gds_vault.cache --cov-report=term-missing
```

## Test Environment Setup

### Dependencies

```python
# requirements-test.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.0.0
freezegun>=1.2.0  # For time-based testing
```

### Environment Variables

```bash
# Test environment
export VAULT_ADDR="https://vault-test.example.com"
export VAULT_ROLE_ID="test-role-id"
export VAULT_SECRET_ID="test-secret-id"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Mock Configuration

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_vault_response():
    """Mock Vault API response with rotation metadata."""
    return {
        "data": {
            "data": {"password": "test123"},
            "metadata": {
                "last_rotation": "2024-10-08T02:00:00Z",
                "rotation_schedule": "0 2 * * *"
            }
        }
    }

@pytest.fixture
def rotation_aware_cache():
    """Pre-configured RotationAwareCache for testing."""
    from gds_vault.cache import RotationAwareCache
    return RotationAwareCache(buffer_minutes=10, fallback_ttl=300)
```

## Error Condition Testing

### Exception Handling Tests

```python
def test_invalid_cron_expression_handling():
    """Test graceful handling of invalid cron expressions."""
    from gds_vault.rotation import CronParser

    with pytest.raises(ValueError, match="Invalid cron expression"):
        CronParser("invalid cron expression")

def test_rotation_calculation_error_fallback():
    """Test fallback behavior when rotation calculation fails."""
    cache = RotationAwareCache(fallback_ttl=300)

    # Invalid rotation metadata should not crash
    invalid_metadata = {
        "last_rotation": "not-a-date",
        "schedule": "invalid-cron"
    }

    # Should use fallback TTL without raising exception
    cache.set("test", {"key": "value"}, rotation_metadata=invalid_metadata)

    result = cache.get("test")
    assert result is not None
```

### Edge Case Testing

```python
def test_timezone_edge_cases():
    """Test handling of various timezone formats."""
    from gds_vault.rotation import calculate_rotation_ttl

    timezone_formats = [
        "2024-10-08T02:00:00Z",           # UTC
        "2024-10-08T02:00:00+00:00",      # UTC with offset
        "2024-10-08T02:00:00-05:00",      # EST
        "2024-10-08T02:00:00.123Z",       # With microseconds
    ]

    for time_format in timezone_formats:
        ttl = calculate_rotation_ttl(time_format, "0 2 * * *")
        assert isinstance(ttl, int)
        assert ttl >= 0

def test_leap_year_handling():
    """Test cron parsing during leap year edge cases."""
    from gds_vault.rotation import CronParser
    from datetime import datetime

    # February 29th in leap year
    leap_day = datetime(2024, 2, 29, 1, 0, 0)
    cron = CronParser("0 2 * * *")

    next_run = cron.next_run_time(leap_day)
    expected = datetime(2024, 2, 29, 2, 0, 0)
    assert next_run == expected
```

## Test Maintenance and Evolution

### Test Documentation Standards

- Each test method must have a descriptive docstring
- Test scenarios must be clearly documented
- Expected behaviors must be explicitly stated
- Edge cases must be identified and tested

### Test Review Checklist

- [ ] All positive test cases covered
- [ ] Error conditions tested
- [ ] Edge cases identified and tested
- [ ] Performance implications considered
- [ ] Backward compatibility verified
- [ ] Documentation updated
- [ ] Test data realistic and comprehensive

### Future Test Enhancements

1. **Property-Based Testing**: Use hypothesis for automated test case generation
2. **Integration Testing**: Full end-to-end testing with real Vault server
3. **Load Testing**: Performance under high secret volume
4. **Concurrency Testing**: Thread safety validation
5. **Monitoring Integration**: Test metrics and alerting

This comprehensive test documentation ensures the rotation-aware TTL implementation is thoroughly validated and maintains high quality standards.
