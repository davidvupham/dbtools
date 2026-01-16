# MongoDB Parameter Setting Implementation

## Overview

This document describes the implementation of MongoDB server parameter **setting** functionality (using `setParameter` command) to complement the parameter retrieval capabilities.

## Reference Documentation

- MongoDB setParameter Command: https://www.mongodb.com/docs/manual/reference/command/setParameter/
- MongoDB Server Parameters: https://www.mongodb.com/docs/manual/reference/parameters/

## Implementation Summary

### New Methods Added to `MongoDBParameterManager`

#### 1. `set_parameter(parameter_name, value, comment)`

Sets a single runtime-configurable parameter.

**Features:**
- Validates parameter can be set at runtime
- Provides clear error messages for startup-only parameters
- Supports optional comment for audit trails
- Returns command result dictionary

**Example:**
```python
# Set log level to verbose
result = param_manager.set_parameter("logLevel", 1)

# Set with audit comment
result = param_manager.set_parameter(
    "cursorTimeoutMillis",
    300000,
    comment="Increase timeout for analytics workload"
)
```

**Error Handling:**
- Distinguishes between runtime-settable and startup-only parameters
- Provides specific error message when parameter is startup-only
- Wraps PyMongo errors with context

#### 2. `set_multiple_parameters(parameters, comment)`

Sets multiple parameters in a single command.

**Features:**
- Atomic operation (all or nothing)
- Accepts dictionary of parameter names to values
- Optional comment applies to entire operation
- Returns command result

**Example:**
```python
params = {
    "logLevel": 2,
    "cursorTimeoutMillis": 300000,
    "notablescan": False
}
result = param_manager.set_multiple_parameters(
    params,
    comment="Configure for development environment"
)
```

#### 3. `reset_parameter(parameter_name)`

Attempts to reset a parameter to its documented default value.

**Features:**
- Built-in defaults for commonly modified parameters
- Returns True if default is known and applied
- Safe fallback for unknown parameters
- Useful for cleanup and testing

**Supported Parameters with Defaults:**
```python
defaults = {
    "logLevel": 0,
    "quiet": 0,
    "notablescan": False,
    "cursorTimeoutMillis": 600000,  # 10 minutes
    "ttlMonitorEnabled": True,
}
```

## Usage Patterns

### Pattern 1: Simple Parameter Change

```python
from gds_mongodb import MongoDBConnection, MongoDBParameterManager

with MongoDBConnection(host='localhost', database='admin') as conn:
    param_manager = MongoDBParameterManager(conn)

    # Enable verbose logging
    param_manager.set_parameter("logLevel", 1)
```

### Pattern 2: Safe Modification with Verification

```python
# Get current value first
original_value = param_manager.get_parameter("logLevel")

try:
    # Make change
    param_manager.set_parameter("logLevel", 2)

    # Verify change
    new_value = param_manager.get_parameter("logLevel")
    assert new_value == 2

finally:
    # Always restore original
    param_manager.set_parameter("logLevel", original_value)
```

### Pattern 3: Check Before Modifying

```python
# Get parameter details first
param_info = param_manager.get_parameter_details("maxBsonObjectSize")

if param_info.is_runtime_settable():
    param_manager.set_parameter("maxBsonObjectSize", 20971520)
else:
    print("Parameter requires server restart to modify")
```

### Pattern 4: Bulk Configuration

```python
# Configure multiple parameters for specific workload
analytics_config = {
    "allowDiskUseByDefault": True,
    "cursorTimeoutMillis": 1800000,  # 30 minutes
    "internalQueryExecMaxBlockingSortBytes": 209715200  # 200MB
}

param_manager.set_multiple_parameters(
    analytics_config,
    comment="Optimize for analytics workload"
)
```

### Pattern 5: Temporary Changes for Testing

```python
# Store originals
originals = {
    name: param_manager.get_parameter(name)
    for name in ["logLevel", "notablescan"]
}

try:
    # Apply test configuration
    test_config = {
        "logLevel": 5,  # Maximum verbosity
        "notablescan": True  # Prevent table scans
    }
    param_manager.set_multiple_parameters(test_config)

    # Run tests...

finally:
    # Restore all originals
    param_manager.set_multiple_parameters(originals)
```

## Runtime vs Startup Parameters

### Runtime-Settable Parameters (Examples)

Can be modified while MongoDB is running:
- `logLevel` - Logging verbosity
- `logComponentVerbosity` - Component-specific logging
- `cursorTimeoutMillis` - Cursor timeout
- `notablescan` - Prevent collection scans
- `quiet` - Quiet logging mode
- `ttlMonitorEnabled` - TTL index processing
- `allowDiskUseByDefault` - Disk usage for operations

### Startup-Only Parameters (Examples)

Require server restart to modify:
- `honorSystemUmask` - File permission settings
- `processUmask` - Custom umask
- `journalCompressor` - Journal compression
- `wiredTigerEngineConfig` - WiredTiger configuration
- `tcmallocEnableBackgroundThread` - TCMalloc settings

### Detecting Parameter Type

```python
param_info = param_manager.get_parameter_details("logLevel")

if param_info.is_runtime_settable():
    # Can use set_parameter()
    param_manager.set_parameter("logLevel", 1)
else:
    # Must be set in config file or command line
    print("Requires server restart")
```

## Safety Considerations

### 1. Always Check Before Modifying

```python
param_info = param_manager.get_parameter_details(param_name)
if not param_info.is_runtime_settable():
    raise ValueError(f"{param_name} cannot be set at runtime")
```

### 2. Store Original Values

```python
original = param_manager.get_parameter(param_name)
try:
    param_manager.set_parameter(param_name, new_value)
    # ... use new setting ...
finally:
    param_manager.set_parameter(param_name, original)
```

### 3. Use Comments for Audit Trail

```python
param_manager.set_parameter(
    "logLevel",
    2,
    comment=f"Debugging issue TICKET-123, changed by {user}"
)
```

### 4. Test in Non-Production First

```python
if environment == "production":
    raise ValueError("Test parameter changes in dev/staging first")

param_manager.set_parameter(param_name, value)
```

### 5. Monitor Impact

```python
# Record metrics before change
before_metrics = get_server_metrics()

# Make change
param_manager.set_parameter("cursorTimeoutMillis", 300000)

# Monitor for issues
time.sleep(60)
after_metrics = get_server_metrics()

# Rollback if problems detected
if detect_issues(before_metrics, after_metrics):
    param_manager.reset_parameter("cursorTimeoutMillis")
```

## Example Workflow: Performance Tuning

```python
from gds_mongodb import MongoDBConnection, MongoDBParameterManager

# Connect to admin database
with MongoDBConnection(host='localhost', database='admin') as conn:
    param_manager = MongoDBParameterManager(conn)

    # Step 1: Document current configuration
    print("Current Configuration:")
    current_config = {
        "logLevel": param_manager.get_parameter("logLevel"),
        "cursorTimeoutMillis": param_manager.get_parameter("cursorTimeoutMillis"),
        "allowDiskUseByDefault": param_manager.get_parameter("allowDiskUseByDefault")
    }
    for name, value in current_config.items():
        print(f"  {name}: {value}")

    # Step 2: Check which parameters are runtime-settable
    print("\nParameter Capabilities:")
    for name in current_config.keys():
        info = param_manager.get_parameter_details(name)
        if info.is_runtime_settable():
            print(f"  {name}: Can modify at runtime")
        else:
            print(f"  {name}: Requires restart")

    # Step 3: Apply tuning (if appropriate)
    if should_tune_for_analytics:
        tuning_params = {
            "logLevel": 1,
            "cursorTimeoutMillis": 1800000,  # 30 min
            "allowDiskUseByDefault": True
        }

        print("\nApplying performance tuning...")
        param_manager.set_multiple_parameters(
            tuning_params,
            comment="Optimize for analytics workload"
        )

        # Step 4: Verify changes
        print("\nVerifying changes:")
        for name, expected in tuning_params.items():
            actual = param_manager.get_parameter(name)
            status = "✓" if actual == expected else "✗"
            print(f"  {status} {name}: {actual}")
```

## Integration with Existing Retrieval

The parameter setting functionality integrates seamlessly with retrieval:

```python
# Retrieval (already implemented)
all_params = param_manager.get_all_parameters()
param_info = param_manager.get_parameter_details("logLevel")
runtime_params = param_manager.get_runtime_parameters()

# Setting (newly added)
param_manager.set_parameter("logLevel", 2)
param_manager.set_multiple_parameters({"logLevel": 1, "quiet": False})
param_manager.reset_parameter("logLevel")
```

## Error Handling

### Startup-Only Parameter

```python
try:
    param_manager.set_parameter("honorSystemUmask", True)
except PyMongoError as e:
    if "settable at startup" in str(e).lower():
        print("This parameter requires server restart")
        print("Add to mongod.conf or use --setParameter")
```

### Invalid Parameter Value

```python
try:
    param_manager.set_parameter("logLevel", 999)  # Out of range
except PyMongoError as e:
    print(f"Invalid value: {e}")
```

### Permission Denied

```python
try:
    param_manager.set_parameter("logLevel", 2)
except PyMongoError as e:
    if "not authorized" in str(e).lower():
        print("User lacks permission to modify parameters")
        print("Requires clusterManager role or similar")
```

## Testing

Unit tests added to `tests/test_server_config.py`:

- `test_set_parameter_success()` - Verify successful parameter setting
- `test_set_parameter_empty_name()` - Validate input checking
- `test_set_parameter_startup_only()` - Handle startup-only errors
- `test_set_multiple_parameters()` - Bulk parameter setting
- `test_reset_parameter_known()` - Reset to default values
- `test_reset_parameter_unknown()` - Handle unknown defaults

## Documentation Updates

Updated `README.md` with:
- "Setting Parameters at Runtime" section
- "Safe Parameter Modification Workflow" section
- Updated "Parameter Manager API" with modification methods
- Examples of parameter setting usage

Updated `examples/parameter_management.py` with:
- Example 12: Setting parameters
- Example 13: Setting multiple parameters
- Example 14: Runtime vs startup parameters
- Example 15: Safe parameter modification

## Benefits

1. **Complete Management**: Both retrieval and modification in one interface
2. **Safety**: Built-in checks for runtime vs startup parameters
3. **Audit Trail**: Optional comments for all modifications
4. **Error Handling**: Clear messages for common failure scenarios
5. **Convenience**: Reset to defaults for known parameters
6. **Consistency**: Same API pattern as retrieval methods

## Limitations

1. **Startup-Only Parameters**: Cannot modify parameters that require restart
2. **Permissions**: Requires appropriate MongoDB roles (clusterManager, etc.)
3. **Validation**: Some invalid values may not be caught until MongoDB processes them
4. **Defaults**: Not all parameters have well-documented default values
5. **Replication**: Changes only affect the specific instance, not replica set wide

## Security Considerations

1. **Authentication Required**: Parameter setting requires admin database access
2. **Role-Based Access**: User must have appropriate privileges
3. **Audit Logging**: Enable MongoDB auditing to track parameter changes
4. **Sensitive Parameters**: Some parameters affect security (e.g., authentication settings)
5. **Production Safety**: Always test changes in non-production first

## Conclusion

The parameter setting implementation provides a complete, safe, and well-documented solution for runtime MongoDB parameter management. Combined with the retrieval functionality, users have full programmatic control over MongoDB server configuration within the `gds_mongodb` package.

### Files Modified

1. **`gds_mongodb/server_config.py`**
   - Added `set_parameter()` method (~50 lines)
   - Added `set_multiple_parameters()` method (~35 lines)
   - Added `reset_parameter()` method (~30 lines)

2. **`examples/parameter_management.py`**
   - Added Example 12: Setting parameters
   - Added Example 13: Setting multiple parameters
   - Added Example 14: Runtime vs startup parameters
   - Added Example 15: Safe parameter modification

3. **`README.md`**
   - Added "Setting Parameters at Runtime" section
   - Added "Safe Parameter Modification Workflow" section
   - Updated "Parameter Manager API" section

### Total Addition: ~450 lines of new code + documentation
