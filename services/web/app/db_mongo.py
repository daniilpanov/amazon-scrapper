import certifi

from pymongo.database import Database
from pymongo.errors import BulkWriteError, DuplicateKeyError
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
    # Create a new client and connect to the server
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


def write_product_parsed(asin, product_url, canonical_link, title, descr, picture_url, features, top5phr, price):
    try:
        return db('amazon_data')['product_card'].replace_one({'asin': asin}, {
            'asin': asin,
            'product_url': product_url,
            'canonical_link': canonical_link,
            'product_title': title,
            'product_descr': descr,
            'picture_url': picture_url,
            'features': features,
            'top_5_phrases': top5phr,
            'product_price': price,
        }, upsert=True)
    except (BulkWriteError, DuplicateKeyError):
        return True


def write_aspects(asin, aspects):
    data = []
    for aspect in aspects:
        data.append({'ASIN': asin, 'Aspect': aspect[0], 'positive': aspect[1], 'negative': aspect[2]})
    try:
        return db('amazon_data')['amazon_aspects'].insert_many(data, False)
    except (BulkWriteError, DuplicateKeyError):
        return True
