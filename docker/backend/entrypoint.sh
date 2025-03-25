#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Debug: Verify Python and Django
echo "Python path: $(which python)"
python -c "import django; print('Django version:', django.__version__)" || echo "Django not found!"

echo "Waiting for PostgreSQL..."
/wait_for_db.sh

echo "Setting up storage buckets..."
/setup_buckets.sh

echo "Waiting for S3..."
sleep 5
/wait_for_s3.sh

if [ "${ENVIRONMENT:-development}" == "development" ]; then
	mkdir -p static staticfiles mediafiles

    echo "Do database migrations..."
    python manage.py migrate --noinput

    echo "Creating superuser..."
    /check_superuser.sh
	
	echo "Collect static..."
	python manage.py collectstatic --noinput
fi

echo "Starting server..."
/runserver.sh