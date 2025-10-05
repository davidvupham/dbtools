"""
Example usage of the SnowflakeDatabase and SnowflakeTable modules.

This example demonstrates how to use the database and table metadata retrieval.

Note:
- Use SnowflakeDatabase for database-level metadata
  (databases, schemas, functions, procedures, stages, pipes, tasks, streams)
- Use SnowflakeTable for table-level metadata
  (tables, views, columns)
"""

import json
import logging

from gds_snowflake import SnowflakeConnection, SnowflakeDatabase, SnowflakeTable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_json(data, title):
    """Pretty print JSON data."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(json.dumps(data, indent=2, default=str))


def example_database_metadata():
    """Example of retrieving database-level metadata."""
    # Initialize connection
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        warehouse="COMPUTE_WH",
        role="SYSADMIN",
        database="MYDB",
        vault_secret_path="secret/data/snowflake",
        vault_mount_point="secret",
    )

    try:
        # Connect to Snowflake
        conn.connect()

        # Initialize database metadata retriever
        db_metadata = SnowflakeDatabase(conn)

        # Get all databases
        databases = db_metadata.get_databases()
        print_json(databases, "All Databases")

        # Get specific database info
        db_info = db_metadata.get_database_info("MYDB")
        print_json(db_info, "Database Info: MYDB")

        # Get schemas in a database
        schemas = db_metadata.get_schemas(database_name="MYDB")
        print_json(schemas, "Schemas in MYDB")

        # Get functions
        functions = db_metadata.get_functions(database_name="MYDB", schema_name="PUBLIC")
        print_json(functions, "Functions in MYDB.PUBLIC")

        # Get procedures
        procedures = db_metadata.get_procedures(database_name="MYDB", schema_name="PUBLIC")
        print_json(procedures, "Procedures in MYDB.PUBLIC")

    finally:
        conn.close()


def example_table_metadata():
    """Example of retrieving table-level metadata."""
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    )

    try:
        conn.connect()

        # Initialize table metadata retriever
        table_metadata = SnowflakeTable(conn)

        # Get tables in a schema
        tables = table_metadata.get_tables(database_name="MYDB", schema_name="PUBLIC")
        print_json(tables, "Tables in MYDB.PUBLIC")

        # Get info about a specific table
        table_info = table_metadata.get_table_info(table_name="CUSTOMERS", database_name="MYDB", schema_name="PUBLIC")
        print_json(table_info, "Table Info: CUSTOMERS")

        # Get all columns for the table
        columns = table_metadata.get_columns(table_name="CUSTOMERS", database_name="MYDB", schema_name="PUBLIC")
        print_json(columns, "Columns in CUSTOMERS")

        # Get views
        views = table_metadata.get_views(database_name="MYDB", schema_name="PUBLIC")
        print_json(views, "Views in MYDB.PUBLIC")

    finally:
        conn.close()


def example_data_pipeline_objects():
    """Example of retrieving data pipeline object metadata."""
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    )

    try:
        conn.connect()
        db_metadata = SnowflakeDatabase(conn)

        # Get stages
        stages = db_metadata.get_stages(database_name="MYDB", schema_name="PUBLIC")
        print_json(stages, "Stages in MYDB.PUBLIC")

        # Get file formats
        file_formats = db_metadata.get_file_formats(database_name="MYDB", schema_name="PUBLIC")
        print_json(file_formats, "File Formats in MYDB.PUBLIC")

        # Get pipes (Snowpipe)
        pipes = db_metadata.get_pipes(database_name="MYDB", schema_name="PUBLIC")
        print_json(pipes, "Pipes in MYDB.PUBLIC")

        # Get tasks
        tasks = db_metadata.get_tasks(database_name="MYDB", schema_name="PUBLIC")
        print_json(tasks, "Tasks in MYDB.PUBLIC")

        # Get streams
        streams = db_metadata.get_streams(database_name="MYDB", schema_name="PUBLIC")
        print_json(streams, "Streams in MYDB.PUBLIC")

    finally:
        conn.close()


def example_comprehensive_metadata():
    """Example of retrieving comprehensive metadata."""
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    )

    try:
        conn.connect()

        # Get all database-level metadata
        db_metadata = SnowflakeDatabase(conn)
        all_db_metadata = db_metadata.get_all_database_metadata(database_name="MYDB")

        # Print summary
        print("\n" + "=" * 80)
        print("Database Metadata Summary")
        print("=" * 80)
        print(json.dumps(all_db_metadata["summary"], indent=2))

        # Get all table-level metadata
        table_metadata = SnowflakeTable(conn)
        all_table_metadata = table_metadata.get_all_table_metadata(database_name="MYDB", schema_name="PUBLIC")

        # Print summary
        print("\n" + "=" * 80)
        print("Table Metadata Summary")
        print("=" * 80)
        print(json.dumps(all_table_metadata["summary"], indent=2))

        # Access specific parts
        print(f"\nNumber of functions: {len(all_db_metadata['functions'])}")
        print(f"Number of procedures: {len(all_db_metadata['procedures'])}")
        print(f"Number of tables: {len(all_table_metadata['tables'])}")
        print(f"Number of views: {len(all_table_metadata['views'])}")

    finally:
        conn.close()


def example_context_manager():
    """Example using context manager for automatic connection handling."""
    with SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    ) as conn:
        db_metadata = SnowflakeDatabase(conn)
        table_metadata = SnowflakeTable(conn)

        # Get databases
        databases = db_metadata.get_databases()
        print(f"\nFound {len(databases)} databases:")
        for db in databases:
            print(f"  - {db['DATABASE_NAME']}")

        # Get all tables with views
        all_tables = table_metadata.get_tables(include_views=True)
        print(f"\nFound {len(all_tables)} tables and views")


def example_filtering_results():
    """Example demonstrating various filtering options."""
    with SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    ) as conn:
        table_metadata = SnowflakeTable(conn)

        # Get all tables (no filter)
        all_tables = table_metadata.get_tables()
        print(f"Total tables across all databases: {len(all_tables)}")

        # Get tables in a specific database
        db_tables = table_metadata.get_tables(database_name="MYDB")
        print(f"Tables in MYDB: {len(db_tables)}")

        # Get tables in a specific schema
        schema_tables = table_metadata.get_tables(database_name="MYDB", schema_name="PUBLIC")
        print(f"Tables in MYDB.PUBLIC: {len(schema_tables)}")

        # Include views in results
        tables_and_views = table_metadata.get_tables(database_name="MYDB", include_views=True)
        print(f"Tables and views in MYDB: {len(tables_and_views)}")

        # Get columns for a specific table
        table_columns = table_metadata.get_columns(table_name="CUSTOMERS", database_name="MYDB", schema_name="PUBLIC")
        print("\nColumns in CUSTOMERS table:")
        for col in table_columns:
            print(f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']} " f"(Nullable: {col['IS_NULLABLE']})")


def example_error_handling():
    """Example demonstrating error handling."""
    conn = SnowflakeConnection(
        account="myaccount",
        user="myuser",
        vault_secret_path="secret/data/snowflake",
    )

    try:
        conn.connect()
        db_metadata = SnowflakeDatabase(conn)
        table_metadata = SnowflakeTable(conn)

        # Try to get info about a non-existent database
        db_info = db_metadata.get_database_info("NONEXISTENT_DB")
        if db_info is None:
            print("Database not found")

        # Try to get info about a non-existent table
        table_info = table_metadata.get_table_info("NONEXISTENT_TABLE")
        if table_info is None:
            print("Table not found")

    except Exception as e:
        logger.error("Error retrieving metadata: %s", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Run examples (uncomment the ones you want to try)

    print("\n" + "=" * 80)
    print("Snowflake Metadata Retrieval Examples")
    print("=" * 80)

    # Note: These examples won't run without proper Snowflake credentials
    # Uncomment to run with your credentials:

    # example_database_metadata()
    # example_table_metadata()
    # example_data_pipeline_objects()
    # example_comprehensive_metadata()
    # example_context_manager()
    # example_filtering_results()
    # example_error_handling()
