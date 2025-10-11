import os

import fake_useragent

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')

DEFAULT_SERVICE_FILE = os.environ.get('DEFAULT_SERVICE_FILE')

SQL_DB_NAME = os.environ.get('DB_NAME')
SQL_DB_USER = os.environ.get('DB_USER')
SQL_DB_PASS = os.environ.get('DB_PASS')
SQL_DB_HOST = os.environ.get('DB_HOST')
SQL_DB_PORT = int(os.environ.get('DB_PORT') or 3306)

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
MONGO_DB_HOST_SCHEMA = os.environ.get('MONGO_DB_HOST_SCHEMA')
MONGO_DB_PROXY = os.environ.get('MONGO_DB_PROXY')

WEB_PROXY = os.environ.get('WEB_PROXY')
PROXY_AUTH_TOKEN = os.environ.get('PROXY_AUTH_TOKEN')

WEB_PORT = int(os.environ.get('WEB_PORT') or 8838)

# UserAgent Maker
ua = fake_useragent.UserAgent(browsers=['chrome'], min_version=119.0, platforms=['pc'])
