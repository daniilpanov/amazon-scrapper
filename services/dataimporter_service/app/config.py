import os
from hashlib import sha256

API_KEY = os.environ.get('DATA_IMPORTER_API_KEY')
API_KEY_HASHED = sha256(API_KEY.encode('utf-8')).hexdigest()

MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST', 'localhost')
MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST_SCHEMA = os.environ.get('MONGO_DB_HOST_SCHEMA')

PORT = int(os.environ.get('DATA_IMPORTER_PORT') or 8831)
