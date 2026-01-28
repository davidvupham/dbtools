# MongoDB WiredTiger Storage Engine Configuration

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Database Reliability Engineering
> **Status:** Draft

**Table of Contents**

- [Introduction](#introduction)
- [Cache Configuration](#cache-configuration)
- [Compression](#compression)
- [Checkpoints and Eviction](#checkpoints-and-eviction)
- [Verification](#verification)

## Introduction

The WiredTiger storage engine is the default and recommended engine for MongoDB. Proper tuning of its cache and compression settings is vital for performance.

## Cache Configuration

The WiredTiger internal cache works in tandem with the filesystem cache.

### Best Practices

*   **Default Size:** WiredTiger defaults to 50% of RAM minus 1 GB. For dedicated database servers, **do not change this**. The remaining RAM is needed for the OS filesystem cache and connections.
*   **Containerized Environments:** If running in a container (Docker/Kubernetes) with memory limits, you **MUST** set `cacheSizeGB`.
    *   Formula: `(Container Limit * 0.5) - 1GB`.
    *   Example: For a 16GB container, set cache to ~7GB.

### Configuration
```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 7
```

**Official Reference:** [WiredTiger Cache Settings](https://www.mongodb.com/docs/manual/reference/configuration-options/#storage.wiredtiger.engineconfig.cachesizegb)

## Compression

WiredTiger supports block compression to save disk space and I/O.

### Recommendations

| Workload Type | Algorithm | Recommendation |
| :--- | :--- | :--- |
| **General Purpose** | `snappy` | **Default.** Good balance of CPU/Storage. |
| **Read-Heavy / Archival** | `zstd` | Higher compression, higher CPU usage. Good for time-series. |
| **Throughput Critical** | `none` | Avoids CPU overhead but increases Disk I/O. Rarely recommended on modern SSDs. |

### Configuration
```yaml
storage:
  wiredTiger:
    collectionConfig:
      blockCompressor: snappy
```

**Official Reference:** [WiredTiger Compression](https://www.mongodb.com/docs/manual/reference/configuration-options/#storage.wiredtiger.collectionconfig.blockcompressor)

## Checkpoints and Eviction

WiredTiger writes data to disk via checkpoints (typically every 60 seconds) and eviction threads.

*   **Dirty Cache:** Monitor the "dirty" cache percentage. It should generally stay under 5%. If it frequently hits 20%, writes may stall.
*   **Eviction triggers:** Tuning eviction threads is complex and generally discouraged unless advised by MongoDB Support.

## Verification

### Check Cache Size
Verify the configured cache size matches your expectation:
```javascript
db.serverStatus().wiredTiger.cache["maximum bytes configured"] / 1024 / 1024 / 1024
```

### Check Compression
Verify a collection's compression setting:
```javascript
db.getCollection("myCollection").stats().wiredTiger.creationString
```
Look for `block_compressor=snappy`.
