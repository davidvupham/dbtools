"""
GDS MongoDB - MongoDB Management and MonitoringPackage

A comprehensive Python package for MongoDB database interaction, providing
connection management, CRUD operations, server configuration,
monitoring capabilities, and database administration tools.

This package implements the gds-database interface while offering MongoDB-
specific functionality for production database management and operations.

Core Capabilities:
    • Connection Management: Flexible connection configuration with multiple
      authentication mechanisms and connection string support
    • CRUD Operations: Complete create, read, update, delete operations with
      advanced query support
    • Server Parameter Management: Runtime and startup parameter retrieval,
      modification, and inspection
    • Database Administration: Collection management, indexing, and metadata
      access
    • Configuration Management: Reusable configuration classes for consistent
      connection and instance management
    • Monitoring & Operations: Server parameter monitoring and configuration
      tracking

Primary Classes:
    MongoDBConnection: Database connection with full CRUD operations
    MongoDBConnectionConfig: Connection configuration with optional metadata
    MongoDBConfiguration: Server configuration retrieval and modification

Supported Authentication Mechanisms:
    • SCRAM-SHA-256 (default for MongoDB 4.0+)
    • SCRAM-SHA-1
    • MONGODB-X509 (certificate-based authentication)
    • GSSAPI (Kerberos authentication)
    • PLAIN (LDAP authentication)

Common Usage Patterns:

    1. Database Connection and CRUD Operations:
        from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig

        config = MongoDBConnectionConfig(
            host='localhost',
            database='mydb',
            username='admin',
            password='secret',
            auth_mechanism='SCRAM-SHA-256'
        )

        with MongoDBConnection(config=config) as conn:
            # Insert documents
            conn.insert('users', {'name': 'Alice', 'age': 30})

            # Query with filters
            results = conn.execute_query(
                'users',
                {'age': {'$gte': 18}},
                projection={'name': 1, 'age': 1}
            )

            # Update documents
            conn.update('users', {'name': 'Alice'}, {'age': 31})

            # Delete documents
            conn.delete('users', {'age': {'$lt': 18}})

    2. Server Configuration Management:
        from gds_mongodb import (
            MongoDBConnection,
            MongoDBConfiguration
        )

        with MongoDBConnection(host='localhost', database='admin') as conn:
            config = MongoDBConfiguration(conn)

            # Retrieve configuration settings
            log_level = config.get("logLevel")
            all_settings = config.get_all()

            # Inspect configuration details
            details = config.get_details("logLevel")
            if details.get("settable_at_runtime"):
                # Modify runtime configuration
                config.set("logLevel", 2)

    3. Database Administration:
        with MongoDBConnection(host='localhost', database='mydb') as conn:
            # List collections
            collections = conn.get_collection_names()

            # Get collection metadata
            fields = conn.get_field_names('users')

            # Execute aggregations
            pipeline = [
                {'$match': {'age': {'$gte': 18}}},
                {'$group': {'_id': '$country', 'count': {'$sum': 1}}}
            ]
            results = conn.execute_query('users', pipeline=pipeline)

Package Structure:
    gds_mongodb/
    ├── connection.py          # MongoDBConnection implementation
    ├── connection_config.py   # Connection configuration classes
    ├── server_config.py       # Server configuration management classes
    └── __init__.py           # Package exports

For detailed documentation, examples, and advanced usage, see:
    - README.md for comprehensive guide
    - examples/ directory for usage examples
    - MongoDB documentation: https://www.mongodb.com/docs/
"""

from .configuration import MongoDBConfiguration
from .connection import MongoDBConnection
from .connection_config import MongoDBConnectionConfig
from .monitoring import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertType,
    MongoDBMonitoring,
    MonitoringResult,
)
from .replica_set import MongoDBReplicaSetManager

__version__ = "1.0.0"
__all__ = [
    "Alert",
    "AlertManager",
    "AlertSeverity",
    "AlertType",
    "MongoDBConfiguration",
    "MongoDBConnection",
    "MongoDBConnectionConfig",
    "MongoDBMonitoring",
    "MongoDBReplicaSetManager",
    "MonitoringResult",
]
