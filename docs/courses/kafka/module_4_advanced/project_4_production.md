# Project 4: Production-Ready Kafka Deployment

**[← Back to Module 4](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Estimated Time:** 6-8 hours
> **Difficulty:** Advanced

## Project Overview

In this project, you will deploy a production-ready Kafka cluster with enterprise features including security, monitoring, high availability, and operational procedures. This simulates a real-world production deployment scenario.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION KAFKA ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌─────────────────────────────────────────────────────────────┐     │
│    │                    MONITORING STACK                          │     │
│    │  ┌──────────┐   ┌──────────────┐   ┌───────────────────┐   │     │
│    │  │Prometheus│──►│   Grafana    │   │   Alertmanager    │   │     │
│    │  └────┬─────┘   └──────────────┘   └───────────────────┘   │     │
│    └───────│─────────────────────────────────────────────────────┘     │
│            │ scrape                                                     │
│            ▼                                                            │
│    ┌─────────────────────────────────────────────────────────────┐     │
│    │                    KAFKA CLUSTER (KRaft)                     │     │
│    │                                                               │     │
│    │  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │     │
│    │  │Broker 1 │    │Broker 2 │    │Broker 3 │                  │     │
│    │  │ :9092   │◄──►│ :9093   │◄──►│ :9094   │                  │     │
│    │  │ JMX     │    │ JMX     │    │ JMX     │                  │     │
│    │  └────┬────┘    └────┬────┘    └────┬────┘                  │     │
│    │       │              │              │                        │     │
│    │       └──────────────┼──────────────┘                        │     │
│    │                      │                                        │     │
│    │              ┌───────▼───────┐                               │     │
│    │              │Schema Registry│                               │     │
│    │              └───────────────┘                               │     │
│    │                                                               │     │
│    │    Security: TLS + SASL/SCRAM + ACLs                         │     │
│    └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│    ┌─────────────────────────────────────────────────────────────┐     │
│    │                    CLIENT LAYER                              │     │
│    │  ┌──────────┐   ┌──────────┐   ┌──────────────────────┐    │     │
│    │  │Producers │   │Consumers │   │   Kafka Connect      │    │     │
│    │  │(Secured) │   │(Secured) │   │   (Secured)          │    │     │
│    │  └──────────┘   └──────────┘   └──────────────────────┘    │     │
│    └─────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Learning Objectives

By completing this project, you will:

- Deploy a multi-broker Kafka cluster with KRaft
- Configure TLS encryption and SASL authentication
- Set up fine-grained access control with ACLs
- Deploy Prometheus, Grafana, and Alertmanager for monitoring
- Create operational runbooks and procedures
- Implement backup and disaster recovery strategies

## Prerequisites

- Completed Module 4 lessons (13-17)
- Docker and Docker Compose installed
- Basic understanding of TLS/SSL certificates
- 16 GB RAM recommended (for full stack)

---

## Part 1: Cluster Infrastructure

### 1.1 Project Structure

```
kafka-production/
├── docker-compose.yml          # Main compose file
├── docker-compose.override.yml # Local overrides
├── .env                        # Environment variables
├── certs/                      # TLS certificates
│   ├── ca/
│   ├── broker/
│   └── client/
├── config/
│   ├── kafka/                  # Broker configurations
│   ├── prometheus/             # Prometheus config
│   ├── grafana/                # Grafana dashboards
│   └── alertmanager/           # Alert rules
├── scripts/
│   ├── generate-certs.sh       # Certificate generation
│   ├── create-users.sh         # SCRAM user creation
│   ├── configure-acls.sh       # ACL configuration
│   └── health-check.sh         # Health monitoring
└── runbooks/
    ├── upgrade.md              # Upgrade procedure
    ├── disaster-recovery.md    # DR procedures
    └── troubleshooting.md      # Common issues
```

### 1.2 Environment Configuration

Create `.env`:

```bash
# .env - Production Kafka Configuration

# Cluster Settings
CLUSTER_ID=MkU3OEVBNTcwNTJENDM2Qk
KAFKA_VERSION=7.5.0

# Security
TLS_PASSWORD=kafka-tls-secret-2026
SCRAM_ADMIN_PASSWORD=admin-secure-password
SCRAM_APP_PASSWORD=app-secure-password

# Network
KAFKA_EXTERNAL_HOST=localhost
KAFKA_INTERNAL_NETWORK=kafka-network

# Monitoring
PROMETHEUS_RETENTION=15d
GRAFANA_ADMIN_PASSWORD=grafana-admin-2026

# Resource Limits
KAFKA_HEAP_OPTS=-Xms2g -Xmx2g
```

### 1.3 Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
# docker-compose.yml - Production Kafka Stack
version: '3.8'

networks:
  kafka-network:
    driver: bridge
    name: kafka-network

volumes:
  kafka1-data:
  kafka2-data:
  kafka3-data:
  prometheus-data:
  grafana-data:

services:
  # ============================================================
  # KAFKA BROKERS (3-node KRaft cluster)
  # ============================================================

  kafka1:
    image: confluentinc/cp-kafka:${KAFKA_VERSION:-7.5.0}
    container_name: kafka1
    hostname: kafka1
    networks:
      - kafka-network
    ports:
      - "9092:9092"
      - "9192:9192"  # JMX
    volumes:
      - kafka1-data:/var/lib/kafka/data
      - ./certs:/etc/kafka/secrets
      - ./config/kafka:/etc/kafka/config
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:29093,2@kafka2:29093,3@kafka3:29093
      CLUSTER_ID: ${CLUSTER_ID}

      # Listeners
      KAFKA_LISTENERS: PLAINTEXT://kafka1:29092,CONTROLLER://kafka1:29093,EXTERNAL://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:29092,EXTERNAL://${KAFKA_EXTERNAL_HOST:-localhost}:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:SASL_SSL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT

      # Security - SASL/SCRAM
      KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
      KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAINTEXT

      # Security - SSL
      KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/broker/kafka1.keystore.jks
      KAFKA_SSL_KEYSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_KEY_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/broker/kafka.truststore.jks
      KAFKA_SSL_TRUSTSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM: https

      # Replication
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2

      # Retention
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 300000

      # Performance
      KAFKA_NUM_NETWORK_THREADS: 8
      KAFKA_NUM_IO_THREADS: 16
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"

      # JMX for monitoring
      KAFKA_JMX_PORT: 9192
      KAFKA_JMX_HOSTNAME: kafka1
      KAFKA_OPTS: -javaagent:/etc/kafka/config/jmx_prometheus_javaagent.jar=7071:/etc/kafka/config/kafka-metrics.yml

      # Heap settings
      KAFKA_HEAP_OPTS: ${KAFKA_HEAP_OPTS:--Xms1g -Xmx1g}
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:29092"]
      interval: 30s
      timeout: 10s
      retries: 5

  kafka2:
    image: confluentinc/cp-kafka:${KAFKA_VERSION:-7.5.0}
    container_name: kafka2
    hostname: kafka2
    networks:
      - kafka-network
    ports:
      - "9093:9093"
      - "9193:9193"
    volumes:
      - kafka2-data:/var/lib/kafka/data
      - ./certs:/etc/kafka/secrets
      - ./config/kafka:/etc/kafka/config
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:29093,2@kafka2:29093,3@kafka3:29093
      CLUSTER_ID: ${CLUSTER_ID}
      KAFKA_LISTENERS: PLAINTEXT://kafka2:29092,CONTROLLER://kafka2:29093,EXTERNAL://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:29092,EXTERNAL://${KAFKA_EXTERNAL_HOST:-localhost}:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:SASL_SSL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
      KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/broker/kafka2.keystore.jks
      KAFKA_SSL_KEYSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_KEY_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/broker/kafka.truststore.jks
      KAFKA_SSL_TRUSTSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM: https
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_NUM_NETWORK_THREADS: 8
      KAFKA_NUM_IO_THREADS: 16
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
      KAFKA_JMX_PORT: 9193
      KAFKA_JMX_HOSTNAME: kafka2
      KAFKA_OPTS: -javaagent:/etc/kafka/config/jmx_prometheus_javaagent.jar=7071:/etc/kafka/config/kafka-metrics.yml
      KAFKA_HEAP_OPTS: ${KAFKA_HEAP_OPTS:--Xms1g -Xmx1g}
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:29092"]
      interval: 30s
      timeout: 10s
      retries: 5

  kafka3:
    image: confluentinc/cp-kafka:${KAFKA_VERSION:-7.5.0}
    container_name: kafka3
    hostname: kafka3
    networks:
      - kafka-network
    ports:
      - "9094:9094"
      - "9194:9194"
    volumes:
      - kafka3-data:/var/lib/kafka/data
      - ./certs:/etc/kafka/secrets
      - ./config/kafka:/etc/kafka/config
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka1:29093,2@kafka2:29093,3@kafka3:29093
      CLUSTER_ID: ${CLUSTER_ID}
      KAFKA_LISTENERS: PLAINTEXT://kafka3:29092,CONTROLLER://kafka3:29093,EXTERNAL://0.0.0.0:9094
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:29092,EXTERNAL://${KAFKA_EXTERNAL_HOST:-localhost}:9094
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:SASL_SSL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
      KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/broker/kafka3.keystore.jks
      KAFKA_SSL_KEYSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_KEY_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/broker/kafka.truststore.jks
      KAFKA_SSL_TRUSTSTORE_PASSWORD: ${TLS_PASSWORD}
      KAFKA_SSL_ENDPOINT_IDENTIFICATION_ALGORITHM: https
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_NUM_NETWORK_THREADS: 8
      KAFKA_NUM_IO_THREADS: 16
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
      KAFKA_JMX_PORT: 9194
      KAFKA_JMX_HOSTNAME: kafka3
      KAFKA_OPTS: -javaagent:/etc/kafka/config/jmx_prometheus_javaagent.jar=7071:/etc/kafka/config/kafka-metrics.yml
      KAFKA_HEAP_OPTS: ${KAFKA_HEAP_OPTS:--Xms1g -Xmx1g}
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:29092"]
      interval: 30s
      timeout: 10s
      retries: 5

  # ============================================================
  # SCHEMA REGISTRY
  # ============================================================

  schema-registry:
    image: confluentinc/cp-schema-registry:${KAFKA_VERSION:-7.5.0}
    container_name: schema-registry
    hostname: schema-registry
    networks:
      - kafka-network
    ports:
      - "8081:8081"
    depends_on:
      kafka1:
        condition: service_healthy
      kafka2:
        condition: service_healthy
      kafka3:
        condition: service_healthy
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka1:29092,kafka2:29092,kafka3:29092
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
      SCHEMA_REGISTRY_KAFKASTORE_TOPIC_REPLICATION_FACTOR: 3

  # ============================================================
  # MONITORING STACK
  # ============================================================

  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: prometheus
    hostname: prometheus
    networks:
      - kafka-network
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
      - ./config/prometheus:/etc/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION:-15d}'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:10.1.0
    container_name: grafana
    hostname: grafana
    networks:
      - kafka-network
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./config/grafana/provisioning:/etc/grafana/provisioning
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: "false"
      GF_SERVER_ROOT_URL: http://localhost:3000

  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager
    hostname: alertmanager
    networks:
      - kafka-network
    ports:
      - "9093:9093"
    volumes:
      - ./config/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
```

---

## Part 2: Security Configuration

### 2.1 Certificate Generation Script

Create `scripts/generate-certs.sh`:

```bash
#!/bin/bash
# generate-certs.sh - Generate TLS certificates for Kafka cluster

set -euo pipefail

# Load environment
source ../.env 2>/dev/null || true
PASSWORD="${TLS_PASSWORD:-kafka-tls-secret}"
VALIDITY=365
CA_CN="Kafka-Production-CA"

CERTS_DIR="../certs"
mkdir -p "$CERTS_DIR"/{ca,broker,client}

echo "=== Kafka TLS Certificate Generation ==="
echo "Password: [hidden]"
echo "Validity: $VALIDITY days"
echo ""

# ============================================================
# 1. Generate CA
# ============================================================
echo "[1/4] Generating Certificate Authority..."

cd "$CERTS_DIR/ca"

# Generate CA private key and certificate
openssl req -new -x509 \
    -keyout ca-key.pem \
    -out ca-cert.pem \
    -days $VALIDITY \
    -subj "/CN=$CA_CN/O=Kafka/C=US" \
    -passout pass:$PASSWORD

echo "  CA certificate generated"

# ============================================================
# 2. Generate Broker Certificates
# ============================================================
echo "[2/4] Generating broker certificates..."

cd "$CERTS_DIR/broker"

for broker in kafka1 kafka2 kafka3; do
    echo "  Processing $broker..."

    # Generate keystore with private key
    keytool -genkey -noprompt \
        -alias $broker \
        -keyalg RSA -keysize 2048 \
        -keystore ${broker}.keystore.jks \
        -storepass $PASSWORD \
        -keypass $PASSWORD \
        -dname "CN=$broker,O=Kafka,C=US" \
        -ext "SAN=DNS:$broker,DNS:localhost"

    # Generate CSR
    keytool -certreq -alias $broker \
        -keystore ${broker}.keystore.jks \
        -storepass $PASSWORD \
        -file ${broker}.csr \
        -ext "SAN=DNS:$broker,DNS:localhost"

    # Create extensions file for SAN
    cat > ${broker}.ext << EOF
subjectAltName=DNS:$broker,DNS:localhost
EOF

    # Sign with CA
    openssl x509 -req \
        -CA ../ca/ca-cert.pem \
        -CAkey ../ca/ca-key.pem \
        -in ${broker}.csr \
        -out ${broker}-signed.pem \
        -days $VALIDITY \
        -CAcreateserial \
        -passin pass:$PASSWORD \
        -extfile ${broker}.ext

    # Import CA cert to keystore
    keytool -importcert -alias CARoot \
        -file ../ca/ca-cert.pem \
        -keystore ${broker}.keystore.jks \
        -storepass $PASSWORD \
        -noprompt

    # Import signed cert to keystore
    keytool -importcert -alias $broker \
        -file ${broker}-signed.pem \
        -keystore ${broker}.keystore.jks \
        -storepass $PASSWORD \
        -noprompt

    echo "    $broker keystore created"
done

# Create shared truststore
keytool -importcert -alias CARoot \
    -file ../ca/ca-cert.pem \
    -keystore kafka.truststore.jks \
    -storepass $PASSWORD \
    -noprompt

echo "  Broker truststore created"

# ============================================================
# 3. Generate Client Certificates
# ============================================================
echo "[3/4] Generating client certificates..."

cd "$CERTS_DIR/client"

for client in admin producer consumer; do
    echo "  Processing $client..."

    # Generate keystore
    keytool -genkey -noprompt \
        -alias $client \
        -keyalg RSA -keysize 2048 \
        -keystore ${client}.keystore.jks \
        -storepass $PASSWORD \
        -keypass $PASSWORD \
        -dname "CN=$client,O=KafkaClient,C=US"

    # Generate CSR
    keytool -certreq -alias $client \
        -keystore ${client}.keystore.jks \
        -storepass $PASSWORD \
        -file ${client}.csr

    # Sign with CA
    openssl x509 -req \
        -CA ../ca/ca-cert.pem \
        -CAkey ../ca/ca-key.pem \
        -in ${client}.csr \
        -out ${client}-signed.pem \
        -days $VALIDITY \
        -CAcreateserial \
        -passin pass:$PASSWORD

    # Import to keystore
    keytool -importcert -alias CARoot \
        -file ../ca/ca-cert.pem \
        -keystore ${client}.keystore.jks \
        -storepass $PASSWORD \
        -noprompt

    keytool -importcert -alias $client \
        -file ${client}-signed.pem \
        -keystore ${client}.keystore.jks \
        -storepass $PASSWORD \
        -noprompt

    echo "    $client keystore created"
done

# Create client truststore
keytool -importcert -alias CARoot \
    -file ../ca/ca-cert.pem \
    -keystore client.truststore.jks \
    -storepass $PASSWORD \
    -noprompt

echo "  Client truststore created"

# ============================================================
# 4. Summary
# ============================================================
echo ""
echo "[4/4] Certificate generation complete!"
echo ""
echo "Generated files:"
echo "  CA:      $CERTS_DIR/ca/ca-cert.pem"
echo "  Brokers: $CERTS_DIR/broker/*.keystore.jks"
echo "  Clients: $CERTS_DIR/client/*.keystore.jks"
echo ""
echo "Truststores:"
echo "  Broker:  $CERTS_DIR/broker/kafka.truststore.jks"
echo "  Client:  $CERTS_DIR/client/client.truststore.jks"
```

### 2.2 SCRAM User Creation Script

Create `scripts/create-users.sh`:

```bash
#!/bin/bash
# create-users.sh - Create SCRAM users for Kafka authentication

set -euo pipefail

source ../.env 2>/dev/null || true
BOOTSTRAP="localhost:9092"

echo "=== Creating Kafka SCRAM Users ==="

# Wait for cluster
echo "Waiting for Kafka cluster..."
sleep 10

# Admin user (full access)
echo "Creating admin user..."
docker exec kafka1 kafka-configs \
    --bootstrap-server kafka1:29092 \
    --alter \
    --add-config "SCRAM-SHA-512=[iterations=8192,password=${SCRAM_ADMIN_PASSWORD:-admin-password}]" \
    --entity-type users \
    --entity-name admin

# Application user (producer)
echo "Creating producer user..."
docker exec kafka1 kafka-configs \
    --bootstrap-server kafka1:29092 \
    --alter \
    --add-config "SCRAM-SHA-512=[iterations=8192,password=${SCRAM_APP_PASSWORD:-app-password}]" \
    --entity-type users \
    --entity-name producer-app

# Application user (consumer)
echo "Creating consumer user..."
docker exec kafka1 kafka-configs \
    --bootstrap-server kafka1:29092 \
    --alter \
    --add-config "SCRAM-SHA-512=[iterations=8192,password=${SCRAM_APP_PASSWORD:-app-password}]" \
    --entity-type users \
    --entity-name consumer-app

# Service account (Connect)
echo "Creating connect user..."
docker exec kafka1 kafka-configs \
    --bootstrap-server kafka1:29092 \
    --alter \
    --add-config "SCRAM-SHA-512=[iterations=8192,password=${SCRAM_APP_PASSWORD:-app-password}]" \
    --entity-type users \
    --entity-name kafka-connect

# List users
echo ""
echo "Created users:"
docker exec kafka1 kafka-configs \
    --bootstrap-server kafka1:29092 \
    --describe \
    --entity-type users

echo ""
echo "=== User creation complete ==="
```

### 2.3 ACL Configuration Script

Create `scripts/configure-acls.sh`:

```bash
#!/bin/bash
# configure-acls.sh - Configure Kafka ACLs for authorization

set -euo pipefail

BOOTSTRAP="kafka1:29092"

echo "=== Configuring Kafka ACLs ==="

# ============================================================
# Admin user - Full cluster access
# ============================================================
echo "Configuring admin ACLs..."

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:admin \
    --operation All \
    --cluster

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:admin \
    --operation All \
    --topic '*'

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:admin \
    --operation All \
    --group '*'

# ============================================================
# Producer application - Write to specific topics
# ============================================================
echo "Configuring producer ACLs..."

# Create application topics first
docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP \
    --create --topic orders --partitions 6 --replication-factor 3 --if-not-exists

docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP \
    --create --topic events --partitions 6 --replication-factor 3 --if-not-exists

docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP \
    --create --topic logs --partitions 3 --replication-factor 3 --if-not-exists

# Producer ACLs
docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:producer-app \
    --operation Write \
    --operation Describe \
    --topic orders

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:producer-app \
    --operation Write \
    --operation Describe \
    --topic events

# ============================================================
# Consumer application - Read from specific topics
# ============================================================
echo "Configuring consumer ACLs..."

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:consumer-app \
    --operation Read \
    --operation Describe \
    --topic orders

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:consumer-app \
    --operation Read \
    --operation Describe \
    --topic events

# Consumer group ACLs
docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:consumer-app \
    --operation Read \
    --group 'order-processor-*'

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:consumer-app \
    --operation Read \
    --group 'event-processor-*'

# ============================================================
# Kafka Connect - Read/Write for connectors
# ============================================================
echo "Configuring Connect ACLs..."

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:kafka-connect \
    --operation All \
    --topic 'connect-*'

docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:kafka-connect \
    --operation All \
    --group 'connect-*'

# ============================================================
# List all ACLs
# ============================================================
echo ""
echo "=== Current ACL Configuration ==="
docker exec kafka1 kafka-acls --bootstrap-server $BOOTSTRAP --list

echo ""
echo "=== ACL configuration complete ==="
```

---

## Part 3: Monitoring Configuration

### 3.1 Prometheus Configuration

Create `config/prometheus/prometheus.yml`:

```yaml
# prometheus.yml - Kafka Monitoring Configuration

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Kafka brokers (JMX Exporter)
  - job_name: 'kafka'
    static_configs:
      - targets:
        - 'kafka1:7071'
        - 'kafka2:7071'
        - 'kafka3:7071'
    relabel_configs:
      - source_labels: [__address__]
        regex: '([^:]+):\d+'
        target_label: instance
        replacement: '${1}'

  # Schema Registry
  - job_name: 'schema-registry'
    static_configs:
      - targets: ['schema-registry:8081']
    metrics_path: /metrics
```

### 3.2 Prometheus Alert Rules

Create `config/prometheus/rules/kafka-alerts.yml`:

```yaml
# kafka-alerts.yml - Critical Kafka Alerts

groups:
  - name: kafka-cluster
    rules:
      # Broker availability
      - alert: KafkaBrokerDown
        expr: up{job="kafka"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka broker {{ $labels.instance }} is down"
          description: "Broker has been unreachable for more than 1 minute"

      # Under-replicated partitions
      - alert: KafkaUnderReplicatedPartitions
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Under-replicated partitions on {{ $labels.instance }}"
          description: "{{ $value }} partitions are under-replicated"

      # Offline partitions (critical!)
      - alert: KafkaOfflinePartitions
        expr: kafka_controller_kafkacontroller_offlinepartitionscount > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Offline partitions detected"
          description: "{{ $value }} partitions are offline - data unavailable!"

      # No active controller
      - alert: KafkaNoActiveController
        expr: sum(kafka_controller_kafkacontroller_activecontrollercount) != 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "No active Kafka controller"
          description: "Cluster has {{ $value }} active controllers (should be 1)"

  - name: kafka-performance
    rules:
      # High request latency
      - alert: KafkaHighRequestLatency
        expr: kafka_network_requestmetrics_totaltimems{quantile="0.99"} > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency on {{ $labels.instance }}"
          description: "p99 latency is {{ $value }}ms"

      # Low ISR (In-Sync Replicas)
      - alert: KafkaLowISR
        expr: kafka_server_replicamanager_isrshrinkspersecount > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ISR shrinking on {{ $labels.instance }}"
          description: "In-sync replicas are shrinking"

  - name: kafka-consumer
    rules:
      # Consumer lag alert
      - alert: KafkaConsumerLag
        expr: kafka_consumer_group_lag > 10000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High consumer lag for {{ $labels.group }}"
          description: "Consumer group has {{ $value }} messages lag"

      # Stalled consumer
      - alert: KafkaConsumerStalled
        expr: rate(kafka_consumer_group_offset[5m]) == 0 and kafka_consumer_group_lag > 0
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "Consumer group {{ $labels.group }} is stalled"
          description: "Consumer not making progress with {{ $value }} lag"
```

### 3.3 Alertmanager Configuration

Create `config/alertmanager/alertmanager.yml`:

```yaml
# alertmanager.yml - Alert Routing Configuration

global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'

  routes:
    # Critical alerts - immediate notification
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 10s
      repeat_interval: 1h

    # Warning alerts - less urgent
    - match:
        severity: warning
      receiver: 'warning-alerts'
      group_wait: 5m
      repeat_interval: 4h

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
        send_resolved: true

  - name: 'critical-alerts'
    webhook_configs:
      - url: 'http://localhost:5001/critical'
        send_resolved: true
    # Add email, PagerDuty, Slack, etc.
    # email_configs:
    #   - to: 'oncall@example.com'
    # pagerduty_configs:
    #   - service_key: '<key>'
    # slack_configs:
    #   - api_url: '<webhook_url>'
    #     channel: '#kafka-alerts'

  - name: 'warning-alerts'
    webhook_configs:
      - url: 'http://localhost:5001/warning'
        send_resolved: true

inhibit_rules:
  # If broker is down, suppress other alerts from that broker
  - source_match:
      alertname: 'KafkaBrokerDown'
    target_match_re:
      alertname: 'Kafka.*'
    equal: ['instance']
```

### 3.4 Grafana Dashboard

Create `config/grafana/dashboards/kafka-overview.json`:

```json
{
  "dashboard": {
    "title": "Kafka Cluster Overview",
    "uid": "kafka-overview",
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "title": "Cluster Health",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(up{job=\"kafka\"})",
            "legendFormat": "Brokers Online"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 2},
                {"color": "green", "value": 3}
              ]
            }
          }
        }
      },
      {
        "title": "Under-Replicated Partitions",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
        "targets": [
          {
            "expr": "sum(kafka_server_replicamanager_underreplicatedpartitions)",
            "legendFormat": "Under-replicated"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            }
          }
        }
      },
      {
        "title": "Messages In/Sec",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "sum(rate(kafka_server_brokertopicmetrics_messagesinpersec_count[5m])) by (instance)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Bytes In/Out",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "targets": [
          {
            "expr": "sum(rate(kafka_server_brokertopicmetrics_bytesinpersec_count[5m]))",
            "legendFormat": "Bytes In"
          },
          {
            "expr": "sum(rate(kafka_server_brokertopicmetrics_bytesoutpersec_count[5m]))",
            "legendFormat": "Bytes Out"
          }
        ]
      },
      {
        "title": "Request Latency (p99)",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
        "targets": [
          {
            "expr": "kafka_network_requestmetrics_totaltimems{quantile=\"0.99\",request=\"Produce\"}",
            "legendFormat": "Produce p99"
          },
          {
            "expr": "kafka_network_requestmetrics_totaltimems{quantile=\"0.99\",request=\"FetchConsumer\"}",
            "legendFormat": "Fetch p99"
          }
        ]
      },
      {
        "title": "Consumer Group Lag",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
        "targets": [
          {
            "expr": "sum(kafka_consumer_group_lag) by (group)",
            "legendFormat": "{{group}}"
          }
        ]
      }
    ]
  }
}
```

---

## Part 4: Operational Runbooks

### 4.1 Health Check Script

Create `scripts/health-check.sh`:

```bash
#!/bin/bash
# health-check.sh - Comprehensive Kafka cluster health check

set -euo pipefail

BOOTSTRAP="kafka1:29092"

echo "========================================"
echo "KAFKA CLUSTER HEALTH CHECK"
echo "$(date)"
echo "========================================"

# Check broker connectivity
echo ""
echo "[1] BROKER CONNECTIVITY"
echo "------------------------"
for broker in kafka1 kafka2 kafka3; do
    if docker exec $broker kafka-broker-api-versions --bootstrap-server localhost:29092 > /dev/null 2>&1; then
        echo "  $broker: OK"
    else
        echo "  $broker: FAILED"
    fi
done

# Check controller
echo ""
echo "[2] CONTROLLER STATUS"
echo "---------------------"
docker exec kafka1 kafka-metadata --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log \
    --command "controller" 2>/dev/null || echo "  Check manually"

# Check under-replicated partitions
echo ""
echo "[3] UNDER-REPLICATED PARTITIONS"
echo "-------------------------------"
URPs=$(docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP --describe --under-replicated-partitions 2>/dev/null | wc -l)
if [ "$URPs" -eq 0 ]; then
    echo "  None - OK"
else
    echo "  WARNING: $URPs under-replicated partitions"
    docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP --describe --under-replicated-partitions
fi

# Check offline partitions
echo ""
echo "[4] OFFLINE PARTITIONS"
echo "----------------------"
OPs=$(docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP --describe --unavailable-partitions 2>/dev/null | wc -l)
if [ "$OPs" -eq 0 ]; then
    echo "  None - OK"
else
    echo "  CRITICAL: $OPs offline partitions!"
    docker exec kafka1 kafka-topics --bootstrap-server $BOOTSTRAP --describe --unavailable-partitions
fi

# Check consumer lag
echo ""
echo "[5] CONSUMER GROUP LAG"
echo "----------------------"
docker exec kafka1 kafka-consumer-groups --bootstrap-server $BOOTSTRAP --all-groups --describe 2>/dev/null | \
    grep -v "^$" | head -20

# Disk usage
echo ""
echo "[6] DISK USAGE"
echo "--------------"
for broker in kafka1 kafka2 kafka3; do
    echo "  $broker:"
    docker exec $broker df -h /var/lib/kafka/data | tail -1 | awk '{print "    Used: " $3 " / " $2 " (" $5 ")"}'
done

# Summary
echo ""
echo "========================================"
echo "HEALTH CHECK COMPLETE"
echo "========================================"
if [ "$URPs" -eq 0 ] && [ "$OPs" -eq 0 ]; then
    echo "Status: HEALTHY"
    exit 0
else
    echo "Status: DEGRADED - Review issues above"
    exit 1
fi
```

### 4.2 Upgrade Runbook

Create `runbooks/upgrade.md`:

```markdown
# Kafka Cluster Upgrade Runbook

## Pre-Upgrade Checklist

- [ ] Review release notes for breaking changes
- [ ] Test upgrade in staging environment
- [ ] Backup cluster metadata and configurations
- [ ] Verify no under-replicated or offline partitions
- [ ] Notify stakeholders of maintenance window
- [ ] Ensure monitoring and alerting is active

## Upgrade Procedure

### Phase 1: Preparation

1. **Run health check**
   ```bash
   ./scripts/health-check.sh
   ```

2. **Backup configurations**
   ```bash
   mkdir -p backups/$(date +%Y%m%d)
   cp -r config/ backups/$(date +%Y%m%d)/
   docker exec kafka1 kafka-configs --bootstrap-server kafka1:29092 \
       --describe --all > backups/$(date +%Y%m%d)/cluster-configs.txt
   ```

3. **Record current state**
   ```bash
   docker exec kafka1 kafka-topics --bootstrap-server kafka1:29092 --describe \
       > backups/$(date +%Y%m%d)/topics.txt
   ```

### Phase 2: Rolling Upgrade (Per Broker)

For each broker (kafka1, kafka2, kafka3):

1. **Verify cluster health**
   ```bash
   ./scripts/health-check.sh
   ```
   Proceed only if healthy.

2. **Drain broker** (optional, for zero-downtime)
   ```bash
   # Reassign partitions away from this broker
   # Wait for reassignment to complete
   ```

3. **Stop broker**
   ```bash
   docker stop kafka1
   ```

4. **Update image version**
   Update `.env`:
   ```
   KAFKA_VERSION=7.6.0  # New version
   ```

5. **Start broker**
   ```bash
   docker-compose up -d kafka1
   ```

6. **Wait for ISR recovery**
   ```bash
   watch -n 5 'docker exec kafka2 kafka-topics --bootstrap-server kafka2:29092 \
       --describe --under-replicated-partitions'
   ```
   Wait until no under-replicated partitions.

7. **Verify broker health**
   ```bash
   docker exec kafka1 kafka-broker-api-versions --bootstrap-server localhost:29092
   ```

8. **Repeat for next broker**

### Phase 3: Post-Upgrade

1. **Final health check**
   ```bash
   ./scripts/health-check.sh
   ```

2. **Update protocol version** (if required)
   ```bash
   # Only after all brokers upgraded
   # Update inter.broker.protocol.version
   # Perform another rolling restart
   ```

3. **Verify application connectivity**
   - Test producer connections
   - Test consumer connections
   - Check consumer lag is normal

4. **Remove old backups** (after verification period)

## Rollback Procedure

If issues occur during upgrade:

1. Stop the problematic broker
2. Restore previous version in docker-compose
3. Start broker with old version
4. Verify cluster recovers

## Post-Upgrade Monitoring

Monitor for 24-48 hours:
- Under-replicated partitions
- Consumer lag
- Request latency
- Error rates in application logs
```

---

## Part 5: Deployment and Verification

### 5.1 Deployment Steps

```bash
# 1. Generate certificates
cd scripts
chmod +x *.sh
./generate-certs.sh

# 2. Start the cluster
cd ..
docker-compose up -d

# 3. Wait for brokers to be healthy
sleep 60
docker-compose ps

# 4. Create users
./scripts/create-users.sh

# 5. Configure ACLs
./scripts/configure-acls.sh

# 6. Run health check
./scripts/health-check.sh

# 7. Access Grafana
echo "Grafana: http://localhost:3000 (admin / $GRAFANA_ADMIN_PASSWORD)"
```

### 5.2 Client Connection Test

Create `scripts/test-connection.py`:

```python
#!/usr/bin/env python3
"""Test secure connection to Kafka cluster."""

from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import json
import os

# Load credentials from environment
BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')
USERNAME = os.getenv('KAFKA_USERNAME', 'producer-app')
PASSWORD = os.getenv('KAFKA_PASSWORD', 'app-password')
TRUSTSTORE = os.getenv('KAFKA_TRUSTSTORE', './certs/client/client.truststore.jks')
TRUSTSTORE_PASSWORD = os.getenv('KAFKA_TRUSTSTORE_PASSWORD', 'kafka-tls-secret')

def get_config():
    """Get Kafka client configuration."""
    return {
        'bootstrap.servers': BOOTSTRAP,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'SCRAM-SHA-512',
        'sasl.username': USERNAME,
        'sasl.password': PASSWORD,
        'ssl.ca.location': './certs/ca/ca-cert.pem',
        # For JKS truststore:
        # 'ssl.truststore.location': TRUSTSTORE,
        # 'ssl.truststore.password': TRUSTSTORE_PASSWORD,
    }

def test_producer():
    """Test producer connectivity."""
    print("\n[1] Testing Producer...")

    config = get_config()
    producer = Producer(config)

    delivered = [0]
    errors = [0]

    def callback(err, msg):
        if err:
            errors[0] += 1
            print(f"  Error: {err}")
        else:
            delivered[0] += 1

    # Send test messages
    for i in range(10):
        producer.produce(
            'orders',
            key=f'test-{i}'.encode(),
            value=json.dumps({'test': i}).encode(),
            callback=callback
        )

    producer.flush(timeout=10)
    print(f"  Delivered: {delivered[0]}, Errors: {errors[0]}")
    return errors[0] == 0

def test_consumer():
    """Test consumer connectivity."""
    print("\n[2] Testing Consumer...")

    config = get_config()
    config['group.id'] = 'test-consumer-group'
    config['auto.offset.reset'] = 'earliest'

    consumer = Consumer(config)
    consumer.subscribe(['orders'])

    messages = 0
    try:
        for _ in range(30):  # Poll for up to 30 seconds
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"  Error: {msg.error()}")
            else:
                messages += 1
                if messages >= 5:
                    break
    finally:
        consumer.close()

    print(f"  Received: {messages} messages")
    return messages > 0

def main():
    print("=" * 50)
    print("KAFKA SECURE CONNECTION TEST")
    print("=" * 50)
    print(f"Bootstrap: {BOOTSTRAP}")
    print(f"User: {USERNAME}")

    results = []

    try:
        results.append(('Producer', test_producer()))
    except Exception as e:
        print(f"  Producer failed: {e}")
        results.append(('Producer', False))

    try:
        results.append(('Consumer', test_consumer()))
    except Exception as e:
        print(f"  Consumer failed: {e}")
        results.append(('Consumer', False))

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)
    print(f"\nOverall: {'SUCCESS' if all_passed else 'FAILURE'}")
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
```

---

## Deliverables

Complete the following for project submission:

1. **Infrastructure**
   - [ ] Docker Compose configuration with 3 brokers
   - [ ] Schema Registry deployment
   - [ ] Environment configuration

2. **Security**
   - [ ] TLS certificates (CA, broker, client)
   - [ ] SCRAM user configuration
   - [ ] ACL configuration

3. **Monitoring**
   - [ ] Prometheus configuration and alert rules
   - [ ] Grafana dashboards
   - [ ] Alertmanager configuration

4. **Operations**
   - [ ] Health check script
   - [ ] Upgrade runbook
   - [ ] Connection test script

5. **Documentation**
   - [ ] Architecture diagram
   - [ ] Security configuration docs
   - [ ] Operational procedures

## Evaluation Criteria

| Criteria | Points |
|----------|--------|
| Multi-broker cluster deployment | 15 |
| TLS encryption configured | 15 |
| SASL authentication working | 15 |
| ACLs properly configured | 10 |
| Prometheus metrics collection | 10 |
| Grafana dashboards created | 10 |
| Alert rules configured | 10 |
| Health check script working | 5 |
| Connection tests passing | 5 |
| Documentation complete | 5 |
| **Total** | **100** |

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove certificates
rm -rf certs/

# Remove network
docker network rm kafka-network
```

---

**[← Back to Module 4](./README.md)** | **[Next: Module 5 Capstone →](../module_5_project/project_5_capstone.md)**
