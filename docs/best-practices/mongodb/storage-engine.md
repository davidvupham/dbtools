# MongoDB WiredTiger storage engine configuration

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Topic](https://img.shields.io/badge/Topic-MongoDB-green)

> [!IMPORTANT]
> **Related Docs:** [RHEL Configuration](./rhel-configuration.md) | [Instance Configuration](./instance-configuration.md) | [Replica Set Architecture](./replica-set-architecture.md)

## Table of contents

- [Introduction](#introduction)
- [Cache configuration](#cache-configuration)
- [Compression](#compression)
- [Checkpoints and eviction](#checkpoints-and-eviction)
- [Verification](#verification)

## Introduction

The WiredTiger storage engine is the default and recommended engine for MongoDB. Proper tuning of its cache and compression settings is vital for performance.

[↑ Back to Table of Contents](#table-of-contents)

## Cache configuration

The WiredTiger internal cache works in tandem with the OS filesystem cache.

### Best practices

*   **Default size:** WiredTiger defaults to `max(0.5 * (RAM - 1 GB), 256 MB)`. For dedicated database servers, **do not change this**. The remaining RAM is needed for the OS filesystem cache, connections, and other processes.
*   **Containerized environments:** If running in a container (Docker/Kubernetes) with memory limits, you **must** set `cacheSizeGB`. Without this, MongoDB calculates cache based on the **host's** total RAM, not the container limit, which can cause out-of-memory kills.
    *   Formula: `(Container Limit * 0.5) - 1 GB`.
    *   Example: For a 16 GB container, set cache to approximately 7 GB.
    *   Alternative: Use `--wiredTigerCacheSizePct` (up to 80% of available memory) for vertical scaling scenarios.

> [!WARNING]
> Avoid increasing the WiredTiger internal cache size above its default value. MongoDB performs best with 50-70% of system memory allocated to the WiredTiger cache, unlike other databases that may target 80-90%.

### Configuration

```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 7
```

**Official Reference:** [WiredTiger storage engine](https://www.mongodb.com/docs/manual/core/wiredtiger/) | [cacheSizeGB option](https://www.mongodb.com/docs/manual/reference/configuration-options/#storage.wiredtiger.engineconfig.cachesizegb)

[↑ Back to Table of Contents](#table-of-contents)

## Compression

WiredTiger supports block compression to save disk space and I/O.

### Collection compression

| Workload type | Algorithm | Recommendation |
| :--- | :--- | :--- |
| **General purpose** | `snappy` | **Default.** Good balance of CPU and storage. |
| **Read-heavy / archival** | `zstd` | Higher compression ratio, moderate CPU. Default for time series collections. |
| **High compression needs** | `zlib` | Better ratio than snappy, slower than zstd. Legacy option. |
| **Throughput critical** | `none` | Avoids CPU overhead but increases disk I/O. Rarely recommended on modern SSDs. |

### Configuration

```yaml
storage:
  wiredTiger:
    collectionConfig:
      blockCompressor: snappy
```

### Journal and index compression

*   **Journal compression:** Uses `snappy` by default. Configurable via `storage.wiredTiger.engineConfig.journalCompressor`. Journal records of 128 bytes or smaller are not compressed.
*   **Index compression:** Uses **prefix compression** by default for all indexes. Configurable via `storage.wiredTiger.indexConfig.prefixCompression`.

> [!NOTE]
> Starting in MongoDB 5.2, time series collections use **column compression** with zstd, which significantly improves both disk usage and WiredTiger cache efficiency.

**Official Reference:** [WiredTiger compression](https://www.mongodb.com/docs/manual/core/wiredtiger/) | [blockCompressor option](https://www.mongodb.com/docs/manual/reference/configuration-options/#storage.wiredtiger.collectionconfig.blockcompressor)

[↑ Back to Table of Contents](#table-of-contents)

## Checkpoints and eviction

WiredTiger writes data to disk via checkpoints (every 60 seconds) and manages memory through eviction threads.

### Checkpoints

*   MongoDB creates a WiredTiger checkpoint every **60 seconds** by default.
*   During a new checkpoint write, the previous checkpoint remains valid.
*   If MongoDB terminates during a checkpoint, it recovers from the last valid checkpoint using the write-ahead journal.

### Eviction thresholds

WiredTiger uses background eviction threads and, under pressure, application threads to manage cache memory. Monitor these thresholds:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `eviction_target` | **80%** | Background eviction begins when overall cache usage exceeds this. |
| `eviction_trigger` | **95%** | Application threads are throttled when overall cache exceeds this. |
| `eviction_dirty_target` | **5%** | Background eviction of dirty pages begins at this threshold. |
| `eviction_dirty_trigger` | **20%** | Application threads are throttled when dirty data exceeds this. |

> [!WARNING]
> If the dirty cache percentage frequently reaches `eviction_dirty_trigger` (20%), writes may stall as application threads are conscripted for eviction. If overall cache reaches 100%, all operations stall. Monitor `db.serverStatus().wiredTiger.cache` for early warning signs.

> [!NOTE]
> Tuning eviction threads and thresholds is an advanced operation. Do not modify these parameters unless advised by MongoDB Support. The defaults are suitable for most workloads.

**Official Reference:** [WiredTiger storage engine](https://www.mongodb.com/docs/manual/core/wiredtiger/)

[↑ Back to Table of Contents](#table-of-contents)

## Verification

### Check cache size

Verify the configured cache size matches your expectation:
```javascript
db.serverStatus().wiredTiger.cache["maximum bytes configured"] / 1024 / 1024 / 1024
```

### Check compression

Verify a collection's compression setting:
```javascript
db.getCollection("myCollection").stats().wiredTiger.creationString
```
Look for `block_compressor=snappy` (or `zstd`, `zlib`, `none`).

### Check dirty cache percentage

Monitor the current dirty cache ratio:
```javascript
var cache = db.serverStatus().wiredTiger.cache;
var dirtyBytes = cache["tracked dirty bytes in the cache"];
var totalBytes = cache["maximum bytes configured"];
print("Dirty cache: " + (dirtyBytes / totalBytes * 100).toFixed(2) + "%");
```

[↑ Back to Table of Contents](#table-of-contents)
