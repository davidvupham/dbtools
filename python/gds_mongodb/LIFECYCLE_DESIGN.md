# MongoDB OOP Design - Build & Destroy Lifecycle

## Overview

MongoDB has a two-level architecture:
1. **MongoDBEngine** - Individual MongoDB instance (mongod process)
2. **ReplicaSet** - Collection of MongoDBEngine instances working together

---

## Class Design

### MongoDBEngine (Individual Instance)

```python
class MongoDBEngine(DatabaseEngine):
    """
    Represents a single MongoDB instance (mongod process).

    Can exist as:
    - Standalone instance (no replica set)
    - Member of a replica set
    """

    def __init__(
        self,
        connection: DatabaseConnection,
        name: str,
        host: str = "localhost",
        port: int = 27017
    ):
        super().__init__(connection)
        self.name = name
        self.host = host
        self.port = port
        self._replica_set: Optional[ReplicaSet] = None

    # ============================================
    # LIFECYCLE - Individual Instance
    # ============================================

    def build(
        self,
        port: int = None,
        mongodb_version: str = "8.0.1",
        build_version: str = "1.0.1",
        **kwargs
    ) -> OperationResult:
        """
        Build a STANDALONE MongoDB instance.

        Naming Convention:
        - **Image Tag** (standardized): gds-mongodb-{mongodb_version}:{build_version}
        - **Container Name** (custom): {self.name}

        Steps:
        1. Build/pull Docker image: gds-mongodb-{mongodb_version}:{build_version}
        2. Create container with name: {self.name}
        3. Configure to listen on specified port (default: 27017)
        4. Start container and wait for MongoDB to be ready
        5. Verify connection

        Args:
            port: Port number for MongoDB (default: instance's port, usually 27017)
            mongodb_version: MongoDB version (default: "8.0.1")
            build_version: Build version tag (default: "1.0.1")
            platform: "docker", "kubernetes", "bare-metal" (default: docker)
            data_volume: Volume for data persistence
            log_volume: Volume for logs
            **kwargs: Platform-specific options

        Returns:
            OperationResult

        Docker Image & Container:
            Image Tag: gds-mongodb-8.0.1:1.0.1 (shared, reusable)
            Container Name: auscl090041 (unique per instance)

            Multiple containers can use the same image!

        Build Command Example:
            # Build image once
            docker build \
                --build-arg MONGODB_VERSION=8.0.1 \
                --build-arg BUILD_VERSION=1.0.1 \
                -t gds-mongodb-8.0.1:1.0.1 \
                -f docker/mongodb/Dockerfile .

            # Run multiple containers from same image
            docker run -d --name auscl090041 -p 27017:27017 gds-mongodb-8.0.1:1.0.1
            docker run -d --name auscl090042 -p 27018:27017 gds-mongodb-8.0.1:1.0.1

        Example:
            >>> # Build instance named 'auscl090041' using MongoDB 8.0.1
            >>> engine = MongoDBEngine(conn, name="auscl090041")
            >>> result = engine.build(mongodb_version="8.0.1", build_version="1.0.1")
            >>> # Image: gds-mongodb-8.0.1:1.0.1
            >>> # Container: auscl090041

            >>> # Build another instance with same image
            >>> engine2 = MongoDBEngine(conn, name="mongo1", port=27018)
            >>> result = engine2.build(mongodb_version="8.0.1", build_version="1.0.1")
            >>> # Image: gds-mongodb-8.0.1:1.0.1 (reused!)
            >>> # Container: mongo1
        """
        # Use provided port or fall back to instance port (default 27017)
        actual_port = port if port is not None else self.port

        # Standardized Docker image tag
        image_tag = f"gds-mongodb-{mongodb_version}:{build_version}"

        # Custom container name
        container_name = self.name

        # Build/pull image if needed
        # docker build --build-arg MONGODB_VERSION={mongodb_version}
        #              --build-arg BUILD_VERSION={build_version}
        #              -t {image_tag} ...

        # Run container with custom name
        # docker run -d --name {container_name} -p {actual_port}:27017 {image_tag}

        pass

    def destroy(self, force: bool = False, remove_data: bool = False) -> OperationResult:
        """
        Destroy this MongoDB instance.

        Steps:
        1. Shutdown mongod process gracefully (or force)
        2. Remove container / pod
        3. Optionally remove data volumes

        Args:
            force: Force shutdown without graceful period
            remove_data: Also delete data volumes (WARNING: data loss)

        Returns:
            OperationResult

        Warning:
            If this instance is part of a replica set, you should
            remove it from the replica set first using:
            replica_set.remove_member(host)
        """
        pass

    # ============================================
    # REPLICA SET ASSOCIATION
    # ============================================

    @property
    def replica_set(self) -> Optional['ReplicaSet']:
        """Get the replica set this instance belongs to (if any)"""
        return self._replica_set

    @property
    def is_standalone(self) -> bool:
        """Check if this instance is standalone (not in replica set)"""
        return self._replica_set is None

    def join_replica_set(self, replica_set: 'ReplicaSet') -> OperationResult:
        """
        Join this instance to a replica set.
        Internal method called by ReplicaSet.add_member()
        """
        self._replica_set = replica_set
        return OperationResult.success_result("Joined replica set")

    def leave_replica_set(self) -> OperationResult:
        """
        Leave the replica set (become standalone).
        Internal method called by ReplicaSet.remove_member()
        """
        self._replica_set = None
        return OperationResult.success_result("Left replica set")
```

---

### ReplicaSet (Collection of Engines)

```python
class ReplicaSet:
    """
    Manages a MongoDB replica set (collection of MongoDB instances).

    Lifecycle: build() -> operate -> destroy()
    """

    def __init__(
        self,
        name: str,
        member_configs: List[MemberConfig],
        platform: str = "docker"
    ):
        """
        Initialize replica set configuration.

        Args:
            name: Replica set name (e.g., "rs0")
            member_configs: Configuration for each member
            platform: "docker", "kubernetes", "bare-metal"
        """
        self.name = name
        self.member_configs = member_configs
        self.platform = platform
        self.members: List[MongoDBEngine] = []  # Built instances

    # ============================================
    # LIFECYCLE - Replica Set
    # ============================================

    def build(self, **kwargs) -> OperationResult:
        """
        Build the entire replica set with N members.

        Steps:
        1. Create N MongoDB instances based on member_configs
        2. For each member:
           a. Call MongoDBEngine.build()
           b. Wait for instance to be ready
        3. Connect to first instance (will become primary)
        4. Execute rs.initiate() with replica set config
        5. Add remaining members with rs.add()
        6. Wait for primary election
        7. Verify all members are in correct state

        Args:
            **kwargs: Platform-specific build options

        Returns:
            OperationResult with build status

        Example:
            >>> member_configs = [
            ...     MemberConfig(id=0, host="mongo1:27017", priority=2),
            ...     MemberConfig(id=1, host="mongo2:27017", priority=1),
            ...     MemberConfig(id=2, host="mongo3:27017", priority=1),
            ... ]
            >>> replica_set = ReplicaSet("rs0", member_configs)
            >>> result = replica_set.build()
        """
        # 1. Build each MongoDB instance
        for config in self.member_configs:
            engine = MongoDBEngine(
                connection=...,
                name=f"{self.name}_{config.id}",
                host=config.host.split(':')[0],
                port=int(config.host.split(':')[1]) if ':' in config.host else 27017
            )

            # Build the instance
            result = engine.build(platform=self.platform, **kwargs)
            if not result.success:
                # Rollback: destroy already-built instances
                self._rollback_build()
                return result

            # Track member
            self.members.append(engine)
            engine.join_replica_set(self)

        # 2. Initialize replica set
        result = self.initiate()
        if not result.success:
            self._rollback_build()
            return result

        # 3. Add remaining members
        for member in self.members[1:]:
            result = self.add_member(member.host, ...)
            if not result.success:
                # Continue anyway, can be fixed manually
                pass

        return OperationResult.success_result(f"Replica set {self.name} built successfully")

    def destroy(
        self,
        force: bool = False,
        destroy_members: bool = False,
        remove_data: bool = False
    ) -> OperationResult:
        """
        Destroy the replica set.

        Args:
            force: Force shutdown without graceful period
            destroy_members: Also destroy the underlying MongoDB instances
            remove_data: If destroying members, also remove data volumes

        Behavior:
        - destroy_members=False (default):
          * Removes replica set configuration
          * Members become standalone instances
          * Instances remain running

        - destroy_members=True:
          * Removes replica set configuration
          * Destroys all MongoDB instances
          * Optionally removes data volumes

        Returns:
            OperationResult

        Examples:
            >>> # Just disband replica set, keep instances running
            >>> replica_set.destroy(destroy_members=False)

            >>> # Destroy everything including instances
            >>> replica_set.destroy(destroy_members=True, remove_data=True)
        """
        results = []

        # 1. Shutdown secondaries first (graceful)
        for member in self.get_secondaries():
            member.shutdown(force=force)
            member.leave_replica_set()

        # 2. Step down and shutdown primary
        primary = self.get_primary()
        if primary:
            self.step_down_primary()
            primary.shutdown(force=force)
            primary.leave_replica_set()

        # 3. Optionally destroy the MongoDB instances themselves
        if destroy_members:
            for member in self.members:
                result = member.destroy(force=True, remove_data=remove_data)
                results.append(result)

        # 4. Clear member list
        self.members.clear()

        if all(r.success for r in results):
            return OperationResult.success_result(
                f"Replica set {self.name} destroyed. "
                f"Members {'destroyed' if destroy_members else 'left as standalone'}"
            )
        else:
            return OperationResult.failure_result("Some operations failed")

    # ============================================
    # MEMBER MANAGEMENT
    # ============================================

    def add_member_instance(
        self,
        member_config: MemberConfig,
        **kwargs
    ) -> OperationResult:
        """
        Build a new MongoDB instance and add it to replica set.

        Steps:
        1. Create new MongoDBEngine
        2. Build the instance
        3. Add to replica set via rs.add()
        4. Wait for initial sync
        """
        # Create and build new instance
        engine = MongoDBEngine(...)
        result = engine.build(**kwargs)
        if not result.success:
            return result

        # Add to replica set
        result = self.add_member(engine.host, member_config)
        if result.success:
            self.members.append(engine)
            engine.join_replica_set(self)

        return result

    def remove_member_instance(
        self,
        host: str,
        destroy_instance: bool = False
    ) -> OperationResult:
        """
        Remove a member from replica set.

        Args:
            host: Member to remove
            destroy_instance: Also destroy the MongoDB instance

        Behavior:
        - destroy_instance=False: Instance becomes standalone
        - destroy_instance=True: Instance is destroyed
        """
        # Remove from replica set
        result = self.remove_member(host)
        if not result.success:
            return result

        # Find the engine
        engine = next((m for m in self.members if m.host == host), None)
        if engine:
            engine.leave_replica_set()
            self.members.remove(engine)

            # Optionally destroy the instance
            if destroy_instance:
                engine.destroy()

        return result

    # ============================================
    # HELPER METHODS
    # ============================================

    def _rollback_build(self):
        """Rollback failed build by destroying created instances"""
        for member in self.members:
            try:
                member.destroy(force=True, remove_data=True)
            except:
                pass
        self.members.clear()
```

---

## Usage Examples

### 1. Build Standalone MongoDB Instance

```python
# Create and build on default port (27017)
engine = MongoDBEngine(
    connection=connection,
    name="mongo-standalone"
    # port defaults to 27017
)

result = engine.build(
    platform="docker",
    docker_image="mongo:7.0",
    data_volume="mongo-data"
)

# Create on custom port
engine2 = MongoDBEngine(
    connection=connection,
    name="mongo-standalone-2",
    port=27018  # Custom port
)

result = engine2.build(
    platform="docker",
    docker_image="mongo:7.0"
)

# Use the standalone instance
databases = engine.list_databases()

# Destroy when done
engine.destroy(remove_data=True)
```

### 2. Build Replica Set (Creates Instances)

```python
# Define replica set with 3 members on different ports
member_configs = [
    MemberConfig(id=0, host="mongo1:27017", priority=2),  # Primary (higher priority)
    MemberConfig(id=1, host="mongo2:27018", priority=1),  # Secondary on port 27018
    MemberConfig(id=2, host="mongo3:27019", priority=1),  # Secondary on port 27019
]

replica_set = ReplicaSet(name="rs0", member_configs=member_configs)

# Build entire replica set (creates all 3 MongoDB instances)
# Each instance will bind to its configured port
result = replica_set.build(platform="docker")

# Operate on replica set
status = replica_set.get_status()
primary = replica_set.get_primary()
```

### 3. Destroy Replica Set (Keep Instances)

```python
# Disband replica set but keep MongoDB instances running
result = replica_set.destroy(
    destroy_members=False  # Instances become standalone
)

# Now members are standalone MongoDB instances
for member in replica_set.members:
    assert member.is_standalone == True
```

### 4. Destroy Replica Set (Destroy Everything)

```python
# Destroy replica set AND all MongoDB instances
result = replica_set.destroy(
    destroy_members=True,   # Destroy instances too
    remove_data=True        # Delete data volumes
)

# All resources cleaned up
assert len(replica_set.members) == 0
```

### 5. Add New Member to Existing Replica Set

```python
# Build new instance and add to replica set
new_member = MemberConfig(id=3, host="mongo4:27017", priority=1)

result = replica_set.add_member_instance(
    member_config=new_member,
    platform="docker"
)

# Now replica set has 4 members
assert len(replica_set.members) == 4
```

### 6. Remove Member from Replica Set

```python
# Option A: Remove from RS but keep instance running
replica_set.remove_member_instance(
    host="mongo4:27017",
    destroy_instance=False  # Instance becomes standalone
)

# Option B: Remove from RS and destroy instance
replica_set.remove_member_instance(
    host="mongo4:27017",
    destroy_instance=True  # Instance destroyed
)
```

---

## Key Design Decisions

### 1. MongoDBEngine Ownership
- ✅ `MongoDBEngine` can exist independently (standalone)
- ✅ `ReplicaSet` does NOT own the engines, it manages them
- ✅ Engines track their replica set association via `_replica_set`

### 2. Build Separation
- ✅ `MongoDBEngine.build()` - Builds ONE instance
- ✅ `ReplicaSet.build()` - Builds MULTIPLE instances + initializes RS
- ✅ Clear separation of concerns

### 3. Destroy Flexibility
- ✅ `destroy_members=False` - Disband RS, keep standalone instances
- ✅ `destroy_members=True` - Complete cleanup
- ✅ Gives operator control over infrastructure

### 4. Lifecycle Independence
```
MongoDBEngine (Instance)
    ├── Can be built standalone
    ├── Can join replica set later
    ├── Can leave replica set (become standalone)
    └── Can be destroyed independently

ReplicaSet (Collection)
    ├── Builds N MongoDB instances
    ├── Manages them as a group
    ├── Can be destroyed (keeping or destroying instances)
    └── Members can be added/removed dynamically
```

---

## Class Diagram

```
┌─────────────────────────────────────┐
│       MongoDBEngine                 │
│  (Individual mongod instance)       │
│                                     │
│  + build()          ← Build instance│
│  + destroy()        ← Destroy inst  │
│  + is_standalone    ← Check status  │
│  + replica_set      ← Get RS or None│
└─────────────────────────────────────┘
            ↑
            │ 0..1
            │ has
            │
┌─────────────────────────────────────┐
│         ReplicaSet                  │
│  (Collection of instances)          │
│                                     │
│  + members: List[MongoDBEngine]     │
│  + build()          ← Build N inst. │
│  + destroy()        ← Destroy RS    │
│  + add_member_instance()            │
│  + remove_member_instance()         │
└─────────────────────────────────────┘
```

This design gives you maximum flexibility while maintaining clear ownership and lifecycle management.
