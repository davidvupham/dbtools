FROM hashicorp/vault:latest

LABEL org.opencontainers.image.title="HashiCorp Vault" \
      org.opencontainers.image.description="Vault server configured for containerized deployments" \
      org.opencontainers.image.source="https://github.com/hashicorp/vault" \
      org.opencontainers.image.licenses="BUSL-1.1"

# Copy static configuration into the image. Using a single COPY keeps layer
# count to a minimum while enabling reproducible builds.
COPY docker/hvault/config/vault.hcl /vault/config/vault.hcl

# Vault drops privileges internally; keep running as the default non-root user
# provided by the base image for better security.
USER vault

ENTRYPOINT ["vault"]
CMD ["server", "-config=/vault/config/vault.hcl"]
