import os
import boto3

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

def generate_upload_url(key: str, expiration: int = 3600):
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expiration
    )

def generate_download_url(key: str, expiration: int = 3600):
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expiration
    )