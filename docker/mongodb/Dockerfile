FROM mongo:latest

# Create directories for persistent volumes
RUN mkdir -p /gds/data/mongodb /gds/log/mongodb && \
    chown -R mongodb:mongodb /gds

# Copy keyfile to a temporary location (will be moved to persistent volume on first run)
COPY mongodb-keyfile /tmp/mongodb-keyfile.template

# Define volumes for persistent storage
VOLUME ["/gds/data/mongodb", "/gds/log/mongodb"]

EXPOSE 27017

# Use entrypoint script to handle instance-specific configuration
COPY docker-entrypoint-custom.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint-custom.sh

ENTRYPOINT ["docker-entrypoint-custom.sh"]
CMD ["mongod"]
