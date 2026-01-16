from dataclasses import dataclass, field
from typing import Optional

from .constants import (
    BM_TPCC,
    DEFAULT_DURATION_MINUTES,
    DEFAULT_RAMPUP_MINUTES,
    DEFAULT_VIRTUAL_USERS,
)


@dataclass
class HammerDBConfig:
    """Base configuration for HammerDB run."""

    db_type: str
    benchmark_type: str = BM_TPCC
    virtual_users: int = DEFAULT_VIRTUAL_USERS
    rampup_minutes: int = DEFAULT_RAMPUP_MINUTES
    duration_minutes: int = DEFAULT_DURATION_MINUTES
    tpch_scale_factor: int = 1
    autopilot: bool = False
    autopilot_sequence: list[int] = field(default_factory=list)


@dataclass
class PostgresConnectionConfig:
    """PostgreSQL connection details."""

    host: str
    port: int = 5432
    superuser: str = "postgres"
    password: str = ""
    db_name: str = "tpcc"


@dataclass
class MSSQLConnectionConfig:
    """Mssql connection details."""

    server: str
    uid: str = "sa"
    password: str = ""
    instance: Optional[str] = None
