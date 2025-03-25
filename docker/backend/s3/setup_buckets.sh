#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

setup_buckets() {
python << END
import sys
import json
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

buckets = ["static", "media", "products", "documents", "profiles"]

def create_bucket(bucket_name):
    try:
        client.create_bucket(Bucket=bucket_name)
        print(f"Created bucket: {bucket_name}")
        
        # Set public access for buckets
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        
        # Enable CORS
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag']
            }]
        }
        client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        print(f"Set public policy and CORS for bucket: {bucket_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
            print(f"Error creating bucket {bucket_name}: {e}", file=sys.stderr)

for bucket in buckets:
    create_bucket(bucket)
END
}

setup_buckets
echo "Storage buckets setup completed."