import os

import fake_useragent

ua = fake_useragent.UserAgent(browsers=['chrome'], min_version=119.0, platforms=['pc'])

PROXY_AUTH_TOKEN = os.environ.get('PROXY_AUTH_TOKEN')

MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST', 'localhost')
MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST_SCHEMA = os.environ.get('MONGO_DB_HOST_SCHEMA')

PORT = int(os.environ.get('PROXIES_PORT') or 8833)
