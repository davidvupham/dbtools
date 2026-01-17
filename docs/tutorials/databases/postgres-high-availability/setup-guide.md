# Tutorial: High Availability PostgreSQL with Docker

This tutorial guides you through setting up a High Availability (HA) PostgreSQL environment using Docker Compose. We will use **PostgreSQL**, **PgBouncer**, **HAProxy**, and **Keepalived**.

## Prerequisites
-   Docker Desktop or Docker Engine installed.
-   `docker-compose` (or `docker compose` plugin).
-   Basic understanding of SQL and shell commands.

## Architecture
We will spin up the following containers:
1.  **`pg-primary`**: The primary Read/Write database.
2.  **`pg-replica`**: A streaming replica (Read-Only).
3.  **`pgbouncer`**: Connection pooling middleware.
4.  **`haproxy`**: Load balancer managing traffic between database nodes.
5.  **`keepalived`**: Manages the Virtual IP (VIP). *Note: Keepalived in Docker requires privileged network capabilities.*

---

## 1. Project Structure

Create a directory for your project and the following structure:

```text
postgres-ha/
├── docker-compose.yml
├── haproxy/
│   └── haproxy.cfg
├── pgbouncer/
│   ├── pgbouncer.ini
│   └── userlist.txt
├── keepalived/
│   ├── keepalived.conf
│   └── master.sh (script to verify functionality)
└── scripts/
    └── update_replication.sh (dummy script for setup)
```

## 2. Docker Compose Configuration

Create `docker-compose.yml`. Notice the `healthcheck` blocks which are critical for auto-healing and dependency management.

```yaml
version: '3.8'

services:
  # --- Database Layer ---
  pg-primary:
    image: postgres:15
    hostname: pg-primary
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: appdb
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - pg_primary_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ha-net

  pg-replica:
    image: postgres:15
    hostname: pg-replica
    depends_on:
      pg-primary:
        condition: service_healthy
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_HOST_AUTH_METHOD: trust
    command: |
      bash -c "
      until pg_isready -h pg-primary -U admin; do sleep 1; done;
      rm -rf /var/lib/postgresql/data/*
      pg_basebackup -h pg-primary -D /var/lib/postgresql/data -U admin -v -P --wal-method=stream
      touch /var/lib/postgresql/data/standby.signal
      echo \"primary_conninfo = 'host=pg-primary port=5432 user=admin password=password123'\" >> /var/lib/postgresql/data/postgresql.conf
      docker-entrypoint.sh postgres
      "
    volumes:
      - pg_replica_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -h localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ha-net

  # --- Pooling Layer ---
  pgbouncer:
    image: edoburu/pgbouncer:latest
    depends_on:
      pg-primary:
        condition: service_healthy
    environment:
      DB_USER: admin
      DB_PASSWORD: password123
      DB_HOST: pg-primary
      DB_NAME: appdb
      POOLS: "appdb=host=pg-primary dbname=appdb pool_mode=transaction"
      LISTEN_PORT: "6432"
    ports:
      - "6432:6432"
    volumes:
      - ./pgbouncer/pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini
      - ./pgbouncer/userlist.txt:/etc/pgbouncer/userlist.txt
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "6432"]
      interval: 5s
      timeout: 3s
      retries: 3
    networks:
      - ha-net

  # --- Load Balancing Layer ---
  haproxy:
    image: haproxy:2.4
    depends_on:
      pgbouncer:
        condition: service_started
    ports:
      - "5000:5000" # Database traffic
      - "7000:7000" # Stats UI
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    healthcheck:
        test: ["CMD-SHELL", "service haproxy status || exit 1"]
        interval: 10s
        timeout: 5s
        retries: 3
    networks:
      - ha-net

  # --- VIP Layer ---
  keepalived:
    image: osixia/keepalived:latest
    cap_add:
      - NET_ADMIN
      - NET_BROADCAST
      - NET_RAW
    volumes:
        - ./keepalived/keepalived.conf:/container/service/keepalived/assets/keepalived.conf
    network_mode: host # Simplifies VIP visibility for tutorial
    # In a real Docker network setup, you'd use macvlan or specific subnet routing.
    healthcheck:
      test: ["CMD", "pidof", "keepalived"]
      interval: 5s
      retries: 3

volumes:
  pg_primary_data:
  pg_replica_data:

networks:
  ha-net:
```

## 3. Configuration Files

### HAProxy (`haproxy/haproxy.cfg`)
Configures HAProxy to check Postgres status. In this simplified tutorial, we check port accessibility. In production, use `pgsql-check`.

```haproxy
global
    log stdout format raw local0

defaults
    log     global
    mode    tcp
    option  tcplog
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

listen stats
    bind *:7000
    mode http
    stats enable
    stats uri /

listen postgres_write
    bind *:5000
    mode tcp
    option pgsql-check user admin
    default-server inter 3s fall 3 rise 2
    server pg_primary pg-primary:5432 check
    server pg_replica pg-replica:5432 check backup
```

### PgBouncer (`pgbouncer/pgbouncer.ini`)

```ini
[databases]
appdb = host=pg-primary port=5432 dbname=appdb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = trust
auth_file = /etc/pgbouncer/userlist.txt
admin_users = admin
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

### Keepalived (`keepalived/keepalived.conf`)
Replace `INTERFACE_NAME` with your actual network interface (e.g., `eth0`, `wlan0`).

```conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.1.100
    }
}
```

## 4. Running the Setup

1.  Start the stack:
    ```bash
    docker-compose up -d
    ```

2.  Check service health:
    ```bash
    docker-compose ps
    ```
    Wait until `pg-primary` and `pg-replica` are `healthy`.

3.  Verify Replication:
    Connect to the primary and check replication slots:
    ```bash
    docker-compose exec pg-primary psql -U admin -c "select * from pg_stat_replication;"
    ```

## 5. Connecting and Testing

### Connect via HAProxy
Connect to port `5000`. HAProxy routes this to `pg-primary`.

```bash
psql -h localhost -p 5000 -U admin -d appdb
```

### Simulate Failover
1.  Stop the primary database:
    ```bash
    docker-compose stop pg-primary
    ```
2.  Check HAProxy stats at `http://localhost:7000`. You should see `pg_primary` go DOWN and `pg_replica` (configured as backup) might take over if configured with a promotion script (omitted here for brevity, typically handled by Patroni).
3.  In this static configuration, HAProxy will mark primary as DOWN.

## Conclusion
You now have a containerized stack with:
-   **HAProxy** load balancing and checking health.
-   **PgBouncer** pooling connections.
-   **Postgres** replicating data.
-   **Keepalived** ready to manage a VIP.
