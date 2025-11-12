# MongoDB Replica Set Setup Guide

This guide explains how to set up and run a 3-node MongoDB replica set using Docker.

## Overview

- **Replica Set Name**: `mdbreplset1`
- **Instances**: mongodb1, mongodb2, mongodb3
- **Ports**: 27017, 27018, 27019
- **MongoDB Version**: 8.2.1

## Directory Structure

Each MongoDB instance has its own persistent directories:

```
/gds/data/mongodb/
├── mongodb1/
│   ├── mdb1.conf          # Configuration file
│   └── data/              # Database files
├── mongodb2/
│   ├── mdb2.conf          # Configuration file
│   └── data/              # Database files
└── mongodb3/
    ├── mdb3.conf          # Configuration file
    └── data/              # Database files

/gds/log/mongodb/
├── mongodb1/
│   └── mongod.log         # Log file
├── mongodb2/
│   └── mongod.log         # Log file
└── mongodb3/
    └── mongod.log         # Log file
```

## Configuration Files

Each instance is configured with:

- Data path: `/gds/data/mongodb/mongodb{N}/data`
- Log path: `/gds/log/mongodb/mongodb{N}/mongod.log`
- Replica set: `mdbreplset1`
- Bind IP: `0.0.0.0` (all interfaces)
- Port: `27017` (internal, mapped to different host ports)

## Step 1: Build the Docker Image

```bash
cd /workspaces/dbtools/docker/mongodb
docker build -t gds-mongodb:latest .
```

## Step 2: Start the MongoDB Instances

Using Docker Compose:

```bash
cd /workspaces/dbtools/docker/mongodb
docker-compose up -d
```

Or start manually:

```bash
# Instance 1
docker run -d --name mongodb1 -p 27017:27017 \
  -e MONGO_INSTANCE=mongodb1 \
  -v gds-mongodb-data:/gds/data/mongodb \
  -v gds-mongodb-log:/gds/log/mongodb \
  --network mongodb-network \
  gds-mongodb:latest

# Instance 2
docker run -d --name mongodb2 -p 27018:27017 \
  -e MONGO_INSTANCE=mongodb2 \
  -v gds-mongodb-data:/gds/data/mongodb \
  -v gds-mongodb-log:/gds/log/mongodb \
  --network mongodb-network \
  gds-mongodb:latest

# Instance 3
docker run -d --name mongodb3 -p 27019:27017 \
  -e MONGO_INSTANCE=mongodb3 \
  -v gds-mongodb-data:/gds/data/mongodb \
  -v gds-mongodb-log:/gds/log/mongodb \
  --network mongodb-network \
  gds-mongodb:latest
```

## Step 3: Verify Instances are Running

```bash
docker ps | grep mongodb
```

You should see all three instances running.

## Step 4: Check Logs

```bash
# View logs for all instances
docker-compose logs -f

# Or check individual instances
docker logs mongodb1
docker logs mongodb2
docker logs mongodb3

# Or check log files directly
docker exec mongodb1 tail -f /gds/log/mongodb/mongodb1/mongod.log
```

## Step 5: Initialize the Replica Set

Connect to the primary instance (mongodb1) and initialize the replica set:

```bash
docker exec -it mongodb1 mongosh
```

In the MongoDB shell, run:

```javascript
rs.initiate({
  _id: "mdbreplset1",
  members: [
    { _id: 0, host: "mongodb1:27017" },
    { _id: 1, host: "mongodb2:27017" },
    { _id: 2, host: "mongodb3:27017" }
  ]
})
```

You should see a response like:

```javascript
{ ok: 1 }
```

## Step 6: Verify Replica Set Status

After a few seconds, check the replica set status:

```javascript
rs.status()
```

This will show detailed information about the replica set, including:

- Which member is PRIMARY
- Which members are SECONDARY
- Health status of each member
- Replication lag

To see a simpler view:

```javascript
rs.conf()  // Show replica set configuration
rs.isMaster()  // Check if current node is primary
```

## Step 7: Test Replication

### On the Primary Node

```javascript
// Switch to a test database
use testdb

// Insert a document
db.testcol.insertOne({ name: "test", value: 123 })

// Verify insertion
db.testcol.find()
```

### On a Secondary Node

Connect to a secondary:

```bash
docker exec -it mongodb2 mongosh
```

In the MongoDB shell:

```javascript
// Enable reading from secondary
rs.secondaryOk()
// or in newer versions:
db.getMongo().setReadPref('secondary')

// Switch to test database
use testdb

// Verify the data was replicated
db.testcol.find()
```

You should see the same document you inserted on the primary.

## Accessing MongoDB from Host

- **mongodb1**: `mongodb://localhost:27017`
- **mongodb2**: `mongodb://localhost:27018`
- **mongodb3**: `mongodb://localhost:27019`

Connection string for replica set from host:

```
mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=mdbreplset1
```

## Common Operations

### Stop All Instances

```bash
docker-compose down
```

### Stop Without Removing Volumes (Data Persists)

```bash
docker-compose stop
```

### Start Stopped Instances

```bash
docker-compose start
```

### Remove Everything Including Data

```bash
docker-compose down -v
```

### View Configuration Files

```bash
docker exec mongodb1 cat /gds/data/mongodb/mongodb1/mdb1.conf
docker exec mongodb2 cat /gds/data/mongodb/mongodb2/mdb2.conf
docker exec mongodb3 cat /gds/data/mongodb/mongodb3/mdb3.conf
```

### Add Authentication (Optional)

To add authentication to the replica set:

1. Create a keyfile for internal authentication:

```bash
openssl rand -base64 756 > mongodb-keyfile
chmod 400 mongodb-keyfile
```

2. Update the config files to include:

```yaml
security:
  authorization: enabled
  keyFile: /gds/data/mongodb/mongodb-keyfile
```

3. Create an admin user on the primary:

```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "securepassword",
  roles: [ { role: "root", db: "admin" } ]
})
```

## Troubleshooting

### Check if MongoDB is Running

```bash
docker exec mongodb1 mongosh --eval "db.adminCommand('ping')"
```

### Check Replica Set Member Health

```javascript
rs.status().members.forEach(function(member) {
  print(member.name + ": " + member.stateStr + " (health: " + member.health + ")")
})
```

### View Recent Errors

```bash
docker exec mongodb1 tail -100 /gds/log/mongodb/mongodb1/mongod.log
```

### Re-initialize Replica Set

If you need to start over:

```bash
# Stop all instances
docker-compose down -v

# Start them again
docker-compose up -d

# Wait for all instances to be ready, then re-initialize
docker exec -it mongodb1 mongosh
rs.initiate({...})  # Use the same config as before
```

## Performance Considerations

- **Write Concern**: By default, writes must be acknowledged by the primary. You can configure write concern to wait for replication:

```javascript
db.collection.insertOne(
  { data: "example" },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)
```

- **Read Preference**: Configure your application to read from secondaries to distribute load:
  - `primary` (default)
  - `primaryPreferred`
  - `secondary`
  - `secondaryPreferred`
  - `nearest`

## Backup Strategy

To backup the replica set:

```bash
# Using mongodump
docker exec mongodb1 mongodump --out /gds/data/mongodb/backup

# Or copy the data directory (while MongoDB is stopped)
docker-compose stop
sudo cp -r /var/lib/docker/volumes/gds-mongodb-data/_data /backup/location
docker-compose start
```

## References

- [MongoDB Replica Set Documentation](https://www.mongodb.com/docs/manual/replication/)
- [MongoDB Configuration File Options](https://www.mongodb.com/docs/manual/reference/configuration-options/)
- [Deploy a Replica Set](https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set/)
