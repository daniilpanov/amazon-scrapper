from os import environ as env

ACCESS_KEY = env.get('ACCESS_KEY')
SECRET_KEY = env.get('SECRET_KEY')
BASE_BUCKET = env.get('BASE_BUCKET')

MONGO_DB_USER = env.get('MONGO_DB_USER')
MONGO_DB_PASS = env.get('MONGO_DB_PASS')
MONGO_DB_HOST = env.get('MONGO_DB_HOST')
MONGO_DB_HOST_SCHEMA = env.get('MONGO_DB_HOST_SCHEMA')
MONGO_DB_PROXY = env.get('MONGO_DB_PROXY')
