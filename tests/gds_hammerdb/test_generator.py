from gds_hammerdb.constants import DB_MSSQL_LINUX, DB_POSTGRES
from gds_hammerdb.generator import ScriptGenerator
from gds_hammerdb.models import (
    HammerDBConfig,
    MSSQLConnectionConfig,
    PostgresConnectionConfig,
)


def test_generate_postgres_tpcc():
    generator = ScriptGenerator()
    h_config = HammerDBConfig(db_type=DB_POSTGRES, virtual_users=5)
    pg_config = PostgresConnectionConfig(host="localhost", password="secure_password")

    script = generator.generate_postgres_tpcc(h_config, pg_config)

    assert "dbset db pg" in script
    assert 'diset connection pg_host "localhost"' in script
    assert 'diset connection pg_pass "secure_password"' in script
    assert "vuset vu 5" in script
    assert "vuset logtotemp 1" in script


def test_generate_mssql_tpcc():
    generator = ScriptGenerator()
    h_config = HammerDBConfig(db_type=DB_MSSQL_LINUX, virtual_users=10)
    ms_config = MSSQLConnectionConfig(server="10.0.0.1", password="sa_password")

    script = generator.generate_mssql_tpcc(h_config, ms_config)

    assert "dbset db mssqls" in script
    assert 'diset connection mssqls_server "10.0.0.1"' in script
    assert 'diset connection mssqls_pass "sa_password"' in script
    assert "vuset vu 10" in script
