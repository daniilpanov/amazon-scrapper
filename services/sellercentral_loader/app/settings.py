import os

import fake_useragent

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
MONGO_DB_HOST_SCHEMA = os.environ.get('MONGO_DB_HOST_SCHEMA')
MONGO_DB_PROXY = os.environ.get('MONGO_DB_PROXY')
