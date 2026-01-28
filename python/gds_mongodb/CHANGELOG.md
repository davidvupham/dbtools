# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added

- `MongoDBConnection` implementing `DatabaseConnection`, `ConfigurableComponent`, and `ResourceManager` ABCs
- `MongoDBConnectionConfig` for reusable, validated connection configuration
- `MongoDBConfiguration` for runtime server parameter management
- `MongoDBMonitoring` with threshold-based alerting and `AlertManager`
- `MongoDBReplicaSetManager` for replica set administration
- Support for SCRAM-SHA-1, SCRAM-SHA-256, MONGODB-X509, GSSAPI, and PLAIN authentication
- Context manager support for automatic resource cleanup
- Comprehensive unit tests for connection, configuration, and replica set modules
