# Prefect 3.0 Tutorial

Modern Python workflow orchestration for data pipelines.

## Overview

**Prefect** is a workflow orchestration framework that lets you build, schedule, and monitor data pipelines using pure Python. Version 3.0 introduces transactional semantics, improved performance, and an open-source events system.

| | |
|---|---|
| **Package** | `prefect` |
| **Install** | `pip install prefect` |
| **Documentation** | [docs.prefect.io](https://docs.prefect.io/) |
| **GitHub** | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Flows and Tasks](#flows-and-tasks)
4. [Type Hints and Async](#type-hints-and-async)
5. [Task Caching and Retries](#task-caching-and-retries)
6. [Transactional Orchestration](#transactional-orchestration)
7. [Deployments and Scheduling](#deployments-and-scheduling)
8. [Workers and Infrastructure](#workers-and-infrastructure)
9. [Observability](#observability)
10. [Prefect Cloud vs Self-Hosted](#prefect-cloud-vs-self-hosted)

---

## Installation

```bash
pip install prefect
```

Verify installation:

```bash
prefect version
```

Start the local server (optional, for UI):

```bash
prefect server start
```

---

## Quick Start

```python
from prefect import flow, task

@task
def extract_data():
    """Extract data from source."""
    return [1, 2, 3, 4, 5]

@task
def transform_data(data: list[int]) -> list[int]:
    """Transform the data."""
    return [x * 2 for x in data]

@task
def load_data(data: list[int]):
    """Load data to destination."""
    print(f"Loaded: {data}")

@flow(name="ETL Pipeline")
def etl_pipeline():
    """Simple ETL pipeline."""
    raw = extract_data()
    transformed = transform_data(raw)
    load_data(transformed)

# Run the flow
if __name__ == "__main__":
    etl_pipeline()
```

---

## Flows and Tasks

### Flows

Flows are the main containers for your workflow logic:

```python
from prefect import flow

@flow(name="My Data Pipeline", description="Process daily data")
def my_pipeline(date: str):
    print(f"Processing data for {date}")
    return {"status": "complete", "date": date}

# Run with parameters
result = my_pipeline("2024-01-15")
```

### Tasks

Tasks are the individual units of work:

```python
from prefect import task, flow

@task(name="Fetch User Data")
def fetch_users(limit: int = 100) -> list[dict]:
    """Fetch users from API."""
    # Simulated API call
    return [{"id": i, "name": f"User {i}"} for i in range(limit)]

@task(name="Process Users")
def process_users(users: list[dict]) -> dict:
    """Process user data."""
    return {
        "count": len(users),
        "processed": True
    }

@flow
def user_pipeline():
    users = fetch_users(limit=50)
    result = process_users(users)
    return result
```

### Nested Flows (Subflows)

```python
from prefect import flow, task

@flow
def extract_flow():
    return {"data": [1, 2, 3]}

@flow
def transform_flow(data: dict):
    return {"transformed": [x * 2 for x in data["data"]]}

@flow
def main_pipeline():
    # Call subflows
    extracted = extract_flow()
    transformed = transform_flow(extracted)
    return transformed
```

---

## Type Hints and Async

### Type Hints

Prefect 3.0 fully supports type hints:

```python
from prefect import flow, task
from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    name: str
    email: str

@task
def fetch_user(user_id: int) -> UserData:
    return UserData(
        id=user_id,
        name="John Doe",
        email="john@example.com"
    )

@flow
def user_flow(user_id: int) -> UserData:
    return fetch_user(user_id)
```

### Async Support

```python
import asyncio
from prefect import flow, task

@task
async def async_fetch(url: str) -> dict:
    """Async HTTP fetch."""
    await asyncio.sleep(1)  # Simulate async operation
    return {"url": url, "data": "fetched"}

@task
async def async_process(data: dict) -> dict:
    """Async processing."""
    await asyncio.sleep(0.5)
    return {"processed": data}

@flow
async def async_pipeline():
    """Async flow with concurrent tasks."""
    # Run tasks concurrently
    results = await asyncio.gather(
        async_fetch("https://api1.example.com"),
        async_fetch("https://api2.example.com"),
        async_fetch("https://api3.example.com"),
    )

    processed = [await async_process(r) for r in results]
    return processed

# Run async flow
asyncio.run(async_pipeline())
```

---

## Task Caching and Retries

### Caching

Cache task results to avoid redundant computation:

```python
from prefect import task, flow
from prefect.cache_policies import INPUTS
from datetime import timedelta

@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=1))
def expensive_computation(x: int) -> int:
    """Results are cached based on input parameters."""
    print(f"Computing for {x}...")
    return x ** 2

@flow
def cached_flow():
    # First call computes
    result1 = expensive_computation(5)

    # Second call uses cache (same input)
    result2 = expensive_computation(5)

    # Different input, computes again
    result3 = expensive_computation(10)

    return result1, result2, result3
```

### Retries

Automatic retry on failure:

```python
from prefect import task, flow
import random

@task(retries=3, retry_delay_seconds=10)
def flaky_api_call() -> dict:
    """Task that might fail."""
    if random.random() < 0.7:
        raise Exception("API temporarily unavailable")
    return {"status": "success"}

@task(
    retries=5,
    retry_delay_seconds=[1, 5, 10, 30, 60],  # Exponential backoff
)
def api_with_backoff() -> dict:
    """Task with exponential backoff."""
    # Your API call here
    return {"status": "success"}

@flow
def resilient_pipeline():
    result = flaky_api_call()
    return result
```

### Retry with Jitter

```python
from prefect import task
import random

@task(
    retries=3,
    retry_delay_seconds=lambda retry_count: 2 ** retry_count + random.uniform(0, 1)
)
def retry_with_jitter():
    """Retry with exponential backoff and jitter."""
    pass
```

---

## Transactional Orchestration

New in Prefect 3.0: group tasks into atomic transactions.

```python
from prefect import flow, task
from prefect.transactions import transaction

@task
def insert_record(record: dict) -> int:
    """Insert a record and return its ID."""
    print(f"Inserting: {record}")
    return 123

@task
def update_index(record_id: int):
    """Update search index."""
    print(f"Updating index for: {record_id}")

@task
def notify_downstream(record_id: int):
    """Notify downstream systems."""
    print(f"Notifying about: {record_id}")

@flow
def transactional_pipeline(data: dict):
    """All tasks in the transaction succeed or fail together."""
    with transaction():
        record_id = insert_record(data)
        update_index(record_id)
        notify_downstream(record_id)

    return record_id
```

### Rollback Handlers

```python
from prefect import task, flow
from prefect.transactions import transaction

@task
def create_resource() -> str:
    """Create a resource."""
    resource_id = "resource-123"
    print(f"Created: {resource_id}")
    return resource_id

@task
def cleanup_resource(resource_id: str):
    """Cleanup on rollback."""
    print(f"Cleaning up: {resource_id}")

@flow
def pipeline_with_rollback():
    with transaction() as txn:
        resource = create_resource()
        txn.on_rollback(cleanup_resource, resource)

        # If this fails, cleanup_resource is called
        risky_operation(resource)
```

---

## Deployments and Scheduling

### Create a Deployment

```python
from prefect import flow

@flow(log_prints=True)
def my_scheduled_flow():
    print("Running scheduled flow!")

if __name__ == "__main__":
    # Deploy with a schedule
    my_scheduled_flow.serve(
        name="my-deployment",
        cron="0 9 * * *",  # Daily at 9 AM
    )
```

### Deployment with Parameters

```python
from prefect import flow
from datetime import datetime

@flow
def parameterized_flow(date: str, environment: str = "prod"):
    print(f"Processing {environment} data for {date}")

if __name__ == "__main__":
    parameterized_flow.serve(
        name="daily-processing",
        cron="0 8 * * *",
        parameters={"environment": "prod"},
    )
```

### Deploy to Worker Pool

```bash
# Build deployment
prefect deploy --all

# Or programmatically
```

```python
from prefect import flow
from prefect.deployments import Deployment

@flow
def my_flow():
    pass

deployment = Deployment.build_from_flow(
    flow=my_flow,
    name="production-deployment",
    work_pool_name="my-docker-pool",
)

deployment.apply()
```

---

## Workers and Infrastructure

### Start a Worker

```bash
# Start a worker for a work pool
prefect worker start --pool my-pool
```

### Docker Work Pool

```python
from prefect import flow
from prefect.docker import DockerImage

@flow
def containerized_flow():
    print("Running in Docker!")

if __name__ == "__main__":
    containerized_flow.deploy(
        name="docker-deployment",
        work_pool_name="docker-pool",
        image=DockerImage(
            name="my-flow-image",
            dockerfile="Dockerfile"
        ),
    )
```

### Kubernetes Work Pool

```bash
# Create Kubernetes work pool
prefect work-pool create my-k8s-pool --type kubernetes

# Start worker
prefect worker start --pool my-k8s-pool
```

---

## Observability

### Logging

```python
from prefect import flow, task, get_run_logger

@task
def task_with_logging():
    logger = get_run_logger()
    logger.info("Starting task")
    logger.warning("This is a warning")
    logger.error("This is an error")

@flow(log_prints=True)  # Capture print statements
def flow_with_logging():
    logger = get_run_logger()
    logger.info("Flow started")
    print("This will also be logged")
    task_with_logging()
```

### Artifacts

Store and visualize results:

```python
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact, create_table_artifact

@task
def generate_report(data: list[dict]):
    # Create a table artifact
    create_table_artifact(
        key="daily-report",
        table=data,
        description="Daily processing report"
    )

    # Create a markdown artifact
    create_markdown_artifact(
        key="summary",
        markdown=f"## Summary\n\nProcessed {len(data)} records."
    )

@flow
def reporting_flow():
    data = [
        {"name": "Task A", "status": "success", "duration": 10},
        {"name": "Task B", "status": "success", "duration": 15},
    ]
    generate_report(data)
```

### Events and Automations

```python
from prefect import flow
from prefect.events import emit_event

@flow
def flow_with_events():
    # Emit custom event
    emit_event(
        event="data.processed",
        resource={"prefect.resource.id": "my-resource"},
        payload={"records": 1000}
    )
```

---

## Prefect Cloud vs Self-Hosted

| Feature | Self-Hosted (OSS) | Prefect Cloud |
|---------|-------------------|---------------|
| **UI Dashboard** | ✅ Local server | ✅ Hosted |
| **Scheduling** | ✅ | ✅ |
| **Events System** | ✅ (New in 3.0) | ✅ |
| **Automations** | ✅ (New in 3.0) | ✅ |
| **RBAC** | ❌ | ✅ |
| **SSO** | ❌ | ✅ |
| **Audit Logs** | ❌ | ✅ |
| **SLA Monitoring** | ❌ | ✅ |

### Using Prefect Cloud

```bash
# Login to Prefect Cloud
prefect cloud login

# Set workspace
prefect cloud workspace set --workspace my-workspace
```

---

## Quick Reference

### Decorators

```python
@flow(name="...", retries=3, log_prints=True)
@task(name="...", retries=3, cache_policy=INPUTS)
```

### CLI Commands

```bash
prefect server start          # Start local server
prefect deploy                # Deploy flows
prefect worker start          # Start a worker
prefect flow-run create       # Trigger a flow run
prefect deployment run        # Run a deployment
```

### Common Patterns

```python
# Parallel task execution
from prefect import flow, task

@flow
def parallel_flow():
    futures = [my_task.submit(i) for i in range(10)]
    results = [f.result() for f in futures]
```

---

## See Also

- [Prefect Documentation](https://docs.prefect.io/)
- [Prefect Cloud](https://app.prefect.cloud/)
- [Prefect Recipes](https://github.com/PrefectHQ/prefect-recipes)

---

[← Back to Modules Index](../README.md)
