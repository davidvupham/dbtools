#!/usr/bin/env sh
# Minimal exec-form entrypoint. Docker supplies CMD as arguments to the
# entrypoint, so simply exec the provided arguments. This lets users override
# the command when running the container. Using exec preserves signals.
set -e

exec "$@"
