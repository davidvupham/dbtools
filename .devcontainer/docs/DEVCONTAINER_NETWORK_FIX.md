# Dev Container Network Fix - Summary

## Problem

The dev container was hanging during startup with the message:

```
Container started
Not setting dockerd DNS manually.
```

This occurred because the `docker-in-docker` feature was trying to start a Docker daemon inside the container, which was not completing successfully in the WSL2 environment.

## Solution Applied

### 1. Changed from Docker-in-Docker to Docker-Outside-of-Docker

**Modified files:**

- `.devcontainer/ubuntu/devcontainer.json`
- `.devcontainer/redhat/devcontainer.json`

**Change:**

- Removed `docker-in-docker` feature.
- Adopted Docker-outside-of-Docker (DooD) by mounting the host socket at `/var/run/docker.sock`.
- Added the `ghcr.io/devcontainers/features/docker-outside-of-docker:1` feature to install the Docker CLI and align permissions for the mounted socket.

**Why this fixes the hang:**

- No longer starts a Docker daemon inside the container
- Uses the host's Docker daemon via the mounted socket
- Starts immediately without waiting for daemon initialization
- More reliable and performant in WSL2 environments

### 2. Connected Dev Container to `tool-library-network`

**Problem:** With docker-outside-of-docker, the dev container and database containers all run on the same Docker daemon. They need to be on the same network to communicate by container name.

**Solution:**
Added to `runArgs` in both devcontainer.json files:

```json
"--network",
"tool-library-network"
```

**Added `initializeCommand`:**

```json
"initializeCommand": "docker network inspect tool-library-network >/dev/null 2>&1 || docker network create --driver bridge tool-library-network"
```

This creates the network on the host before the dev container starts.

### 3. Updated All Docker Compose Files to Use External Network

**Modified files:**

- `docker/mongodb/docker-compose.yml`
- `docker/mssql/docker-compose.yml`
- `docker/postgresql/docker-compose.yml`
- `docker/kafka/docker-compose.yml`
- `docker/rabbitmq/docker-compose.yml`
- `docker/liquibase/docker-compose.yml`
- `docker/docker-compose.yml` (vault)

**Change:**
Changed network definition from:

```yaml
networks:
  tool-library-network:
    driver: bridge
```

To:

```yaml
networks:
  tool-library-network:
    external: true
```

**Why this is important:**

- Prevents each compose file from creating its own network
- All services use the same shared network created by the dev container
- Enables communication between dev container and all database services

## How It Works Now

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Windows Host (Optional)                        │
│                                   │                                   │
│                                   ↓ localhost:1433, :27017, etc.     │
└───────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────────────────────────────────────────┐
│                           WSL2 Docker Host                            │
│                                   │                                   │
│  WSL Terminal/Tools ──────────────┤ (localhost:1433, :27017, etc.)   │
│                                   │                                   │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              tool-library-network (bridge)                       │ │
│  │                                                                   │ │
│  │  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐          │ │
│  │  │ Dev Container│  │  mssql1  │  │    mongodb1-3    │          │ │
│  │  │   (VSCode)   │  │          │  │                  │          │ │
│  │  │              │  │   :1433  │  │ :27017-27019     │          │ │
│  │  └──────────────┘  └──────────┘  └──────────────────┘          │ │
│  │         │                │                  │                    │ │
│  │         └─────────────────┴──────────────────┘                   │ │
│  │           Container name resolution (mssql1, mongodb1, etc.)     │ │
│  │                                                                   │ │
│  │  ┌──────────┐  ┌───────────┐  ┌────────────────────┐           │ │
│  │  │  psql1-2 │  │   kafka1  │  │     rabbitmq1      │           │ │
│  │  │          │  │           │  │                    │           │ │
│  │  │ :5432-33 │  │   :9092   │  │  :5672, :15672     │           │ │
│  │  └──────────┘  └───────────┘  └────────────────────┘           │ │
│  │                                                                   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                           ↑                                           │
│                           │ Ports published to WSL                    │
│                    (via docker-compose.yml)                           │
└───────────────────────────────────────────────────────────────────────┘
```

## Connectivity Summary

### From Dev Container (Inside VS Code)

✅ **Use container names** on the shared network:

- MongoDB: `mongodb://mongodb1:27017,mongodb2:27017,mongodb3:27017`
- SQL Server: `Server=mssql1,1433`
- PostgreSQL: `host=psql1, port=5432`
- Kafka: `kafka1:29092` (internal) or `kafka1:9092`

### From WSL Terminal/Tools (Outside Dev Container)

✅ **Use localhost** with published ports:

- MongoDB: `mongodb://localhost:27017` (mongodb1), `localhost:27018` (mongodb2), `localhost:27019` (mongodb3)
- SQL Server: `sqlcmd -S localhost,1433`
- PostgreSQL: `psql -h localhost -p 5432`
- Kafka: `localhost:9092`

### From Windows Host (Optional)

✅ **Use localhost** - WSL2 forwards to Windows:

- Same as WSL: `localhost:1433`, `localhost:27017`, etc.
- Example: Connect SQL Server Management Studio to `localhost,1433`

## Testing Connectivity

This section provides detailed commands to test connectivity from all locations.

### Test 1: From Dev Container to Database Containers

Open a terminal inside VS Code (which runs in the dev container):

```bash
# === DNS Resolution Tests ===
# Test if container names resolve to IP addresses
ping -c 1 mssql1
ping -c 1 mongodb1
ping -c 1 mongodb2
ping -c 1 mongodb3
ping -c 1 psql1
ping -c 1 kafka1
ping -c 1 rabbitmq1
ping -c 1 hvault

# === Port Connectivity Tests ===
# Test if services are listening on their ports
nc -zv mssql1 1433          # SQL Server
nc -zv mongodb1 27017       # MongoDB instance 1
nc -zv mongodb2 27017       # MongoDB instance 2
nc -zv mongodb3 27017       # MongoDB instance 3
nc -zv psql1 5432           # PostgreSQL instance 1
nc -zv psql2 5432           # PostgreSQL instance 2
nc -zv kafka1 9092          # Kafka
nc -zv rabbitmq1 5672       # RabbitMQ AMQP
nc -zv rabbitmq1 15672      # RabbitMQ Management
nc -zv hvault 8200          # HashiCorp Vault

# === Network Inspection ===
# List all containers on the network
docker network inspect tool-library-network

# See container names on the network (formatted)
docker network inspect tool-library-network --format '{{range .Containers}}{{.Name}} {{end}}'

# === Database Connection Tests ===
# SQL Server (if sqlcmd is installed in dev container)
sqlcmd -S mssql1,1433 -U sa -P 'YourStrong!Passw0rd' -Q "SELECT @@VERSION"

# MongoDB (if mongosh is installed)
mongosh "mongodb://mongodb1:27017,mongodb2:27017,mongodb3:27017/?replicaSet=rs0" --eval "rs.status()"

# PostgreSQL (if psql is installed)
psql -h psql1 -p 5432 -U postgres -c "SELECT version();"

# === Python Connection Tests ===
# Test with Python (if packages are installed)
python3 << 'EOF'
import socket

# Test if services are reachable
services = {
    'mssql1': 1433,
    'mongodb1': 27017,
    'psql1': 5432,
    'kafka1': 9092,
    'rabbitmq1': 5672
}

for host, port in services.items():
    try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        print(f"✅ {host}:{port} - Connected")
    except Exception as e:
        print(f"❌ {host}:{port} - Failed: {e}")
EOF
```

### Test 2: From WSL Host to Database Containers

Open a WSL terminal (outside of VS Code, directly on WSL):

```bash
# === Verify Docker is Running ===
docker ps
docker network ls | grep tool-library-network

# === Test Localhost Connectivity ===
# These should work because docker-compose publishes ports to localhost

# SQL Server
sqlcmd -S localhost,1433 -U sa -P 'YourStrong!Passw0rd' -Q "SELECT @@VERSION"
# Or test port
nc -zv localhost 1433

# MongoDB instances
mongosh mongodb://localhost:27017 --eval "db.version()"  # mongodb1
mongosh mongodb://localhost:27018 --eval "db.version()"  # mongodb2
mongosh mongodb://localhost:27019 --eval "db.version()"  # mongodb3
# Or test ports
nc -zv localhost 27017
nc -zv localhost 27018
nc -zv localhost 27019

# PostgreSQL instances
psql -h localhost -p 5432 -U postgres -c "SELECT version();"  # psql1
psql -h localhost -p 5433 -U postgres -c "SELECT version();"  # psql2
# Or test ports
nc -zv localhost 5432
nc -zv localhost 5433

# Kafka
nc -zv localhost 9092

# RabbitMQ
nc -zv localhost 5672     # AMQP
nc -zv localhost 15672    # Management UI (can also open in browser: http://localhost:15672)

# HashiCorp Vault
nc -zv localhost 8200
# Or test HTTP endpoint
curl http://localhost:8200/v1/sys/health

# === Test All Ports at Once ===
for port in 1433 5432 5433 8200 9092 5672 15672 27017 27018 27019; do
  if nc -zv -w 1 localhost $port 2>&1 | grep -q succeeded; then
    echo "✅ Port $port - Open"
  else
    echo "❌ Port $port - Closed"
  fi
done
```

### Test 3: From Windows Host to Database Containers

Open Windows PowerShell or Command Prompt:

```powershell
# === Test Basic Connectivity ===
# Test if ports are open (PowerShell)
Test-NetConnection -ComputerName localhost -Port 1433    # SQL Server
Test-NetConnection -ComputerName localhost -Port 27017   # MongoDB 1
Test-NetConnection -ComputerName localhost -Port 5432    # PostgreSQL 1
Test-NetConnection -ComputerName localhost -Port 9092    # Kafka

# === SQL Server Management Studio (SSMS) ===
# Connect using these settings:
# Server name: localhost,1433
# Authentication: SQL Server Authentication
# Login: sa
# Password: YourStrong!Passw0rd

# === Command Line Tests ===
# SQL Server (if sqlcmd is installed on Windows)
sqlcmd -S localhost,1433 -U sa -P YourStrong!Passw0rd -Q "SELECT @@VERSION"

# MongoDB (if mongosh is installed on Windows)
mongosh mongodb://localhost:27017
mongosh mongodb://localhost:27018
mongosh mongodb://localhost:27019

# PostgreSQL (if psql is installed on Windows)
psql -h localhost -p 5432 -U postgres

# === Web Browser Tests ===
# RabbitMQ Management UI
# Open in browser: http://localhost:15672
# Default credentials: devuser / devpassword

# HashiCorp Vault UI (if enabled)
# Open in browser: http://localhost:8200

# === PowerShell Port Scanner ===
$ports = @(1433, 5432, 5433, 8200, 9092, 5672, 15672, 27017, 27018, 27019)
foreach ($port in $ports) {
    $result = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
    if ($result) {
        Write-Host "✅ Port $port - Open" -ForegroundColor Green
    } else {
        Write-Host "❌ Port $port - Closed" -ForegroundColor Red
    }
}
```

### Test 4: Between Database Containers

Test connectivity between database containers (peer-to-peer):

```bash
# From WSL or dev container terminal:

# === MongoDB to SQL Server ===
docker exec mongodb1 bash -c "
    apt-get update -qq && apt-get install -y -qq netcat-openbsd 2>/dev/null
    nc -zv mssql1 1433 && echo '✅ MongoDB can reach SQL Server'
"

# === SQL Server to MongoDB ===
docker exec mssql1 bash -c "
    apt-get update -qq && apt-get install -y -qq netcat-openbsd 2>/dev/null
    nc -zv mongodb1 27017 && echo '✅ SQL Server can reach MongoDB'
"

# === PostgreSQL to MongoDB ===
docker exec psql1 bash -c "
    apt-get update -qq && apt-get install -y -qq netcat-openbsd 2>/dev/null
    nc -zv mongodb1 27017 && echo '✅ PostgreSQL can reach MongoDB'
"

# === Kafka to Zookeeper (should already be connected) ===
docker exec kafka1 bash -c "
    nc -zv zookeeper 2181 && echo '✅ Kafka can reach Zookeeper'
"

# === Test Multiple Containers ===
for container in mongodb1 mssql1 psql1; do
    echo "Testing from $container..."
    docker exec $container bash -c "
        which nc >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq netcat-openbsd 2>/dev/null)
        for target in mssql1:1433 mongodb1:27017 psql1:5432; do
            host=\${target%:*}
            port=\${target#*:}
            if [ \"\$host\" != \"$container\" ]; then
                nc -zv \$host \$port 2>&1 | grep -q succeeded && echo \"  ✅ $container -> \$target\" || echo \"  ❌ $container -> \$target\"
            fi
        done
    " 2>/dev/null
done
```

### Test 5: Comprehensive Network Validation Script

Save this as a script for easy testing:

```bash
#!/bin/bash
# Save as: test-network-connectivity.sh
# Run from: Dev container or WSL

echo "=========================================="
echo "Network Connectivity Test Suite"
echo "=========================================="
echo ""

# Test 1: Network Exists
echo "1. Checking if tool-library-network exists..."
if docker network inspect tool-library-network >/dev/null 2>&1; then
    echo "   ✅ Network exists"
else
    echo "   ❌ Network does NOT exist"
    exit 1
fi
echo ""

# Test 2: List Connected Containers
echo "2. Containers connected to network:"
docker network inspect tool-library-network --format '{{range .Containers}}   - {{.Name}}{{"\n"}}{{end}}'
echo ""

# Test 3: DNS Resolution (from dev container only)
if [ -f /.dockerenv ]; then
    echo "3. Testing DNS resolution from dev container..."
    for host in mssql1 mongodb1 psql1 kafka1 rabbitmq1; do
        if ping -c 1 -W 1 $host >/dev/null 2>&1; then
            echo "   ✅ $host resolves"
        else
            echo "   ❌ $host does NOT resolve"
        fi
    done
    echo ""
fi

# Test 4: Port Connectivity from Host
echo "4. Testing port connectivity from host (localhost)..."
declare -A ports=(
    [1433]="SQL Server"
    [5432]="PostgreSQL 1"
    [5433]="PostgreSQL 2"
    [27017]="MongoDB 1"
    [27018]="MongoDB 2"
    [27019]="MongoDB 3"
    [9092]="Kafka"
    [5672]="RabbitMQ"
    [15672]="RabbitMQ UI"
    [8200]="Vault"
)

for port in "${!ports[@]}"; do
    if nc -zv -w 1 localhost $port 2>&1 | grep -q succeeded; then
        echo "   ✅ ${ports[$port]} (localhost:$port)"
    else
        echo "   ❌ ${ports[$port]} (localhost:$port) - Not accessible"
    fi
done

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
```

Make it executable and run:

```bash
chmod +x test-network-connectivity.sh
./test-network-connectivity.sh
```

## What to Do Next

1. **Rebuild the dev container:**
   - Press `F1` or `Ctrl+Shift+P`
   - Type "Dev Containers: Rebuild Container"
   - Select it and press Enter

2. **The container should now:**
   - Build successfully
   - Start without hanging
   - Complete the `postCreateCommand` script
   - Return control to VS Code

3. **Start database containers:**

   ```bash
   # From within dev container
   cd /workspaces/dbtools/docker/mssql
   docker-compose up -d

   cd /workspaces/dbtools/docker/mongodb
   docker-compose up -d

   cd /workspaces/dbtools/docker/postgresql
   docker-compose up -d
   ```

4. **Test network connectivity** - See detailed testing instructions in the "Testing Connectivity" section below

5. **Connect to databases:**
   Your Python code can now connect to databases using container names:

   ```python
   # SQL Server
   connection_string = "Server=mssql1,1433;Database=master;..."

   # MongoDB
   connection_string = "mongodb://mongodb1:27017,mongodb2:27017,mongodb3:27017"
   ```

## Key Benefits

1. **Faster Startup:** No Docker daemon initialization delay
2. **Reliable:** Uses host Docker daemon (more stable in WSL2)
3. **Network Connectivity:** Dev container and services on same network
4. **Service Discovery:** Access services by name (mssql1, mongodb1, etc.)
5. **Better Performance:** Shared Docker daemon uses fewer resources

## Troubleshooting

### If the network doesn't exist when starting a service

```bash
docker network create --driver bridge tool-library-network
```

### If containers can't communicate

```bash
# Verify all containers are on the same network
docker network inspect tool-library-network
```

### If you need to recreate the network

```bash
# Stop all containers first
docker stop $(docker ps -q)

# Remove the network
docker network rm tool-library-network

# Recreate it
docker network create --driver bridge tool-library-network

# Restart dev container
```

## Files Changed

- `.devcontainer/ubuntu/devcontainer.json` - Docker feature, network config, removed redundant port mappings
- `.devcontainer/redhat/devcontainer.json` - Docker feature, network config
- `docker/mongodb/docker-compose.yml` - External network
- `docker/mssql/docker-compose.yml` - External network
- `docker/postgresql/docker-compose.yml` - External network
- `docker/kafka/docker-compose.yml` - External network
- `docker/rabbitmq/docker-compose.yml` - External network
- `docker/liquibase/docker-compose.yml` - External network
- `docker/docker-compose.yml` - External network (vault)

## Important Note About Port Mappings

With `docker-outside-of-docker`, the database containers run directly on the WSL Docker daemon and publish their own ports via docker-compose files. The dev container **does not need** to forward ports - it connects to databases using container names on the shared network, while WSL/Windows hosts connect using `localhost` with the published ports.
