# Module 4: Production

**[← Back to Course Index](../README.md)**

*Focus: Building reliable, scalable, and secure RabbitMQ deployments for production.*

## Lessons

| # | Lesson | Topics |
|:---|:---|:---|
| 1 | [Reliability](./01_reliability.md) | Acknowledgments, persistence, publisher confirms |
| 2 | [Dead Letter Exchanges](./02_dead_letter_exchanges.md) | DLX setup, retry patterns, error handling |
| 3 | [Clustering](./03_clustering.md) | Cluster setup, quorum queues, high availability |
| 4 | [Monitoring](./04_monitoring.md) | Management UI, Prometheus, alerting |
| 5 | [Security](./05_security.md) | Authentication, authorization, TLS |

## Exercises

Practice what you've learned:

- **[Exercise 1: Reliability Patterns](./exercises/ex_01_reliability.md)** - Implement publisher confirms and consumer acknowledgments
- **[Exercise 2: Error Handling](./exercises/ex_02_error_handling.md)** - Set up dead letter queues with retry logic
- **[Exercise 3: Monitoring Setup](./exercises/ex_03_monitoring.md)** - Configure monitoring and alerts

## Assessment

- **[Quiz: Module 4](./quiz_module_4.md)** - Test your understanding (15 questions)

## Project

- **[Project 4: Resilient System](./project_4_resilient_system.md)** - Build a fault-tolerant message processing system

## Learning objectives

By completing this module, you will be able to:

1. **Implement reliable messaging** with acknowledgments and persistence
2. **Handle message failures** using dead letter exchanges and retry patterns
3. **Configure clustering** for high availability
4. **Monitor RabbitMQ** using built-in tools and Prometheus
5. **Secure deployments** with authentication, authorization, and TLS

## Prerequisites

- Completed Module 3: Messaging Patterns
- Familiarity with Docker/Docker Compose
- Basic understanding of networking and security concepts

## Production readiness checklist

```
[ ] Reliability
    [ ] Durable queues for important data
    [ ] Persistent messages (delivery_mode=2)
    [ ] Manual acknowledgments (auto_ack=False)
    [ ] Publisher confirms enabled
    [ ] Prefetch count set appropriately

[ ] Error Handling
    [ ] Dead letter exchanges configured
    [ ] Retry logic with exponential backoff
    [ ] Maximum retry limits
    [ ] Failed message alerting

[ ] High Availability
    [ ] Cluster with odd number of nodes (3+)
    [ ] Quorum queues for critical data
    [ ] Partition handling strategy (pause_minority)
    [ ] Load balancer in front of cluster

[ ] Monitoring
    [ ] Management UI accessible
    [ ] Prometheus metrics exported
    [ ] Alerting on queue depth, memory, disk
    [ ] Log aggregation configured

[ ] Security
    [ ] Default credentials changed
    [ ] TLS enabled for all connections
    [ ] Virtual hosts for isolation
    [ ] Least-privilege permissions
    [ ] Management UI access restricted
```

---

[← Back to Course Index](../README.md) | [Start Module 4 →](./01_reliability.md)
