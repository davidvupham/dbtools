#!/usr/bin/env python3
"""
Fix Liquibase baseline XML files for SQL Server

This script addresses common issues with Liquibase-generated baseline files:
1. Adds missing schemaName attributes to tables and views
2. Adds schema creation changeset at the beginning
3. Extracts and adds stored procedures and functions from the database
4. Provides option to update changeset IDs to be more descriptive

Usage:
    python fix-liquibase-baseline.py --baseline-file /path/to/V0000__baseline.xml \
                                      --schema app \
                                      [--add-db-objects] \
                                      [--server localhost] \
                                      [--database testdb] \
                                      [--username sa] \
                                      [--password 'YourStrong!Passw0rd']
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import pyodbc

    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fix Liquibase baseline XML files for SQL Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--baseline-file", required=True, help="Path to the baseline XML file to fix"
    )
    parser.add_argument(
        "--schema", default="app", help="Schema name to use (default: app)"
    )
    parser.add_argument(
        "--add-db-objects",
        action="store_true",
        help="Connect to database and extract stored procedures and functions",
    )
    parser.add_argument(
        "--server", default="localhost", help="SQL Server hostname (default: localhost)"
    )
    parser.add_argument(
        "--port", default="1433", help="SQL Server port (default: 1433)"
    )
    parser.add_argument(
        "--database", default="testdb", help="Database name (default: testdb)"
    )
    parser.add_argument(
        "--username", default="sa", help="Database username (default: sa)"
    )
    parser.add_argument("--password", help="Database password")
    parser.add_argument("--output", help="Output file (default: overwrites input file)")
    parser.add_argument(
        "--backup", action="store_true", help="Create backup of original file"
    )

    return parser.parse_args()


def backup_file(filepath: Path) -> Path:
    """Create a backup of the original file"""
    backup_path = filepath.with_suffix(".xml.bak")
    counter = 1
    while backup_path.exists():
        backup_path = filepath.with_suffix(f".xml.bak.{counter}")
        counter += 1

    backup_path.write_text(filepath.read_text())
    print(f"✓ Created backup: {backup_path}")
    return backup_path


def add_schema_attributes(xml_content: str, schema: str) -> str:
    """Add schemaName attribute to createTable and createView elements"""

    # Fix createTable without schemaName
    xml_content = re.sub(
        r'<createTable\s+tableName="([^"]+)"(?!\s+schemaName)',
        f'<createTable schemaName="{schema}" tableName="\\1"',
        xml_content,
    )

    # Fix createView without schemaName
    xml_content = re.sub(
        r'<createView\s+(?=.*?viewName="[^"]+")',
        f'<createView schemaName="{schema}" ',
        xml_content,
    )

    # Also fix if viewName comes first
    xml_content = re.sub(
        r'<createView\s+viewName="([^"]+)"(?!\s+schemaName)',
        f'<createView schemaName="{schema}" viewName="\\1"',
        xml_content,
    )

    return xml_content


def create_schema_changeset(schema: str, author: str = "system") -> str:
    """Create a changeset for schema creation"""
    return f'''    <changeSet id="baseline-schema-{schema}" author="{author}">
        <sql>
            IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{schema}')
            BEGIN
                EXEC('CREATE SCHEMA {schema}')
            END
        </sql>
    </changeSet>

'''


def get_database_objects(
    server: str, port: str, database: str, username: str, password: str, schema: str
) -> Tuple[List[str], List[str]]:
    """Connect to database and retrieve stored procedures and functions"""

    if not PYODBC_AVAILABLE:
        print("Warning: pyodbc not available. Install with: pip install pyodbc")
        return [], []

    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Get stored procedures
        procs_query = """
        SELECT
            o.name AS object_name,
            m.definition
        FROM sys.sql_modules m
        INNER JOIN sys.objects o ON m.object_id = o.object_id
        WHERE o.type = 'P'
          AND SCHEMA_NAME(o.schema_id) = ?
        ORDER BY o.name
        """

        cursor.execute(procs_query, schema)
        procedures = []
        for row in cursor.fetchall():
            proc_name = row.object_name
            definition = row.definition
            # Convert CREATE PROCEDURE to CREATE OR ALTER PROCEDURE
            definition = re.sub(
                r"\bCREATE\s+PROCEDURE\b",
                "CREATE OR ALTER PROCEDURE",
                definition,
                flags=re.IGNORECASE,
            )
            procedures.append((proc_name, definition))

        # Get functions
        funcs_query = """
        SELECT
            o.name AS object_name,
            m.definition
        FROM sys.sql_modules m
        INNER JOIN sys.objects o ON m.object_id = o.object_id
        WHERE o.type IN ('FN', 'IF', 'TF')
          AND SCHEMA_NAME(o.schema_id) = ?
        ORDER BY o.name
        """

        cursor.execute(funcs_query, schema)
        functions = []
        for row in cursor.fetchall():
            func_name = row.object_name
            definition = row.definition
            # Convert CREATE FUNCTION to CREATE OR ALTER FUNCTION
            definition = re.sub(
                r"\bCREATE\s+FUNCTION\b",
                "CREATE OR ALTER FUNCTION",
                definition,
                flags=re.IGNORECASE,
            )
            functions.append((func_name, definition))

        conn.close()

        return procedures, functions

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return [], []


def create_procedure_changeset(
    proc_name: str, definition: str, schema: str, author: str = "system"
) -> str:
    """Create a changeset for a stored procedure"""
    # Clean up the definition
    definition = definition.strip()

    return f'''    <changeSet id="baseline-proc-{proc_name}" author="{author}" runOnChange="true">
        <sql splitStatements="false">
            {definition}
        </sql>
    </changeSet>

'''


def create_function_changeset(
    func_name: str, definition: str, schema: str, author: str = "system"
) -> str:
    """Create a changeset for a function"""
    # Clean up the definition
    definition = definition.strip()

    return f'''    <changeSet id="baseline-func-{func_name}" author="{author}" runOnChange="true">
        <sql splitStatements="false">
            {definition}
        </sql>
    </changeSet>

'''


def fix_baseline_xml(
    filepath: Path,
    schema: str,
    procedures: List[Tuple[str, str]] = None,
    functions: List[Tuple[str, str]] = None,
    output_path: Path = None,
) -> None:
    """Fix the baseline XML file"""

    print(f"Processing: {filepath}")

    # Read the original file
    content = filepath.read_text()

    # Step 1: Add schemaName attributes
    print("  • Adding schemaName attributes...")
    content = add_schema_attributes(content, schema)

    # Step 2: Add schema creation changeset at the beginning
    print(f"  • Adding schema creation changeset for '{schema}'...")

    # Find the first changeSet and insert schema creation before it
    schema_changeset = create_schema_changeset(schema)

    # Find the position after the opening databaseChangeLog tag
    match = re.search(r"(<databaseChangeLog[^>]*>)", content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + "\n" + schema_changeset + content[insert_pos:]

    # Step 3: Add stored procedures and functions if provided
    if procedures or functions:
        print("  • Adding stored procedures and functions...")

        # Find the position before the closing databaseChangeLog tag
        match = re.search(r"</databaseChangeLog>\s*$", content)
        if match:
            insert_pos = match.start()

            additional_changesets = []

            # Add procedures
            if procedures:
                additional_changesets.append("    <!-- Stored Procedures -->")
                for proc_name, definition in procedures:
                    changeset = create_procedure_changeset(
                        proc_name, definition, schema
                    )
                    additional_changesets.append(changeset)
                print(f"    ✓ Added {len(procedures)} stored procedure(s)")

            # Add functions
            if functions:
                additional_changesets.append("    <!-- Functions -->")
                for func_name, definition in functions:
                    changeset = create_function_changeset(func_name, definition, schema)
                    additional_changesets.append(changeset)
                print(f"    ✓ Added {len(functions)} function(s)")

            content = (
                content[:insert_pos]
                + "\n".join(additional_changesets)
                + "\n"
                + content[insert_pos:]
            )

    # Write the output
    output = output_path or filepath
    output.write_text(content)
    print(f"✓ Fixed baseline written to: {output}")


def main():
    args = parse_args()

    baseline_file = Path(args.baseline_file)

    if not baseline_file.exists():
        print(f"Error: File not found: {baseline_file}")
        sys.exit(1)

    # Create backup if requested
    if args.backup:
        backup_file(baseline_file)

    # Get database objects if requested
    procedures = []
    functions = []

    if args.add_db_objects:
        if not args.password:
            print("Error: --password required when using --add-db-objects")
            sys.exit(1)

        print(f"Connecting to {args.server}:{args.port}/{args.database}...")
        procedures, functions = get_database_objects(
            args.server,
            args.port,
            args.database,
            args.username,
            args.password,
            args.schema,
        )

        if not procedures and not functions:
            print("Warning: No stored procedures or functions found")

    # Determine output path
    output_path = Path(args.output) if args.output else None

    # Fix the baseline
    fix_baseline_xml(baseline_file, args.schema, procedures, functions, output_path)

    print("\n✓ Done! Review the fixed baseline file before using it.")


if __name__ == "__main__":
    main()
