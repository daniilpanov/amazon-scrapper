import boto3
from botocore.exceptions import NoCredentialsError

from .config import *

session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

s3res = session.resource('s3')
s3client = session.client('s3')

default_bucket = s3res.Bucket(BASE_BUCKET)


def upload_file(local_filename, filename, prefix):
    try:
        s3client.upload_file(local_filename, BASE_BUCKET, prefix + filename)
        return True
    except FileNotFoundError:
        print(f'The file {local_filename} was not found')
        return False
    except NoCredentialsError:
        print('Credentials not available')
        return False
    except Exception as e:
        print(f'Error occurred: {e}')
        return False
