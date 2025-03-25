ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.6.3

# Stage 1: Get uv tool
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# Stage 2: Builder
FROM python:${PYTHON_VERSION}-slim AS builder

# Set working directory
WORKDIR /src

# Copy pyproject.toml and uv.lock
COPY backend/pyproject.toml backend/uv.lock /src/

ENV UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN --mount=from=uv,source=/uv,target=/bin/uv \
	uv pip compile pyproject.toml --all-extras -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Stage 2: Dev
FROM python:${PYTHON_VERSION}-slim AS dev

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
	redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /src

# Copy installed packages and project code from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the project code
COPY backend/src/ /src/

# Copy scripts
COPY docker/backend/django/runserver.sh /runserver.sh
COPY docker/backend/django/check_superuser.sh /check_superuser.sh
COPY docker/backend/db/wait_for_db.sh /wait_for_db.sh
COPY docker/backend/s3/wait_for_s3.sh /wait_for_s3.sh
COPY docker/backend/s3/setup_buckets.sh /setup_buckets.sh
COPY docker/backend/celery/* /celery/
COPY docker/backend/entrypoint.sh /entrypoint.sh

# Make scripts executable and remove Windows line endings
RUN sed -i 's/\r$//g' /runserver.sh && chmod +x /runserver.sh && \
    sed -i 's/\r$//g' /check_superuser.sh && chmod +x /check_superuser.sh && \
    sed -i 's/\r$//g' /wait_for_db.sh && chmod +x /wait_for_db.sh && \
    sed -i 's/\r$//g' /wait_for_s3.sh && chmod +x /wait_for_s3.sh && \
    sed -i 's/\r$//g' /setup_buckets.sh && chmod +x /setup_buckets.sh && \
    sed -i 's/\r$//g' /celery/*.sh && chmod +x /celery/*.sh && \
    sed -i 's/\r$//g' /entrypoint.sh && chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]