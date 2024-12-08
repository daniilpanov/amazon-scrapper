import certifi

from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from . import settings

client: MongoClient | None = None

config = {
    'url': settings.MONGO_DB_HOST,
    'username': settings.MONGO_DB_USER,
    'password': settings.MONGO_DB_PASS,
    'proxy': settings.MONGO_DB_PROXY,
    'url_prefix': settings.MONGO_DB_HOST_SCHEMA,
}


def set_config(**kwargs):
    global config
    for i in kwargs:
        config[i] = kwargs[i]


def init(username=None, password=None):
    global config
    from pymongo.server_api import ServerApi

    if not username:
        username = config.get('username')
    if not password:
        password = config.get('password')

    url = f"{config['url_prefix']}://{username}:{password}@{config['url']}"
    if 'proxy' in config and config['proxy']:
        import os
        os.environ['MONGO_PROXY'] = config['proxy']
    # Create a new client and connect to the server_service
    client = MongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where())
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return False
    return client


def inst() -> MongoClient | bool:
    global client
    if client:
        return client
    client = init(config['username'], config['password'])
    return client


def db(dbname: str) -> Database:
    return inst()[dbname]
