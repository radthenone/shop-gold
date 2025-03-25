#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo "Python path: $(which python)"
python -c "import django; print('Django version:', django.__version__)"

echo "Waiting for PostgreSQL..."
/wait_for_db.sh

echo "Waiting for Redis..."
until redis-cli -h redis ping > /dev/null 2>&1; do
    echo "Redis is unavailable - waiting"
    sleep 2
done
echo "Redis is available"

if [ "${ENVIRONMENT:-development}" == "development" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

mkdir -p logs
exec "$@"