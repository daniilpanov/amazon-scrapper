import dotenv
import os

if not dotenv.load_dotenv('.env'):
    dotenv.load_dotenv('../.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')
# POWER LIMITS (active browsers quantity depending on sum of these numbers)
THREADS = {
    'reviews': int(os.environ.get('REVIEWS_THREADS', os.cpu_count())),
    'products': int(os.environ.get('PRODUCTS_THREADS', os.cpu_count())),
    'departments': int(os.environ.get('DEPARTMENTS_THREADS', os.cpu_count())),
    'all': int(os.environ.get('ALL_THREADS', os.cpu_count())),
}
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT') or 3306)
PROXY = os.environ.get('PROXY')
