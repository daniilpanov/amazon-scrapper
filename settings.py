import dotenv
import os

import fake_useragent

if not dotenv.load_dotenv('.env'):
    dotenv.load_dotenv('../.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')
# POWER LIMITS (active browsers quantity depending on sum of these numbers)
THREADS = {
    'reviews': int(os.environ.get('REVIEWS_THREADS', 10)),
    'products': int(os.environ.get('PRODUCTS_THREADS') or 0),
    'departments': int(os.environ.get('DEPARTMENTS_THREADS') or 0),
    'all': int(os.environ.get('ALL_THREADS', os.cpu_count())),
}
THREADS['collect_reviews'] = THREADS['reviews']
THREADS['collect_products'] = THREADS['products']
THREADS['collect_departments'] = THREADS['departments']
MAX_PROCESSES = os.environ.get('MAX_PROCESSES')

SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE')

SQL_DB_NAME = os.environ.get('DB_NAME')
SQL_DB_USER = os.environ.get('DB_USER')
SQL_DB_PASS = os.environ.get('DB_PASS')
SQL_DB_HOST = os.environ.get('DB_HOST')
SQL_DB_PORT = int(os.environ.get('DB_PORT') or 3306)

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_USER_RESERVE = os.environ.get('MONGO_BD_USER_RESERVE')
MONGO_DB_PASS_RESERVE = os.environ.get('MONGO_BD_PASS_RESERVE')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
MONGO_DB_HOST_SCHEMA = os.environ.get('MONGO_DB_HOST_SCHEMA')
MONGO_DB_PROXY = os.environ.get('MONGO_DB_PROXY')

WEB_PROXY = os.environ.get('WEB_PROXY')
PROXY_AUTH_TOKEN = os.environ.get('PROXY_AUTH_TOKEN')
OPENVPN = os.environ.get('OPENVPN')
OPENVPN_LOGIN = os.environ.get('OPENVPN_LOGIN')
OPENVPN_PASSWORD = os.environ.get('OPENVPN_PASSWORD')

# UserAgent Maker
ua = fake_useragent.UserAgent(browsers=['chrome'], min_version=119.0, platforms=['pc'])
