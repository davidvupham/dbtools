# Lesson 15: Kafka security

**[← Back to ksqlDB](./14_ksqldb.md)** | **[Next: Monitoring →](./16_monitoring.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Security-blue)

## Overview

Kafka security involves three pillars: encryption (TLS), authentication (SASL), and authorization (ACLs). This lesson covers how to secure Kafka clusters for production environments.

**Learning objectives:**
- Configure TLS encryption for data in transit
- Implement authentication with SASL mechanisms
- Set up authorization with Access Control Lists (ACLs)
- Apply security best practices for production

**Prerequisites:** Module 3 completed, basic networking knowledge

**Estimated time:** 55 minutes

---

## Table of contents

- [Security overview](#security-overview)
- [Encryption with TLS](#encryption-with-tls)
- [Authentication with SASL](#authentication-with-sasl)
- [Authorization with ACLs](#authorization-with-acls)
- [Security configurations](#security-configurations)
- [Client configuration](#client-configuration)
- [Best practices](#best-practices)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Security overview

### The three pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA SECURITY PILLARS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ENCRYPTION (TLS)                             │   │
│  │                                                                      │   │
│  │  "Can anyone read our data in transit?"                              │   │
│  │                                                                      │   │
│  │  Client ════════════════════════════════════════════════► Broker    │   │
│  │          Encrypted connection (TLS 1.2/1.3)                          │   │
│  │                                                                      │   │
│  │  Protects against: Eavesdropping, man-in-the-middle                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AUTHENTICATION (SASL)                           │   │
│  │                                                                      │   │
│  │  "Who is connecting to our cluster?"                                 │   │
│  │                                                                      │   │
│  │  Client ──── Username/Password ────► Broker                          │   │
│  │         ──── Kerberos ticket   ────►                                 │   │
│  │         ──── OAuth token       ────►                                 │   │
│  │                                                                      │   │
│  │  Protects against: Unauthorized access, impersonation               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AUTHORIZATION (ACLs)                            │   │
│  │                                                                      │   │
│  │  "What can this user do?"                                            │   │
│  │                                                                      │   │
│  │  User: alice                                                         │   │
│  │  ├── Can READ from topic: orders        ✓                           │   │
│  │  ├── Can WRITE to topic: orders         ✗                           │   │
│  │  └── Can CREATE topics                  ✗                           │   │
│  │                                                                      │   │
│  │  Protects against: Privilege escalation, data exfiltration          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security protocols

| Protocol | Encryption | Authentication |
|----------|------------|----------------|
| PLAINTEXT | No | No |
| SSL | Yes (TLS) | Optional (mTLS) |
| SASL_PLAINTEXT | No | Yes (SASL) |
| SASL_SSL | Yes (TLS) | Yes (SASL) |

> **Production recommendation:** Always use `SASL_SSL` for external clients.

---

## Encryption with TLS

### TLS overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TLS HANDSHAKE                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CLIENT                                              BROKER                 │
│  ──────                                              ──────                 │
│                                                                             │
│  1. ClientHello ─────────────────────────────────────►                     │
│     (TLS version, cipher suites)                                            │
│                                                                             │
│                   ◄───────────────────────────── 2. ServerHello            │
│                       (Selected cipher, server certificate)                 │
│                                                                             │
│  3. Verify server certificate                                               │
│     (Check CA signature, hostname)                                          │
│                                                                             │
│  4. Client certificate ──────────────────────────────► (if mTLS)           │
│                                                                             │
│  5. Key exchange ────────────────────────────────────►                     │
│                                                                             │
│                   ◄──────────────────────────────────── 6. Finished        │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════      │
│                      Encrypted communication begins                         │
│  ════════════════════════════════════════════════════════════════════      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Generate certificates

```bash
#!/bin/bash
# generate-certs.sh

# Variables
PASSWORD="kafka-secret"
VALIDITY=365
CA_CN="Kafka-CA"
BROKER_CN="kafka-broker"
CLIENT_CN="kafka-client"

# 1. Create CA (Certificate Authority)
echo "Creating CA..."
openssl req -new -x509 -days $VALIDITY -keyout ca-key.pem -out ca-cert.pem \
    -subj "/CN=$CA_CN" -passout pass:$PASSWORD

# 2. Create broker keystore
echo "Creating broker keystore..."
keytool -genkey -keystore kafka.broker.keystore.jks -alias broker \
    -validity $VALIDITY -keyalg RSA -keysize 2048 \
    -dname "CN=$BROKER_CN" \
    -storepass $PASSWORD -keypass $PASSWORD

# 3. Create CSR for broker
keytool -certreq -keystore kafka.broker.keystore.jks -alias broker \
    -file broker-cert-request.csr -storepass $PASSWORD

# 4. Sign broker certificate with CA
openssl x509 -req -CA ca-cert.pem -CAkey ca-key.pem \
    -in broker-cert-request.csr -out broker-cert-signed.pem \
    -days $VALIDITY -CAcreateserial -passin pass:$PASSWORD

# 5. Import CA and signed cert into broker keystore
keytool -import -keystore kafka.broker.keystore.jks -alias CARoot \
    -file ca-cert.pem -storepass $PASSWORD -noprompt
keytool -import -keystore kafka.broker.keystore.jks -alias broker \
    -file broker-cert-signed.pem -storepass $PASSWORD -noprompt

# 6. Create broker truststore (contains CA cert)
keytool -import -keystore kafka.broker.truststore.jks -alias CARoot \
    -file ca-cert.pem -storepass $PASSWORD -noprompt

# 7. Create client truststore
keytool -import -keystore kafka.client.truststore.jks -alias CARoot \
    -file ca-cert.pem -storepass $PASSWORD -noprompt

echo "Certificates created successfully!"
```

### Broker TLS configuration

```properties
# server.properties

# Listeners with SSL
listeners=PLAINTEXT://0.0.0.0:9092,SSL://0.0.0.0:9093
advertised.listeners=PLAINTEXT://kafka:9092,SSL://kafka:9093

# SSL configuration
ssl.keystore.location=/etc/kafka/secrets/kafka.broker.keystore.jks
ssl.keystore.password=kafka-secret
ssl.key.password=kafka-secret
ssl.truststore.location=/etc/kafka/secrets/kafka.broker.truststore.jks
ssl.truststore.password=kafka-secret

# Require client authentication (mTLS)
ssl.client.auth=required  # Options: none, requested, required

# TLS protocol version
ssl.enabled.protocols=TLSv1.2,TLSv1.3
ssl.protocol=TLSv1.3

# Cipher suites (optional, for compliance)
ssl.cipher.suites=TLS_AES_256_GCM_SHA384,TLS_AES_128_GCM_SHA256

# Inter-broker communication
security.inter.broker.protocol=SSL
```

---

## Authentication with SASL

### SASL mechanisms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SASL MECHANISMS                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MECHANISM              DESCRIPTION                  USE CASE               │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  PLAIN                  Username/password            Development, simple    │
│                         (cleartext)                  setups with TLS        │
│                                                                             │
│  SCRAM-SHA-256/512      Username/password            Production without     │
│                         (salted hash)                Kerberos               │
│                                                                             │
│  GSSAPI (Kerberos)      Kerberos tickets             Enterprise with        │
│                                                      Active Directory       │
│                                                                             │
│  OAUTHBEARER            OAuth 2.0 tokens             Cloud, modern apps     │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  RECOMMENDATION:                                                            │
│  • Development: PLAIN with TLS                                              │
│  • Production (no Kerberos): SCRAM-SHA-512                                  │
│  • Enterprise: GSSAPI                                                       │
│  • Cloud/Modern: OAUTHBEARER                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SASL/SCRAM configuration

```bash
# Create SCRAM credentials
kafka-configs --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[password=alice-secret]' \
    --entity-type users --entity-name alice

kafka-configs --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[password=bob-secret]' \
    --entity-type users --entity-name bob

# List users
kafka-configs --bootstrap-server localhost:9092 \
    --describe --entity-type users
```

### Broker SASL configuration

```properties
# server.properties

# Listeners
listeners=SASL_SSL://0.0.0.0:9094
advertised.listeners=SASL_SSL://kafka:9094

# SASL configuration
sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
security.inter.broker.protocol=SASL_SSL

# SSL configuration (same as before)
ssl.keystore.location=/etc/kafka/secrets/kafka.broker.keystore.jks
ssl.keystore.password=kafka-secret
ssl.key.password=kafka-secret
ssl.truststore.location=/etc/kafka/secrets/kafka.broker.truststore.jks
ssl.truststore.password=kafka-secret
```

### JAAS configuration

```properties
# kafka_server_jaas.conf

KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="admin"
    password="admin-secret";
};

# For inter-broker communication
Client {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="admin"
    password="admin-secret";
};
```

Set the JAAS config:
```bash
export KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/kafka_server_jaas.conf"
```

---

## Authorization with ACLs

### ACL components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ACL STRUCTURE                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  An ACL defines:                                                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PRINCIPAL          WHO is this rule for?                            │   │
│  │                     User:alice, Group:developers                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  RESOURCE           WHAT resource does this apply to?                │   │
│  │                     Topic, Group, Cluster, TransactionalId           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  OPERATION          WHAT action is being controlled?                 │   │
│  │                     Read, Write, Create, Delete, Describe, etc.      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  PERMISSION TYPE    Allow or Deny?                                   │   │
│  │                     ALLOW / DENY                                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  HOST               FROM where? (IP-based)                           │   │
│  │                     *, 192.168.1.0/24                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Example:                                                                   │
│  "User alice can READ from topic orders from any host"                      │
│                                                                             │
│  Principal: User:alice                                                      │
│  Resource: Topic:orders                                                     │
│  Operation: READ                                                            │
│  Permission: ALLOW                                                          │
│  Host: *                                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Resource types and operations

| Resource | Operations |
|----------|------------|
| **Topic** | Read, Write, Create, Delete, Describe, DescribeConfigs, AlterConfigs |
| **Group** | Read, Describe, Delete |
| **Cluster** | Create, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite |
| **TransactionalId** | Describe, Write |
| **DelegationToken** | Describe |

### Managing ACLs

```bash
# Enable ACL authorizer in server.properties
# authorizer.class.name=kafka.security.authorizer.AclAuthorizer
# super.users=User:admin

# Create ACL - Allow alice to read from orders topic
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --add \
    --allow-principal User:alice \
    --operation Read \
    --topic orders

# Allow alice to use consumer group
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --add \
    --allow-principal User:alice \
    --operation Read \
    --group order-consumers

# Allow bob to write to orders topic
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --add \
    --allow-principal User:bob \
    --operation Write \
    --topic orders

# Allow service account to use transactions
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --add \
    --allow-principal User:order-service \
    --operation Write --operation Describe \
    --transactional-id order-*

# List all ACLs
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --list

# List ACLs for a topic
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --list --topic orders

# Remove an ACL
kafka-acls --bootstrap-server localhost:9094 \
    --command-config admin.properties \
    --remove \
    --allow-principal User:alice \
    --operation Read \
    --topic orders
```

### Common ACL patterns

```bash
# Pattern 1: Read-only consumer
kafka-acls --add \
    --allow-principal User:consumer-app \
    --operation Read --operation Describe \
    --topic orders \
    --group consumer-app-group

# Pattern 2: Producer only
kafka-acls --add \
    --allow-principal User:producer-app \
    --operation Write --operation Describe \
    --topic orders

# Pattern 3: Idempotent producer
kafka-acls --add \
    --allow-principal User:producer-app \
    --operation Write --operation IdempotentWrite --operation Describe \
    --topic orders
kafka-acls --add \
    --allow-principal User:producer-app \
    --operation IdempotentWrite \
    --cluster

# Pattern 4: Kafka Streams application
kafka-acls --add \
    --allow-principal User:streams-app \
    --operation Read \
    --topic input-topic
kafka-acls --add \
    --allow-principal User:streams-app \
    --operation Write \
    --topic output-topic
kafka-acls --add \
    --allow-principal User:streams-app \
    --operation All \
    --topic streams-app-  --resource-pattern-type prefixed
kafka-acls --add \
    --allow-principal User:streams-app \
    --operation All \
    --group streams-app- --resource-pattern-type prefixed

# Pattern 5: Kafka Connect
kafka-acls --add \
    --allow-principal User:connect \
    --operation Read --operation Write --operation Create \
    --topic connect- --resource-pattern-type prefixed
kafka-acls --add \
    --allow-principal User:connect \
    --operation Read \
    --group connect-cluster
```

---

## Security configurations

### Complete secure broker configuration

```properties
# server.properties - Secure configuration

############################# Server Basics #############################
broker.id=0
log.dirs=/var/kafka-logs

############################# Listeners #############################
# Internal: SASL_PLAINTEXT (inside VPC)
# External: SASL_SSL (from outside)
listeners=INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093
advertised.listeners=INTERNAL://kafka-internal:9092,EXTERNAL://kafka.example.com:9093
listener.security.protocol.map=INTERNAL:SASL_PLAINTEXT,EXTERNAL:SASL_SSL
inter.broker.listener.name=INTERNAL

############################# SSL Configuration #############################
ssl.keystore.location=/etc/kafka/secrets/kafka.broker.keystore.jks
ssl.keystore.password=${KEYSTORE_PASSWORD}
ssl.key.password=${KEY_PASSWORD}
ssl.truststore.location=/etc/kafka/secrets/kafka.broker.truststore.jks
ssl.truststore.password=${TRUSTSTORE_PASSWORD}
ssl.client.auth=required
ssl.enabled.protocols=TLSv1.2,TLSv1.3

############################# SASL Configuration #############################
sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512

############################# Authorization #############################
authorizer.class.name=kafka.security.authorizer.AclAuthorizer
super.users=User:admin
allow.everyone.if.no.acl.found=false

############################# Logging #############################
# Log authorization decisions for debugging
log4j.logger.kafka.authorizer.logger=DEBUG
```

---

## Client configuration

### Python producer with SASL_SSL

```python
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'kafka.example.com:9093',

    # Security protocol
    'security.protocol': 'SASL_SSL',

    # SASL configuration
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': 'producer-app',
    'sasl.password': 'producer-secret',

    # SSL configuration
    'ssl.ca.location': '/etc/kafka/certs/ca-cert.pem',
    # For mTLS (client certificate)
    'ssl.certificate.location': '/etc/kafka/certs/client-cert.pem',
    'ssl.key.location': '/etc/kafka/certs/client-key.pem',
    'ssl.key.password': 'key-password',

    # Producer settings
    'acks': 'all',
    'enable.idempotence': True
}

producer = Producer(config)

producer.produce('orders', key='order-1', value='{"amount": 100}')
producer.flush()
```

### Python consumer with SASL_SSL

```python
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'kafka.example.com:9093',
    'group.id': 'order-consumers',

    # Security protocol
    'security.protocol': 'SASL_SSL',

    # SASL configuration
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': 'consumer-app',
    'sasl.password': 'consumer-secret',

    # SSL configuration
    'ssl.ca.location': '/etc/kafka/certs/ca-cert.pem',

    # Consumer settings
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(config)
consumer.subscribe(['orders'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue
        print(f"Received: {msg.value()}")
finally:
    consumer.close()
```

### Java client configuration

```java
Properties props = new Properties();
props.put("bootstrap.servers", "kafka.example.com:9093");
props.put("security.protocol", "SASL_SSL");
props.put("sasl.mechanism", "SCRAM-SHA-512");
props.put("sasl.jaas.config",
    "org.apache.kafka.common.security.scram.ScramLoginModule required " +
    "username=\"producer-app\" password=\"producer-secret\";");
props.put("ssl.truststore.location", "/etc/kafka/certs/client.truststore.jks");
props.put("ssl.truststore.password", "truststore-password");
```

---

## Best practices

### Security checklist

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY BEST PRACTICES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ENCRYPTION                                                                 │
│  ──────────                                                                 │
│  ☐ Use TLS 1.2 or 1.3 (disable older versions)                             │
│  ☐ Use strong cipher suites                                                 │
│  ☐ Rotate certificates before expiry                                        │
│  ☐ Use separate certificates per broker                                     │
│  ☐ Enable encryption for inter-broker communication                        │
│  ☐ Consider mTLS for zero-trust environments                               │
│                                                                             │
│  AUTHENTICATION                                                             │
│  ──────────────                                                             │
│  ☐ Use SCRAM-SHA-512 or Kerberos (not PLAIN without TLS)                   │
│  ☐ Create separate credentials per application                             │
│  ☐ Store credentials securely (vault, secrets manager)                     │
│  ☐ Rotate credentials regularly                                            │
│  ☐ Use service accounts, not personal accounts                             │
│                                                                             │
│  AUTHORIZATION                                                              │
│  ─────────────                                                              │
│  ☐ Enable ACLs (don't allow anonymous access)                              │
│  ☐ Apply principle of least privilege                                       │
│  ☐ Use prefixed ACLs for applications needing multiple topics              │
│  ☐ Audit ACL changes                                                        │
│  ☐ Limit super users                                                        │
│                                                                             │
│  NETWORK                                                                    │
│  ───────                                                                    │
│  ☐ Use private networks for inter-broker communication                     │
│  ☐ Firewall Kafka ports (9092, 9093, 9094)                                 │
│  ☐ Use separate listeners for internal/external traffic                    │
│  ☐ Consider network segmentation                                           │
│                                                                             │
│  OPERATIONS                                                                 │
│  ──────────                                                                 │
│  ☐ Log authentication failures                                             │
│  ☐ Monitor for unusual access patterns                                     │
│  ☐ Regularly review and audit permissions                                  │
│  ☐ Test disaster recovery with security enabled                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hands-on exercises

### Exercise 1: Enable TLS

1. Generate certificates using the provided script
2. Configure broker with SSL listener
3. Test connection with SSL-enabled consumer

### Exercise 2: Add SASL authentication

1. Create SCRAM credentials for two users
2. Configure broker with SASL_SSL
3. Update client configurations

### Exercise 3: Implement ACLs

1. Create read-only user for topic "orders"
2. Create write-only user for topic "orders"
3. Test that permissions are enforced

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY KEY TAKEAWAYS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Use SASL_SSL for production - combines encryption and authentication    │
│                                                                             │
│  ✓ TLS 1.2/1.3 encrypts data in transit - prevent eavesdropping            │
│                                                                             │
│  ✓ SCRAM-SHA-512 is recommended for password-based authentication          │
│                                                                             │
│  ✓ ACLs enforce principle of least privilege - only grant needed access    │
│                                                                             │
│  ✓ Use separate credentials per application, not shared accounts           │
│                                                                             │
│  ✓ Different listeners for internal vs external traffic                    │
│                                                                             │
│  ✓ Store credentials in secrets managers, not config files                 │
│                                                                             │
│  ✓ Regularly audit and rotate credentials and certificates                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to ksqlDB](./14_ksqldb.md)** | **[Next: Monitoring →](./16_monitoring.md)**

[↑ Back to Top](#lesson-15-kafka-security)
