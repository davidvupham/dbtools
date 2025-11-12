FROM mongo:latest

# Create directories for persistent volumes
RUN mkdir -p /data/mongodb /logs/mongodb && \
    chown -R mongodb:mongodb /data /logs

# Copy keyfile to a temporary location (will be moved to persistent volume on first run)
COPY mongodb-keyfile /tmp/mongodb-keyfile.template

# Define volumes for persistent storage
VOLUME ["/data/mongodb", "/logs/mongodb"]

EXPOSE 27017

# Use entrypoint script to handle instance-specific configuration
COPY docker-entrypoint-custom.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint-custom.sh

ENTRYPOINT ["docker-entrypoint-custom.sh"]
CMD ["mongod"]
