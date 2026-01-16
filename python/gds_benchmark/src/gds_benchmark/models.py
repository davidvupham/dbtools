from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class BenchmarkStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Metric:
    """Represents a single metric value."""

    name: str
    value: float
    unit: str
    description: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Represents the result of a benchmark run."""

    run_id: str
    tool_name: str
    status: BenchmarkStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: list[Metric] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_output: Optional[str] = None
    error_message: Optional[str] = None

    def add_metric(self, name: str, value: float, unit: str, description: Optional[str] = None):
        self.metrics.append(Metric(name, value, unit, description))
