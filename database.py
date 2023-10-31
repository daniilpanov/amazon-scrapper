from typing import Union
import datetime

import pytz
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

client: Union[MongoClient, None] = None

config = {
    'url': 'cluster0.tcwqk03.mongodb.net/?retryWrites=true&w=majority',
    'username': 'scrape_processing',
    'database': 'amazon_data',
    'password': 'gxYSEvBIDTgy6RIg',
    'proxy': 'http://Daniel:OsdKey0909@46.19.33.214:3128',
    'url_prefix': 'mongodb+srv',
}


def set_config(**kwargs):
    global config
    for i in kwargs:
        config[i] = kwargs[i]


def inst() -> Union[MongoClient, False]:
    global client
    if client:
        return client

    global config
    from pymongo.server_api import ServerApi

    url = f"{config['url_prefix']}://{config['username']}:{config['password']}@{config['url']}"
    if 'proxy' in config and config['proxy']:
        import os
        os.environ['MONGO_PROXY'] = config['proxy']
    # Create a new client and connect to the server
    client = MongoClient(url, server_api=ServerApi('1'), username=config['username'], password=config['password'])
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return False
    return client


def db() -> Database:
    return inst()[config['database']]


def write_reviews(reviews):
    return db()['customer_reviews'].insert_many(reviews)


def write_product_html(asin, html, keepa_ph, keepa_stats, keepa_comparing, keepa_data):
    res1 = db()['raw_product_card_htmls'].insert_one({
        'asin': asin, 'product_url': f'https://amazon.com/dp/{asin}',
        'HTML_text': html,
        'scrap_datetime': datetime.datetime.now(pytz.UTC),
    })
    res2 = db()['raw_product_card_htmls'].insert_one({
        'asin': asin, 'keepa price history': keepa_ph,
        'keepa statistics': keepa_stats,
        'keepa comparing': keepa_comparing,
        'keepa data': keepa_data,
    })


if __name__ == '__main__':
    print(db().list_collection_names())
    print(db()['customer_reviews'].find().next())
