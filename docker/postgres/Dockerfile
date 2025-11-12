FROM postgres:latest

# Create directories for persistent volumes
RUN mkdir -p /gds/data/postgres /gds/log/postgres && \
    chown -R postgres:postgres /gds

# Define volumes for persistent storage
VOLUME ["/gds/data/postgres", "/gds/log/postgres"]

EXPOSE 5432

CMD ["postgres"]
