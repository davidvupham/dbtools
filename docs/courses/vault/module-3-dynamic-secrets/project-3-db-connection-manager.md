# Project 3: Database Connection Manager

**[← Back to Module 3](./README.md)**

## Overview

Build a service that provides applications with dynamic database credentials using Vault's database secrets engine.

## Requirements

1. **Vault Configuration**
   - Configure database secrets engine for PostgreSQL
   - Create roles for different access levels (readonly, readwrite, admin)

2. **Connection Manager Service**
   - Python service that wraps Vault credential generation
   - Automatic credential renewal
   - Connection pooling with credential rotation

3. **Access Control**
   - Different policies for different application types
   - Audit logging of credential requests

## Deliverables

1. Vault configuration scripts
2. Python connection manager library
3. Example application using the library
4. Documentation

## Evaluation

| Criterion | Points |
|-----------|--------|
| Vault configuration | 30 |
| Connection manager | 40 |
| Access control | 20 |
| Documentation | 10 |

---

[← Back to Module 3](./README.md) | [Take Quiz →](./quiz-module-3.md)
