import dotenv
import os

if not dotenv.load_dotenv('.env'):
    dotenv.load_dotenv('../.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')
# POWER LIMITS (active browsers quantity depending on sum of these numbers)
THREADS = {
    'reviews': int(os.environ.get('REVIEWS_THREADS', 2)),
    'products': int(os.environ.get('PRODUCTS_THREADS') or 0),
    'departments': int(os.environ.get('DEPARTMENTS_THREADS') or 0),
    'all': int(os.environ.get('ALL_THREADS', os.cpu_count())),
}
THREADS['collect_reviews'] = THREADS['reviews']
THREADS['collect_products'] = THREADS['products']
THREADS['collect_departments'] = THREADS['departments']
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT') or 3306)
PROXY = os.environ.get('PROXY')
OPENVPN = os.environ.get('OPENVPN')
OPENVPN_LOGIN = os.environ.get('OPENVPN_LOGIN')
OPENVPN_PASSWORD = os.environ.get('OPENVPN_PASSWORD')
