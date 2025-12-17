# Capstone Project: Production-Grade Snowflake Monitoring System

**Goal**: Build a robust, specialized monitoring application that integrates all course concepts.

## Architecture

1. **Core (Foundations)**:
    * Custom Exception classes (`SnowflakeConnectionError`).
    * Type Hints for all interfaces.
2. **Data Layer (Intermediate)**:
    * Classes for `SnowflakeConnection`, `Table`, `ReplicationStatus`.
    * Context Managers for connection handling.
    * Decorators for retry logic (`@with_retry`).
3. **Concurrency (Advanced)**:
    * Async check of multiple "Failover Groups" simultaneously.
4. **Integration (Applied)**:
    * **SQLModel**: Store historical health metrics in a local SQLite db.
    * **Litestar**: Expose current health status via a REST API (`/health`).
    * **Prefect**: Schedule the monitoring job to run every 5 minutes.

## Deliverables

* Source code in `src/`.
* `Dockerfile` for deployment.
* `README.md` with setup instructions.
* Test suite (`pytest`).
