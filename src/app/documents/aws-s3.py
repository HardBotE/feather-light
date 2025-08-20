from http.client import HTTPException

from fastapi import File
from moto import mock_aws
import boto3
import unittest

ALLOWED_MIME = {

    "image/jpeg", "image/png", "image/webp", "image/gif",

    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  #.doc
}

@mock_aws
def upload_mock(file:File()):
    import boto3, os
    s3=boto3.client('s3',region_name='eu-central-1')

    if file.mediatype not in ALLOWED_MIME:
        raise HTTPException(422)

    key=file
