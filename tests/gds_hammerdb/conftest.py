"""Shared fixtures for gds_hammerdb tests."""

import pytest
from gds_hammerdb.constants import BM_TPCC, DB_POSTGRES
from gds_hammerdb.models import (
    HammerDBConfig,
    MSSQLConnectionConfig,
    PostgresConnectionConfig,
)


@pytest.fixture
def postgres_config():
    """Sample PostgreSQL connection configuration."""
    return PostgresConnectionConfig(
        host="localhost",
        port=5432,
        superuser="postgres",
        password="test_password",
        db_name="tpcc",
    )


@pytest.fixture
def mssql_config():
    """Sample SQL Server connection configuration."""
    return MSSQLConnectionConfig(
        server="localhost",
        uid="sa",
        password="test_password",
    )


@pytest.fixture
def hammerdb_tpcc_config():
    """Sample HammerDB TPC-C configuration."""
    return HammerDBConfig(
        db_type=DB_POSTGRES,
        benchmark_type=BM_TPCC,
        virtual_users=4,
        rampup_minutes=2,
        duration_minutes=5,
    )


@pytest.fixture
def mock_executor(mocker):
    """Mock the HammerDB CLI executor."""
    mock = mocker.patch("gds_hammerdb.cli.HammerDBExecutor")
    mock.return_value.run_script.return_value = """
    System Under Test : PostgreSQL
    NOPM : 12500
    TPM : 45000
    TEST RESULT : PASS
    """
    return mock
