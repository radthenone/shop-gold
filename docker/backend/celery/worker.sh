#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# wait for redis
echo "Checking Redis connection..."
until redis-cli -h redis ping; do
    >&2 echo "Redis is unavailable - waiting"
    sleep 1
done

echo "Starting Celery worker..."
# logs exists
mkdir -p logs

# run celery worker
exec celery -A core.celery worker -l info
