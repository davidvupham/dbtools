#!/bin/bash
set -e

# Default instance name if not provided
MONGO_INSTANCE="${MONGO_INSTANCE:-instance1}"

# Create instance-specific directories
INSTANCE_DATA_DIR="/data/mongodb/${MONGO_INSTANCE}/data"
INSTANCE_LOG_DIR="/logs/mongodb/${MONGO_INSTANCE}"

# Keyfile location (shared across all instances)
KEYFILE_PATH="/data/mongodb/mongodb-keyfile"

# Copy keyfile from template if it doesn't exist in the volume
if [ ! -f "${KEYFILE_PATH}" ] && [ -f "/tmp/mongodb-keyfile.template" ]; then
    cp /tmp/mongodb-keyfile.template "${KEYFILE_PATH}"
    chown mongodb:mongodb "${KEYFILE_PATH}"
    chmod 400 "${KEYFILE_PATH}"
fi

# Extract instance number or use full name for config file
# mongodb1 -> mdb1.conf, mongodb2 -> mdb2.conf, etc.
if [[ "${MONGO_INSTANCE}" =~ ^mongodb([0-9]+)$ ]]; then
    CONFIG_NAME="mdb${BASH_REMATCH[1]}.conf"
else
    CONFIG_NAME="${MONGO_INSTANCE}.conf"
fi

INSTANCE_CONFIG="/data/mongodb/${MONGO_INSTANCE}/${CONFIG_NAME}"

mkdir -p "${INSTANCE_DATA_DIR}"
mkdir -p "${INSTANCE_LOG_DIR}"
mkdir -p "$(dirname ${INSTANCE_CONFIG})"

# Create or update MongoDB configuration file if it doesn't exist or needs updating
if [ ! -f "${INSTANCE_CONFIG}" ]; then
    cat > "${INSTANCE_CONFIG}" <<EOF
# MongoDB configuration file for instance: ${MONGO_INSTANCE}

# Where and how to store data
storage:
  dbPath: ${INSTANCE_DATA_DIR}

# Where to write logging data
systemLog:
  destination: file
  logAppend: true
  path: ${INSTANCE_LOG_DIR}/mongod.log

# Network interfaces
net:
  port: 27017
  bindIp: 0.0.0.0

# Replication
replication:
  replSetName: mdbreplset1

# Security
security:
  keyFile: ${KEYFILE_PATH}

# Process management
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
EOF
fi

# Set proper ownership
chown -R mongodb:mongodb /data/mongodb/${MONGO_INSTANCE}
chown -R mongodb:mongodb /logs/mongodb/${MONGO_INSTANCE}

# If the command is mongod, run it with the instance config
if [ "$1" = 'mongod' ]; then
    exec gosu mongodb "$@" --config "${INSTANCE_CONFIG}"
else
    exec "$@"
fi
