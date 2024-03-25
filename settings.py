import dotenv
import os

dotenv.load_dotenv('.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')
# POWER LIMITS (active browsers quantity depending on sum of these numbers)
THREADS = {
    'reviews': int(os.environ.get('REVIEWS_THREADS', os.cpu_count())),
    'products': int(os.environ.get('PRODUCTS_THREADS', os.cpu_count())),
    'departments': int(os.environ.get('DEPARTMENTS_THREADS', os.cpu_count())),
    'all': int(os.environ.get('ALL_THREADS', os.cpu_count())),
}
