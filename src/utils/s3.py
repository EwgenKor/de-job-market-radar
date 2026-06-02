import logging
import os
from pathlib import Path

import boto3
from botocore.client import Config
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")


def get_s3_client():
    if not all([S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY]):
        raise ValueError("S34 config is not fully set in .env")

    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def upload_file_to_s3(local_file_path: Path, s3_key: str):
    if S3_BUCKET is None:
        raise ValueError("S3_BUCKET is not set in .env")

    s3_client = get_s3_client()

    logger.info(
        "Uploading %s to s3://%s/%s",
        local_file_path,
        S3_BUCKET,
        s3_key,
    )

    s3_client.upload_file(
        Filename=str(local_file_path),
        Bucket=S3_BUCKET,
        Key=s3_key,
    )


    logger.info(
        "Uploaded %s to s3://%s/%s",
        local_file_path,
        S3_BUCKET,
        s3_key,
    )