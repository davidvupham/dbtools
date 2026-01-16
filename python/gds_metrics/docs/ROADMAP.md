# Revised Architecture: gds_metrics & gds_kafka Packages

## Goal

Create standalone **gds_metrics** and **gds_kafka** packages for reuse across all `gds_*` packages (gds_vault, gds_database, gds_mongodb, gds_snowflake, etc.).

---

## Architecture Overview

```
dbtools/
├── gds_metrics/          # [NEW] Standalone metrics package
│   ├── gds_metrics/
│   │   ├── __init__.py
│   │   ├── base.py       # MetricsCollector protocol
│   │   ├── noop.py       # NoOpMetrics (null object)
│   │   ├── prometheus.py # PrometheusMetrics
│   │   └── console.py    # ConsoleMetrics (for debugging)
│   ├── tests/
│   └── pyproject.toml
│
├── gds_kafka/            # [NEW] Standalone Kafka package
│   ├── gds_kafka/
│   │   ├── __init__.py
│   │   ├── producer.py   # KafkaProducerClient
│   │   ├── consumer.py   # KafkaConsumerClient
│   │   ├── metrics.py    # KafkaMetrics (implements gds_metrics)
│   │   └── logging.py    # KafkaLoggingHandler
│   ├── tests/
│   └── pyproject.toml
│
├── gds_vault/            # [MODIFY] Use new packages
│   └── ... (add metrics & kafka support)
├── gds_database/         # Can also use gds_metrics & gds_kafka
├── gds_snowflake/        # Can also use gds_metrics & gds_kafka
└── ...
```

---

## Phase 1: gds_metrics Package (✅ COMPLETE)

### [NEW] gds_metrics/gds_metrics/base.py (✅ Implemented)

```python
from typing import Protocol, Optional

class MetricsCollector(Protocol):
    """Protocol for metrics collection - implement for any backend."""

    def increment(self, name: str, value: int = 1, labels: dict = None) -> None: ...
    def gauge(self, name: str, value: float, labels: dict = None) -> None: ...
    def histogram(self, name: str, value: float, labels: dict = None) -> None: ...
    def timing(self, name: str, value_ms: float, labels: dict = None) -> None: ...
```

### [NEW] gds_metrics/gds_metrics/noop.py (✅ Implemented)

```python
class NoOpMetrics:
    """Null object - does nothing (default for all packages)."""
    def increment(self, *args, **kwargs): pass
    def gauge(self, *args, **kwargs): pass
    def histogram(self, *args, **kwargs): pass
    def timing(self, *args, **kwargs): pass
```

### [NEW] gds_metrics/gds_metrics/prometheus.py (✅ Implemented)

```python
class PrometheusMetrics:
    """Prometheus implementation (requires prometheus-client)."""
    def __init__(self, prefix: str = "gds", port: int = 8080, start_server: bool = True): ...
```

---

## Phase 2: gds_kafka Package (NEXT STEP)

### [NEW] gds_kafka/gds_kafka/producer.py

```python
class KafkaProducerClient:
    """Reusable Kafka producer with connection management."""

    def __init__(self, bootstrap_servers: str, **config):
        from kafka import KafkaProducer
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, ...)

    def send(self, topic: str, value: dict, key: str = None) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...

    def __enter__(self): return self
    def __exit__(self, ...): self.close()
```

### [NEW] gds_kafka/gds_kafka/metrics.py

```python
from gds_metrics import MetricsCollector

class KafkaMetrics:
    """Metrics collector that streams to Kafka."""

    def __init__(self, producer: KafkaProducerClient, topic: str = "metrics"): ...
    def increment(self, name, value=1, labels=None): ...  # Implements MetricsCollector
```

### [NEW] gds_kafka/gds_kafka/logging.py

```python
import logging

class KafkaLoggingHandler(logging.Handler):
    """Stream Python logs to Kafka topic."""

    def __init__(self, producer: KafkaProducerClient, topic: str = "logs"): ...
    def emit(self, record: logging.LogRecord): ...
```

---

## Phase 3: Integrate with gds_vault

### [MODIFY] gds_vault/pyproject.toml

```toml
[project.optional-dependencies]
metrics = ["gds-metrics"]
kafka = ["gds-kafka"]
async = ["aiohttp>=3.8.0"]
all = ["gds-metrics", "gds-kafka", "aiohttp>=3.8.0"]
```

### [MODIFY] gds_vault/gds_vault/client.py

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gds_metrics import MetricsCollector

class VaultClient:
    def __init__(self, ..., metrics: "MetricsCollector" = None):
        self._metrics = metrics  # Optional metrics integration
```

### Usage Example

```python
from gds_vault import VaultClient
from gds_metrics import PrometheusMetrics
from gds_kafka import KafkaProducerClient, KafkaMetrics, KafkaLoggingHandler
import logging

# Option 1: Prometheus metrics
client = VaultClient(metrics=PrometheusMetrics(prefix="vault"))

# Option 2: Kafka metrics + logging
kafka = KafkaProducerClient("kafka:9092")
client = VaultClient(metrics=KafkaMetrics(kafka, topic="vault-metrics"))

handler = KafkaLoggingHandler(kafka, topic="vault-logs")
logging.getLogger("gds_vault").addHandler(handler)
```

---

## Implementation Order

1. **gds_metrics** - Create standalone metrics package (DONE)
2. **gds_kafka** - Create standalone Kafka package (NEXT)
3. **gds_vault** - Add optional metrics/kafka integration
4. **gds_vault async** - Add AsyncVaultClient
5. **Documentation** - Update READMEs

---

## Verification

```bash
# Test gds_metrics
cd /home/dpham/src/dbtools/gds_metrics && pytest

# Test gds_kafka
cd /home/dpham/src/dbtools/gds_kafka && pytest

# Test gds_vault integration
cd /home/dpham/src/dbtools/gds_vault && pytest
```
