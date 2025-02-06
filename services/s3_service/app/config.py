from os import environ as env

ACCESS_KEY = env.get('S3_ACCESS_KEY')
SECRET_KEY = env.get('S3_SECRET_KEY')
BASE_BUCKET = env.get('BASE_BUCKET')
PORT = int(env.get('S3_PORT', 8836))
