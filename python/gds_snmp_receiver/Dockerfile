FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && uv pip install --python /app/.venv/bin/python -r pyproject.toml

FROM python:3.11-slim

# Do not generate .pyc files and ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user to run the service
RUN addgroup --system snmp && adduser --system --ingroup snmp snmp

# Copy package source into image under a package directory so
# python can import using `-m gds_snmp_receiver.receiver` when
# the container's working directory (/app) is on sys.path.
COPY . /app/gds_snmp_receiver

# Ensure the entrypoint is executable (it lives inside the package)
RUN chmod +x /app/gds_snmp_receiver/entrypoint.sh

# Fix ownership and drop to non-root user
RUN chown -R snmp:snmp /app
USER snmp

# Expose the UDP port (note: publish as UDP from host with -p 162:162/udp)
EXPOSE 162/udp

# Copy healthcheck and enable a HEALTHCHECK so orchestrators can probe
# for receiver process presence. The healthcheck looks for the running
# Python commandline in /proc. It relies on the bundled healthcheck.py.
COPY healthcheck.py /app/healthcheck.py

# Entrypoint provides flexibility to run commands or the default CMD
ENTRYPOINT ["/app/gds_snmp_receiver/entrypoint.sh"]
CMD ["python", "-m", "gds_snmp_receiver.receiver"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD python /app/healthcheck.py || exit 1
