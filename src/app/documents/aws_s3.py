import time
from fastapi import HTTPException
import os
from fastapi import File
import boto3

ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  # .doc
}


def upload_mock(file: File(), project_id):
    s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION"))
    bucket = os.getenv("S3_BUCKET")

    try:
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                "LocationConstraint": os.getenv("AWS_DEFAULT_REGION")
            },
        )
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print('Bucket "{}" already exists.'.format(bucket))

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(422)

    unix_time_now = int(time.time() * 1000)
    key = f"projects/{project_id}/{unix_time_now}_{file.filename}"

    file.file.seek(0)
    s3.upload_fileobj(
        file.file, bucket, key, ExtraArgs={"ContentType": file.content_type}
    )

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600,
    )

    return {"key": key, "url": url, "mime": file.content_type}


def download_mock(key):
    s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION"))
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": os.getenv("S3_BUCKET"), "Key": key},
        ExpiresIn=300,
    )
    return {"url": url}


def update_mock(key, mime, file: File()):
    s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION"))
    s3.upload_fileobj(
        file.file, os.getenv("S3_BUCKET"), key, ExtraArgs={"ContentType": mime}
    )


def delete_mock(key):
    client = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION"))
    response = client.delete_object(
        Bucket=os.getenv("S3_BUCKET"),
        Key=key,
    )
    return response
