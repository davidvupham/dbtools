# MongoDB Parameter Management Implementation

## Overview

This document describes the implementation of MongoDB server parameter management functionality in the `gds_mongodb` package, following OOP design principles.

## Reference Documentation

MongoDB getParameter Command: https://www.mongodb.com/docs/manual/reference/command/getParameter/

## Implementation Summary

### New Modules Created

#### 1. `gds_mongodb/server_config.py` (462 lines)

Core module containing two main classes:

**ParameterInfo Class**
- Represents detailed information about a MongoDB server parameter
- Properties:
  - `name`: Parameter name
  - `value`: Current parameter value
  - `settable_at_runtime`: Whether parameter can be modified at runtime
  - `settable_at_startup`: Whether parameter can be modified at startup
- Methods:
  - `is_runtime_settable()`: Check if parameter can be changed without restart
  - `is_startup_settable()`: Check if parameter can be set at startup
  - `to_dict()`: Export to dictionary format
  - `__repr__()` and `__str__()`: String representations

**MongoDBParameterManager Class**
- Manages retrieval and inspection of MongoDB server configuration parameters
- Constructor: `__init__(connection: MongoDBConnection)`
- Core Methods:
  - `get_parameter(parameter_name)`: Get single parameter value
  - `get_parameter_details(parameter_name)`: Get ParameterInfo with metadata
  - `get_all_parameters(show_details=False)`: Get all parameters
  - `get_all_parameters_info()`: Get all as ParameterInfo objects
  - `get_runtime_parameters()`: Get runtime-settable parameters (MongoDB 8.0+)
  - `get_startup_parameters()`: Get startup-settable parameters (MongoDB 8.0+)
  - `search_parameters(keyword, case_sensitive=False)`: Search by keyword
  - `get_parameters_by_prefix(prefix)`: Get parameters by name prefix
  - `to_dict()`: Export all parameters as dictionary

### Examples Created

#### 2. `examples/parameter_management.py` (426 lines)

Comprehensive example script demonstrating all parameter management features:

- **Example 1**: Basic parameter retrieval
- **Example 2**: Parameter details with metadata
- **Example 3**: Retrieve all parameters
- **Example 4**: All parameters with details
- **Example 5**: Parameter info list
- **Example 6**: Runtime-settable parameters
- **Example 7**: Startup-settable parameters
- **Example 8**: Search parameters by keyword
- **Example 9**: Parameters by prefix
- **Example 10**: Export parameters
- **Example 11**: Practical monitoring workflow

### Tests Created

#### 3. `tests/test_server_config.py` (657 lines)

Complete unit test suite covering:

**ParameterInfo Tests:**
- Basic initialization
- Initialization with details
- Runtime/startup settable checks
- Dictionary conversion
- String representations

**MongoDBParameterManager Tests:**
- Initialization validation
- Admin database access
- Single parameter retrieval
- Parameter details retrieval
- All parameters retrieval (with/without details)
- Parameter info list generation
- Runtime parameters (modern + fallback)
- Startup parameters (modern + fallback)
- Parameter search (case-sensitive/insensitive)
- Parameters by prefix
- Dictionary export
- Error handling and edge cases

### Documentation Updates

#### 4. Updated `README.md`

Added comprehensive "Server Parameter Management" section including:
- Basic usage examples
- Retrieving multiple parameters
- Filtering parameters
- ParameterInfo object usage
- Practical use cases (monitoring, backup, comparison)
- Complete API reference

Added "Example Scripts" section listing all 7 example files.

#### 5. Updated `gds_mongodb/__init__.py`

- Added imports: `MongoDBParameterManager`, `ParameterInfo`
- Updated `__all__` to export new classes
- Enhanced module docstring with parameter management usage

## Key Design Decisions

### 1. OOP Design Pattern

Following the existing package patterns:
- **Separation of Concerns**: Parameter management separated into dedicated classes
- **Single Responsibility**: ParameterInfo focuses on data, ParameterManager focuses on operations
- **Composition**: Manager uses connection object rather than inheritance
- **Encapsulation**: Internal admin database access hidden from users

### 2. Connection Dependency

```python
param_manager = MongoDBParameterManager(connection)
```

- Requires active `MongoDBConnection` instance
- Validates connection state before operations
- Uses connection's client for admin database access
- Leverages existing connection management and error handling

### 3. Two-Level API

**Simple Access** (for quick parameter retrieval):
```python
value = param_manager.get_parameter("logLevel")
all_params = param_manager.get_all_parameters()
```

**Detailed Access** (for inspection and filtering):
```python
param_info = param_manager.get_parameter_details("logLevel")
if param_info.is_runtime_settable():
    print("Can be changed without restart")
```

### 4. MongoDB Version Compatibility

The implementation handles both MongoDB 8.0+ and older versions:

```python
def get_runtime_parameters(self):
    try:
        # Try MongoDB 8.0+ command with setAt parameter
        return admin_db.command(
            "getParameter",
            {"allParameters": True, "setAt": "runtime"}
        )
    except PyMongoError as e:
        # Fallback: manually filter for older versions
        all_params = self.get_all_parameters_info()
        return {p.name: p.value for p in all_params if p.is_runtime_settable()}
```

### 5. Flexible Filtering

Multiple ways to filter parameters:
- **By name**: `get_parameter("logLevel")`
- **By keyword**: `search_parameters("log")`
- **By prefix**: `get_parameters_by_prefix("net")`
- **By capability**: `get_runtime_parameters()`
- **Programmatically**: Using ParameterInfo list filtering

### 6. Clean Response Data

Automatically removes MongoDB metadata fields:
```python
result.pop("ok", None)
result.pop("$clusterTime", None)
result.pop("operationTime", None)
```

Users get clean parameter data without internal MongoDB fields.

## Usage Patterns

### Pattern 1: Configuration Backup

```python
param_manager = MongoDBParameterManager(connection)
config_backup = param_manager.to_dict()
# Save for documentation or disaster recovery
```

### Pattern 2: Monitoring

```python
# Check critical parameters
max_bson = param_manager.get_parameter("maxBsonObjectSize")
if max_bson < 16777216:  # 16MB
    alert("BSON size limit below default")

log_level = param_manager.get_parameter("logLevel")
if log_level > 2:
    alert("Verbose logging enabled")
```

### Pattern 3: Environment Comparison

```python
dev_manager = MongoDBParameterManager(dev_connection)
prod_manager = MongoDBParameterManager(prod_connection)

dev_params = dev_manager.get_all_parameters()
prod_params = prod_manager.get_all_parameters()

differences = {
    k: (dev_params[k], prod_params[k])
    for k in dev_params
    if dev_params[k] != prod_params.get(k)
}
```

### Pattern 4: Runtime Tuning Discovery

```python
# Find what can be tuned without restart
tunable = param_manager.get_runtime_parameters()
print(f"Can adjust {len(tunable)} parameters at runtime")

# Or with filtering
param_list = param_manager.get_all_parameters_info()
tunable_list = [p for p in param_list if p.is_runtime_settable()]
```

## Benefits

1. **Type Safety**: Full type hints throughout
2. **Error Handling**: Comprehensive exception handling with clear messages
3. **Version Compatibility**: Works with MongoDB 4.0+ with fallbacks for newer features
4. **Testability**: Fully mocked and tested (no actual MongoDB needed for tests)
5. **Documentation**: Extensive docstrings and examples
6. **Consistency**: Follows same patterns as other package components
7. **Extensibility**: Easy to add new filtering or search methods

## Integration with Existing Code

The parameter manager integrates seamlessly with existing `MongoDBConnection`:

```python
# Existing connection code
from gds_mongodb import MongoDBConnection, MongoDBConfig

config = MongoDBConfig(host='localhost', database='admin')
conn = MongoDBConnection(config=config)
conn.connect()

# New parameter management
from gds_mongodb import MongoDBParameterManager

param_manager = MongoDBParameterManager(conn)
params = param_manager.get_all_parameters()
```

No changes required to existing connection code.

## Testing

Run the test suite:

```bash
cd /home/dpham/src/dbtools/gds_mongodb
pytest tests/test_server_config.py -v
```

Run the examples:

```bash
cd /home/dpham/src/dbtools/gds_mongodb/examples
python parameter_management.py
```

## Future Enhancements (Optional)

Potential additions:
1. **Parameter Setting**: `setParameter` command support
2. **Parameter History**: Track parameter changes over time
3. **Validation**: Validate parameter values against acceptable ranges
4. **Comparison Tools**: Built-in diff functions for comparing environments
5. **Export Formats**: JSON, YAML, or configuration file export
6. **Alerting**: Built-in threshold checking and alerting

## Files Modified/Created Summary

### Created:
1. `gds_mongodb/server_config.py` - Core implementation (462 lines)
2. `examples/parameter_management.py` - Example usage (426 lines)
3. `tests/test_server_config.py` - Unit tests (657 lines)

### Modified:
1. `gds_mongodb/__init__.py` - Added exports and documentation
2. `README.md` - Added parameter management documentation section

### Total New Code: ~1,545 lines

## Conclusion

The MongoDB parameter management implementation follows OOP best practices and integrates cleanly with the existing `gds_mongodb` package architecture. It provides a comprehensive, well-tested, and well-documented solution for retrieving and inspecting MongoDB server configuration parameters at runtime.

The implementation is production-ready and includes:
- ✅ Complete OOP design with separation of concerns
- ✅ Full test coverage with mocked dependencies
- ✅ Comprehensive documentation and examples
- ✅ MongoDB version compatibility (4.0+)
- ✅ Error handling and validation
- ✅ Type hints throughout
- ✅ Consistent with existing package patterns
