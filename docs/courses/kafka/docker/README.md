# Kafka Docker Environment

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Overview

This Docker Compose configuration provides a complete Kafka development environment for the course tutorials.

## Services

| Service | Port | Description |
|---------|------|-------------|
| **kafka** | 9092 | Kafka broker (KRaft mode) |
| **schema-registry** | 8081 | Schema Registry |
| **kafka-connect** | 8083 | Kafka Connect workers |
| **ksqldb-server** | 8088 | ksqlDB server |
| **ksqldb-cli** | - | ksqlDB CLI |
| **kafka-ui** | 8080 | Web UI |
| **postgres** | 5432 | PostgreSQL (for Connect tutorials) |

## Quick start

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f kafka

# Stop all services
docker compose down

# Stop and remove data
docker compose down -v
```

## Service URLs

| Service | URL |
|---------|-----|
| Kafka | `localhost:9092` (from host) |
| Kafka | `kafka:29092` (from Docker) |
| Schema Registry | `http://localhost:8081` |
| Kafka Connect | `http://localhost:8083` |
| ksqlDB | `http://localhost:8088` |
| Kafka UI | `http://localhost:8080` |
| PostgreSQL | `localhost:5432` |

## Memory requirements

| Configuration | RAM Required |
|---------------|--------------|
| Kafka only | 2 GB |
| + Schema Registry | 3 GB |
| + Kafka Connect | 4 GB |
| + ksqlDB | 5 GB |
| **Full stack** | **6+ GB** |

## Starting selective services

```bash
# Start Kafka only (Module 1-2)
docker compose up -d kafka kafka-ui

# Add Schema Registry (Module 3)
docker compose up -d schema-registry

# Add Kafka Connect (Module 3)
docker compose up -d kafka-connect postgres

# Add ksqlDB (Module 4)
docker compose up -d ksqldb-server ksqldb-cli
```

## Verification commands

```bash
# Check Kafka
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check Schema Registry
curl http://localhost:8081/subjects

# Check Kafka Connect
curl http://localhost:8083/connectors

# Check ksqlDB
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

## Troubleshooting

See the [Troubleshooting Guide](../troubleshooting.md) for common issues.

```bash
# View logs
docker compose logs kafka
docker compose logs schema-registry

# Restart a service
docker compose restart kafka

# Full reset
docker compose down -v
docker compose up -d
```
