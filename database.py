import datetime
import os
import re
from json import JSONDecoder
import pandas as pd
import certifi

import pytz
from pymongo.database import Database
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo.mongo_client import MongoClient

client: MongoClient | None = None
client_spec: MongoClient | None = None

config = {
    'url': 'cluster0.tcwqk03.mongodb.net/?retryWrites=true&w=majority',
    'username': 'scrape_processing',
    'database': 'amazon_data',
    'password': 'gxYSEvBIDTgy6RIg',
    'proxy': 'http://proxydb:StdInp0101@185.234.247.250:3128',
    'url_prefix': 'mongodb+srv',
}
config_special = {'username': 'ai_operator', 'password': 'jEWVWuNrgrqTkn7w'}


def set_config(**kwargs):
    global config
    for i in kwargs:
        config[i] = kwargs[i]


def init(username, password):
    global config
    from pymongo.server_api import ServerApi

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


def spec_inst():
    global client_spec
    if client_spec:
        return client_spec
    client_spec = init(**config_special)
    return client_spec


def spec_db(dbname=None) -> Database:
    return spec_inst()[dbname or config['database']]


def db(dbname=None) -> Database:
    return inst()[dbname or config['database']]


def write_reviews(reviews):
    revs = []
    for i, row in reviews.iterrows():
        revs.append({
            'asin': row['asin'],
            'product_url': row['product_url'],
            'date': row['date'],
            'country': row['country'],
            'name': row['name'],
            'title': row['title'],
            'description': row['content'],
            'rating': row['rating'],
            'helpful': row['helpful'],
            'options': row['options'],
            'review_id': row['review_id'],
            'scrap_datetime': row['scrap_datetime'],
        })
    if not revs:
        return False
    try:
        return db()['customer_reviews'].insert_many(revs, ordered=False)
    except (BulkWriteError, DuplicateKeyError) as e:
        return True


def write_product_html(asin, html, domain='amazon.com'):
    try:
        return db()['raw_product_card_htmls'].insert_one({
            'asin': asin, 'product_url': f'https://{domain}/dp/{asin}',
            'HTML_text': html,
            'scrap_datetime': datetime.datetime.now(pytz.UTC),
        })
    except (BulkWriteError, DuplicateKeyError) as e:
        return True


def write_product_parsed(asin, product_url, title, descr, picture_url, parse_datetime, features, top5phr, price):
    try:
        return db()['product_card'].insert_one({
            'asin': asin,
            'product_url': product_url,
            'product_title': title,
            'product_descr': descr,
            'picture_url': picture_url,
            'parse_datetime': parse_datetime,
            'features': features,
            'top_5_phrases': top5phr,
            'product_price': price,
        })
    except (BulkWriteError, DuplicateKeyError) as e:
        return True


if __name__ == '__main__':
    ...

