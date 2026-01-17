from gds_benchmark.models import BenchmarkStatus
from gds_hammerdb.models import HammerDBConfig
from gds_hammerdb.parser import ResultParser


def test_parse_success():
    parser = ResultParser()
    config = HammerDBConfig(db_type="pg")

    stdout = """
    Vuser 1:RUNNING
    System Under Test : PostgreSQL
    Count : 123456
    NOPM : 12500
    TPM : 45000
    TEST RESULT : PASS
    """

    result = parser.parse(stdout, config, "test-run")

    assert result.status == BenchmarkStatus.COMPLETED
    assert any(m.name == "NOPM" and m.value == 12500 for m in result.metrics)
    assert any(m.name == "TPM" and m.value == 45000 for m in result.metrics)


def test_parse_failure():
    parser = ResultParser()
    config = HammerDBConfig(db_type="pg")

    stdout = """
    Vuser 1:ERROR
    Some connection error occurred
    """

    result = parser.parse(stdout, config, "test-run")

    assert result.status == BenchmarkStatus.FAILED
    assert len(result.metrics) == 0
