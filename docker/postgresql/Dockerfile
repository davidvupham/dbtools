FROM postgres:latest

# Create directories for persistent volumes
RUN mkdir -p /data/postgresql /logs/postgresql && \
    chown -R postgres:postgres /data /logs

# Define volumes for persistent storage
VOLUME ["/data/postgresql", "/logs/postgresql"]

EXPOSE 5432

CMD ["postgres"]
