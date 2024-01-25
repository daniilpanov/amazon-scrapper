import dotenv
import os

dotenv.load_dotenv('.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'product')
