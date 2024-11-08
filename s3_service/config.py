from os import environ as env
from dotenv import load_dotenv
load_dotenv('.env')

ACCESS_KEY = env.get('ACCESS_KEY')
SECRET_KEY = env.get('SECRET_KEY')
BASE_BUCKET = env.get('BASE_BUCKET')
PORT = int(env.get('PORT', 80))
