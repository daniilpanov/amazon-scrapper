

from io import BytesIO

import boto3
from botocore.exceptions import ClientError

from config import *

session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

s3res = session.resource('s3')
s3client = session.client('s3')

default_bucket = s3res.Bucket(BASE_BUCKET)


def get_file_list(path: str = ''):
    res = []
    for list_object in default_bucket.objects.all():
        if not path or list_object.key.startswith(path):
            res.append(list_object)
    return res


def load_content(item_key: str):
    io = BytesIO()
    try:
        s3client.download_fileobj(BASE_BUCKET, item_key, io)
        return io
    except ClientError:
        return None

