# MongoDB Image vs Container Naming

## Overview

MongoDB Docker deployment uses **standardized image tags** and **custom container names**:

- **Image Tag**: `gds-mongodb-{mongodb_version}:{build_version}` (shared, reusable)
- **Container Name**: Custom name per instance (e.g., `auscl090041`, `mongo1`)

---

## Image Tag (Standardized)

**Format:** `gds-mongodb-{mongodb_version}:{build_version}`

**Examples:**
- `gds-mongodb-8.0.1:1.0.1`
- `gds-mongodb-7.0.5:1.0.0`
- `gds-mongodb-6.0.12:1.0.2`

**Purpose:**
- Single image can be reused by multiple containers
- Version controlled and consistent
- Shared across environments

**Build Once, Use Many Times:**
```bash
# Build image once
docker build \
    --build-arg MONGODB_VERSION=8.0.1 \
    --build-arg BUILD_VERSION=1.0.1 \
    -t gds-mongodb-8.0.1:1.0.1 \
    -f docker/mongodb/Dockerfile .

# Use for multiple containers
docker run -d --name auscl090041 -p 27017:27017 gds-mongodb-8.0.1:1.0.1
docker run -d --name auscl090042 -p 27018:27017 gds-mongodb-8.0.1:1.0.1
docker run -d --name mongo1 -p 27019:27017 gds-mongodb-8.0.1:1.0.1
```

---

## Container Name (Custom)

**Format:** Any valid container name

**Examples:**
- `auscl090041` (server hostname)
- `mongo1`, `mongo2` (simple names)
- `rs0-primary`, `rs0-secondary1` (replica set members)

**Purpose:**
- Unique identifier for the running instance
- Human-readable
- Easy to manage

---

## Python OOP Integration

```python
from gds_mongodb import MongoDBEngine

# Instance 1: Server auscl090041
engine1 = MongoDBEngine(
    connection=conn,
    name="auscl090041",  # ← Container name
    port=27017
)

result = engine1.build(
    mongodb_version="8.0.1",  # ← Used for image tag
    build_version="1.0.1"     # ← Used for image tag
)

# Behind the scenes:
# Image: gds-mongodb-8.0.1:1.0.1
# Container: auscl090041
# Port: 27017

# Instance 2: Server auscl090042 (same image, different container)
engine2 = MongoDBEngine(
    connection=conn,
    name="auscl090042",  # ← Different container name
    port=27018
)

result = engine2.build(
    mongodb_version="8.0.1",  # ← Same image
    build_version="1.0.1"
)

# Behind the scenes:
# Image: gds-mongodb-8.0.1:1.0.1 (REUSED!)
# Container: auscl090042
# Port: 27018
```

---

## Replica Set Example

```python
from gds_mongodb import ReplicaSet, MemberConfig

# All members use same image, different container names
member_configs = [
    MemberConfig(id=0, host="auscl090041:27017", priority=2),
    MemberConfig(id=1, host="auscl090042:27017", priority=1),
    MemberConfig(id=2, host="auscl090043:27017", priority=1),
]

replica_set = ReplicaSet(name="rs0", member_configs=member_configs)

# Build creates 3 containers from 1 image
result = replica_set.build(
    mongodb_version="8.0.1",
    build_version="1.0.1"
)

# Result:
# Image: gds-mongodb-8.0.1:1.0.1 (built once)
# Containers: auscl090041, auscl090042, auscl090043 (3 instances)
```

---

## Benefits

✅ **Efficient**: One image, many containers (saves disk space)
✅ **Consistent**: All instances use same MongoDB binary
✅ **Flexible**: Custom names per environment/purpose
✅ **Version Control**: Clear image versioning
✅ **Manageable**: Easy to identify containers by name

---

## Docker Commands

### Build Image
```bash
docker build \
    --build-arg MONGODB_VERSION=8.0.1 \
    --build-arg BUILD_VERSION=1.0.1 \
    -t gds-mongodb-8.0.1:1.0.1 \
    -f docker/mongodb/Dockerfile .
```

### Run Container with Custom Name
```bash
docker run -d \
    --name auscl090041 \
    -p 27017:27017 \
    -v /data/mongodb:/data/mongodb \
    -v /logs/mongodb:/logs/mongodb \
    gds-mongodb-8.0.1:1.0.1
```

### List Containers
```bash
docker ps
# CONTAINER ID   IMAGE                      NAMES
# abc123         gds-mongodb-8.0.1:1.0.1    auscl090041
# def456         gds-mongodb-8.0.1:1.0.1    auscl090042
# ghi789         gds-mongodb-8.0.1:1.0.1    mongo1
```

All using the same image but with different names!
