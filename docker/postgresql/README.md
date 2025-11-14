# PostgreSQL Docker Setup

This directory contains Docker configuration for running PostgreSQL instances.

## Features

- Two independent PostgreSQL instances (psql1 and psql2)
- Persistent data storage
- Individual instance control (start/stop/build)
- Port mapping: psql1 on 5432, psql2 on 5433

## Quick Start

### Step 1: Set PostgreSQL Password

**IMPORTANT:** You must set the `POSTGRES_PASSWORD` environment variable before starting the containers. There is no default password for security reasons.

**Set the password:**

```bash
export POSTGRES_PASSWORD='YourStrong@Passw0rd123'
```

**Password Requirements:**

- At least 8 characters long
- Contains uppercase letters
- Contains lowercase letters
- Contains numbers
- Contains special characters

**Verify the password is set:**

```bash
echo $POSTGRES_PASSWORD
```

### Step 2: Build and Start Instances

#### Build and Start Both Instances

```bash
docker-compose up -d
```

### Individual Instance Control

#### Build and Start psql1 Only

```bash
docker-compose up -d psql1
```

#### Build and Start psql2 Only

```bash
docker-compose up -d psql2
```

### Stop Instances

#### Stop psql1 Only

```bash
docker-compose stop psql1
```

#### Stop psql2 Only

```bash
docker-compose stop psql2
```

#### Stop Both Instances

```bash
docker-compose stop
```

### Remove Instances

#### Remove psql1 Only

```bash
docker-compose down psql1
# or
docker-compose rm -f psql1
```

#### Remove psql2 Only

```bash
docker-compose down psql2
# or
docker-compose rm -f psql2
```

#### Remove Both Instances

```bash
docker-compose down
```

## Instance Details

### psql1

- **Container Name**: `psql1`
- **Host Port**: `5432`
- **Data Directory**: `/data/postgresql/psql1`
- **Logs Directory**: `/logs/postgresql`

### psql2

- **Container Name**: `psql2`
- **Host Port**: `5433`
- **Data Directory**: `/data/postgresql/psql2`
- **Logs Directory**: `/logs/postgresql`

## Connection Information

### Connect to psql1

```bash
# From host/dev container
psql -h localhost -p 5432 -U postgres

# From inside psql1 container
docker exec -it psql1 psql -U postgres
```

### Connect to psql2

```bash
# From host/dev container
psql -h localhost -p 5433 -U postgres

# From inside psql2 container
docker exec -it psql2 psql -U postgres
```

## Environment Variables

Set these in your environment or in a `.env` file:

- `POSTGRES_PASSWORD` - PostgreSQL superuser password (default: `YourStrong!Passw0rd`)
- `POSTGRES_DB` - Default database name (default: `postgres`)
- `POSTGRES_USER` - PostgreSQL superuser username (default: `postgres`)

## Directory Structure

```
/data/postgresql/
├── psql1/          # psql1 data directory
└── psql2/          # psql2 data directory

/logs/postgresql/   # Shared logs directory
```

## Examples

### Start only psql1

```bash
cd /workspaces/dbtools/docker/postgresql
docker-compose up -d psql1
```

### Check logs for psql1

```bash
docker logs psql1
# or
docker-compose logs psql1
```

### Restart psql2

```bash
docker-compose restart psql2
```

### View running instances

```bash
docker ps --filter name=psql
```

### Stop and remove psql1, keep psql2 running

```bash
docker-compose stop psql1
docker-compose rm -f psql1
```

## Rebuilding

If you update the Dockerfile, rebuild with:

```bash
# Rebuild and restart psql1
docker-compose up -d --build psql1

# Rebuild and restart psql2
docker-compose up -d --build psql2

# Rebuild both
docker-compose up -d --build
```

## Troubleshooting

### Check container status

```bash
docker ps -a --filter name=psql
```

### View logs

```bash
docker logs psql1
docker logs psql2
```

### Connect to container shell

```bash
docker exec -it psql1 bash
docker exec -it psql2 bash
```

### Check data directories

```bash
ls -lh /data/postgresql/psql1/
ls -lh /data/postgresql/psql2/
```
