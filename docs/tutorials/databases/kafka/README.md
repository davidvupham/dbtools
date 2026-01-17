# Kafka Tutorials

This directory contains comprehensive tutorials and guides for working with Apache Kafka.

## 📚 Available Tutorials

### 1. [Kafka Developer's Guide](KAFKA_DEVELOPER_GUIDE.md)

**Best for: Beginners and developers new to Kafka**

A practical, hands-on guide designed for developers with little to no Kafka experience. This tutorial takes you from zero to building production-ready applications.

**What's Included:**

- Simple explanations with real-world analogies
- Complete setup instructions with Docker
- Your first Kafka application (step-by-step)
- **Real-world project**: Server metrics pipeline
  - Collect Linux server metrics (CPU, memory, disk, network)
  - Stream data through Kafka
  - Bulk insert into SQL Server database
- Python code examples throughout
- Best practices for production deployments
- Common pitfalls and how to avoid them
- Testing strategies
- Deployment guide

**Recommended Path:** Start here if you're new to Kafka or want practical, working examples.

### 2. [Kafka Comprehensive Tutorial](KAFKA_COMPREHENSIVE_TUTORIAL.md)

**Best for: Developers seeking in-depth knowledge and reference material**

An extensive reference guide covering Kafka concepts, architecture, best practices, and operational management in detail.

**What's Included:**

- Core Kafka concepts explained in depth
- 8+ detailed use cases with examples
- Best practices for topics and partitions
- Producer and consumer optimization
- Performance tuning (broker, producer, consumer, OS-level)
- Comprehensive monitoring and observability guide
- Troubleshooting common issues (6+ scenarios with solutions)
- Security best practices (SSL/TLS, SASL, ACLs)
- Operational management (scaling, backup, recovery)
- Advanced topics (transactions, log compaction, KRaft mode, Schema Registry)

**Recommended Path:** Use this as a reference guide or after completing the Developer's Guide.

## 🚀 Getting Started

### Prerequisites

Before starting the tutorials, ensure you have:

1. **Docker and Docker Compose** installed
2. **Python 3.7+** installed
3. **Basic command-line knowledge**
4. **Text editor or IDE** (VS Code, PyCharm, etc.)

### Quick Start

1. **Set up Kafka with Docker:**

   ```bash
   # Navigate to the Kafka Docker directory
   cd /workspaces/dbtools/docker/kafka

   # Start Kafka and Zookeeper
   docker-compose up -d

   # Verify services are running
   docker-compose ps
   ```

2. **Install Python dependencies:**

   ```bash
   # Install Kafka Python client
   pip install kafka-python

   # For the metrics project example
   pip install psutil pyodbc
   ```

3. **Follow the tutorials:**
   - **New to Kafka?** Start with [Kafka Developer's Guide](KAFKA_DEVELOPER_GUIDE.md)
   - **Need reference material?** Use [Kafka Comprehensive Tutorial](KAFKA_COMPREHENSIVE_TUTORIAL.md)

## 📖 Tutorial Structure

### Developer's Guide Structure

1. What is Kafka? (Simple explanations)
2. Why use Kafka?
3. Core concepts explained simply
4. Setting up your development environment
5. Your first Kafka application
6. **Real-world project: Server metrics pipeline**
7. Best practices for developers
8. Common pitfalls and solutions
9. Testing Kafka applications
10. Deployment and production readiness

### Comprehensive Tutorial Structure

1. Introduction to Apache Kafka
2. Core Kafka concepts
3. Kafka use cases
4. Best practices for topics and partitions
5. Producer best practices
6. Consumer best practices
7. Performance tuning
8. Monitoring and observability
9. Troubleshooting common issues
10. Security best practices
11. Operational management
12. Advanced topics

## 🎯 Learning Paths

### Path 1: Beginner to Practitioner

1. Read **sections 1-4** of Developer's Guide (concepts and setup)
2. Work through **section 5** (first application)
3. Build the **section 6** project (metrics pipeline)
4. Review **section 7** (best practices)
5. Reference Comprehensive Tutorial as needed

**Time Estimate:** 4-6 hours

### Path 2: Quick Reference

Use the Comprehensive Tutorial as a reference guide when you need:

- Specific best practices (partitioning, replication, etc.)
- Configuration examples
- Troubleshooting help
- Performance tuning tips
- Security configuration

### Path 3: Deep Dive

1. Complete the Developer's Guide end-to-end
2. Build and run the metrics pipeline project
3. Read the Comprehensive Tutorial sections on:
   - Performance tuning
   - Monitoring and observability
   - Security
   - Operational management
4. Implement advanced features in your project

**Time Estimate:** 8-12 hours

## 💡 Practical Examples

Both tutorials include working code examples that you can run immediately:

### Simple Producer/Consumer

```python
# Simple producer
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('my-topic', {'message': 'Hello Kafka!'})
producer.close()
```

```python
# Simple consumer
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```

### Real-World Pipeline

The Developer's Guide includes a complete working example:

- **Producer**: Collects server metrics using `psutil`
- **Kafka**: Streams metrics in real-time
- **Consumer**: Bulk inserts into SQL Server

All code is production-ready with error handling, logging, and graceful shutdown.

## 🔧 Troubleshooting

### Common Issues

**1. Can't connect to Kafka:**

```bash
# Check if Kafka is running
docker-compose ps

# Check Kafka logs
docker-compose logs kafka

# Verify port is accessible
telnet localhost 9092
```

**2. Import errors:**

```bash
# Install required packages
pip install kafka-python psutil pyodbc
```

**3. Permission denied:**

```bash
# Check Docker permissions
sudo usermod -aG docker $USER
# Log out and back in
```

## 📚 Additional Resources

### Related Documentation in This Repository

- [Kafka Docker Setup Guide](../../../docker/kafka/kafka-docker-setup.md) - Detailed Docker setup instructions
- [Docker Compose Configuration](../../../docker/kafka/docker-compose.yml) - Kafka and Zookeeper configuration
- [Dockerfile](../../../docker/kafka/Dockerfile) - Custom Kafka image

### External Resources

- **Apache Kafka Official Documentation**: <https://kafka.apache.org/documentation/>
- **kafka-python Documentation**: <https://kafka-python.readthedocs.io/>
- **Confluent Developer Hub**: <https://developer.confluent.io/>
- **Kafka Improvement Proposals (KIPs)**: <https://cwiki.apache.org/confluence/x/Ri3VAQ>

### Video Tutorials

- Apache Kafka in 5 Minutes: <https://www.youtube.com/watch?v=PzPXRmVHMxI>
- Kafka Tutorial for Beginners: <https://www.youtube.com/watch?v=R873BlNVUB4>
- Kafka Connect Tutorial: <https://www.youtube.com/watch?v=4u8w5vX8xJI>

### Books

- "Kafka: The Definitive Guide" by Neha Narkhede, Gwen Shapira, Todd Palino
- "Kafka Streams in Action" by William P. Bejeck Jr.
- "Designing Event-Driven Systems" by Ben Stopford

## 🤝 Contributing

Found an error or want to improve the tutorials? Contributions are welcome!

1. Review the existing tutorials
2. Create a new branch for your changes
3. Make your updates with clear commit messages
4. Test all code examples
5. Submit a pull request

## 📝 License

These tutorials are part of the dbtools repository. See the repository root for license information.

## 📧 Questions?

If you have questions about these tutorials:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Additional Resources](#additional-resources)
3. Refer to the official Apache Kafka documentation
4. Check the repository issues for similar questions

---

**Last Updated:** November 2025

**Tutorial Authors:** dbtools contributors

**Kafka Version Covered:** Apache Kafka 3.6+ (Confluent Platform 7.6.0)
