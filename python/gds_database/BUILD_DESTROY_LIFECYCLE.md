# Build/Destroy Lifecycle standardization

## Summary

Successfully standardized lifecycle management across all database engines using `build()` and `destroy()` methods.

## Changes Made

### 1. Core ABC (`DatabaseEngine`)
**File:** `/home/dpham/src/dbtools/gds_database/gds_database/engine.py`

Added two abstract lifecycle methods:
- `build(**kwargs) -> OperationResult` - Build/provision engine infrastructure
- `destroy(force=False, **kwargs) -> OperationResult` - Destroy/teardown engine infrastructure

### 2. MongoDB Design
**File:** `/home/dpham/src/dbtools/gds_mongodb/REPLICA_SET_CLASS_DESIGN.md`

Updated `ReplicaSet` class:
- Renamed `deploy()` → `build()`
- Renamed `teardown()` → `destroy()`
- Updated lifecycle documentation: `build() → operate → destroy()`

### 3. Tests
**File:** `/home/dpham/src/dbtools/gds_database/tests/test_ood.py`

Updated all mock engine classes to implement `build()` and `destroy()`.

**Test Results:** ✅ 10/10 tests passing
- New files coverage: 100%
- `engine.py`: 97% (2 lines are abstract bodies)
- `database.py`: 100%
- `metadata.py`: 100%

## API Impact

All concrete `DatabaseEngine` implementations MUST now implement:

```python
class MSSQLEngine(DatabaseEngine):
    def build(self, **kwargs) -> OperationResult:
        """Build MSSQL infrastructure (Docker/K8s/bare-metal)"""
        pass

    def destroy(self, force: bool = False, **kwargs) -> OperationResult:
        """Destroy MSSQL infrastructure"""
        pass
```

## Usage Example

```python
# MongoDB
replica_set = ReplicaSet(name="rs0", members=[...])
replica_set.build()           # Provision replica set
replica_set.get_status()      # Operate
replica_set.destroy()         # Teardown

# MSSQL
engine = MSSQLEngine(config)
engine.build(replicas=3)      # Provision Always On AG
engine.get_databases()        # Operate
engine.destroy(force=False)   # Teardown
```

## Consistency Achieved ✅

- **Standard Terminology:** `build` / `destroy` across all platforms
- **Abstract Methods:** Enforced at ABC level
- **Platform Agnostic:** Works for Docker, Kubernetes, bare-metal
- **Clear Lifecycle:** build → operate → destroy
