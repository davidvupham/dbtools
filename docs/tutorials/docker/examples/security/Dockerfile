# Security-Hardened Dockerfile
# Demonstrates: non-root user, minimal base, health checks

FROM node:20-alpine

# 1. Set working directory
WORKDIR /app

# 2. Create non-root user BEFORE copying files
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 3. Copy application files with correct ownership
COPY --chown=appuser:appgroup server.js .

# 4. Switch to non-root user
USER appuser

# 5. Use high port (non-root can't bind to <1024)
ENV PORT=8080
EXPOSE 8080

# 6. Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# 7. Run with node (not npm, for proper signal handling)
CMD ["node", "server.js"]
