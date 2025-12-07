from gds_hammerdb.constants import BM_TPCH, DB_POSTGRES
from gds_hammerdb.generator import ScriptGenerator
from gds_hammerdb.models import HammerDBConfig, PostgresConnectionConfig


def test_generate_postgres_tpch():
    generator = ScriptGenerator()
    h_config = HammerDBConfig(
        db_type=DB_POSTGRES, benchmark_type=BM_TPCH, tpch_scale_factor=10
    )
    pg_config = PostgresConnectionConfig(host="localhost", password="pass")

    script = generator.generate_postgres_tpch(h_config, pg_config)

    assert "dbset bm TPC-H" in script
    assert 'diset tpch pg_scale_fact "10"' in script
    assert "vurun" in script


def test_generate_build_script_postgres_tpcc():
    generator = ScriptGenerator()
    h_config = HammerDBConfig(
        db_type=DB_POSTGRES, benchmark_type="TPC-C", virtual_users=5
    )
    pg_config = PostgresConnectionConfig(host="localhost")

    script = generator.generate_build_script(h_config, pg_config)

    assert "buildschema" in script
    assert 'diset tpcc pg_num_vu "5"' in script
