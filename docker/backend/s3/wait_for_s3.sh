#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

s3_ready() {
python << END
import sys
import time
import boto3
from botocore.exceptions import ClientError

client = boto3.client(
    "s3",
    endpoint_url="${AWS_S3_ENDPOINT_URL}",
    aws_access_key_id="${AWS_ACCESS_KEY_ID}",
    aws_secret_access_key="${AWS_SECRET_ACCESS_KEY}",
    use_ssl=False,
    verify=False
)

try:
    client.list_buckets()
    sys.exit(0)
except Exception as e:
    sys.stderr.write(f"Error connecting to MinIO: {e}\n")
    sys.exit(1)
END
}

timeout=30
start_time=$(date +%s)

until s3_ready; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    
    if [ $elapsed_time -gt $timeout ]; then
        echo "MinIO not available after ${timeout} seconds"
        exit 1
    fi
    
    echo "Waiting for MinIO... ($elapsed_time seconds)"
    sleep 1
done

echo "MinIO is available"