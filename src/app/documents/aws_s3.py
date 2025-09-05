import asyncio
import datetime
import time
from fastapi import HTTPException

from fastapi import File, UploadFile
import moto
import boto3


from moto.core.utils import unix_time

mock = moto.mock_aws()
mock.start()
ALLOWED_MIME = {

    "image/jpeg", "image/png", "image/webp", "image/gif",

    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  #.doc
}


async def upload_mock(file:File(),project_id):
    import boto3, os
    s3=boto3.client('s3',region_name='eu-central-1')
    bucket  = os.getenv("S3_BUCKET")

    response = s3.list_buckets()

    print(response.get('Buckets'))

    try:
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"}
        )
        print('Bucket "{}" created.'.format(bucket))

    except s3.exceptions.BucketAlreadyOwnedByYou:
        print('Bucket "{}" already exists.'.format(bucket))

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(422)

    unix_time_now=int(time.time()*1000)
    key=f"projects/{project_id}/{unix_time_now}_{file.filename}"

    loop = asyncio.get_running_loop()

    def _do_upload():
        file.file.seek(0)
        s3.upload_fileobj(file.file, bucket, key, ExtraArgs={"ContentType": file.content_type})
        return key

    s3_key = await loop.run_in_executor(None, _do_upload)

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": s3_key},
        ExpiresIn=3600,
    )

    return {"key": key, "url": url, "mime": file.content_type}

async def download_mock(key):
    import boto3, os
    s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"))
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": os.getenv('S3_BUCKET'), "Key": key},
        ExpiresIn=300,
    )
    return {"url": url}

async def update_mock(key,mime,file:File()):
    print(file)
    import boto3, os

    s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"))
    response = s3.list_buckets()

    print(response.get('Buckets'))
    s3.upload_fileobj(file.file, os.getenv('S3_BUCKET'), key, ExtraArgs={"ContentType": mime})

async def delete_mock(key):
    import boto3, os
    client = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"))
    response = client.delete_object(
        Bucket=os.getenv('S3_BUCKET'),
        Key=key,
    )
    return response