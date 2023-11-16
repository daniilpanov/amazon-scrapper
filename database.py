import datetime

import pytz
from pymongo.database import Database
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo.mongo_client import MongoClient

client: MongoClient | None = None

config = {
    'url': 'cluster0.tcwqk03.mongodb.net/?retryWrites=true&w=majority',
    'username': 'scrape_processing',
    'database': 'amazon_data',
    'keepa_database': 'keepa',
    'password': 'gxYSEvBIDTgy6RIg',
    'proxy': 'http://Daniel:OsdKey0909@46.19.33.214:3128',
    'url_prefix': 'mongodb+srv',
}


def set_config(**kwargs):
    global config
    for i in kwargs:
        config[i] = kwargs[i]


def inst() -> MongoClient | bool:
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


def keepa_db() -> Database:
    return inst()[config['keepa_database']]


def write_reviews(reviews):
    revs = []
    for i, row in reviews.iterrows():
        revs.append({
            'asin': row['asin'],
            'product_url': row['product_url'],
            'date': datetime.datetime.strptime(row['date'], '%B %d %Y'),
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


def write_product_html(asin, html):
    try:
        return db()['raw_product_card_htmls'].insert_one({
            'asin': asin, 'product_url': f'https://amazon.com/dp/{asin}',
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


def write_keepa_html(asin, keepa_ph, keepa_stats, keepa_comparing, keepa_data):
    try:
        return keepa_db()['raw_htmls'].insert_one({
            'asin': asin,
            'keepa_price_history': keepa_ph,
            'keepa_statistics': keepa_stats,
            'keepa_comparing': keepa_comparing,
            'keepa_data': keepa_data,
            'scrap_datetime': datetime.datetime.now(pytz.UTC),
        })
    except (BulkWriteError, DuplicateKeyError) as e:
        return True


if __name__ == '__main__':
    print(db().list_collection_names())
    # print(db()['customer_reviews'].find().next())
    # print(db()['product_card'].delete_many({}))
    # print(db()['raw_product_card_htmls'].delete_many({}))
    print(db()['product_card'].find().next())
    print(db()['raw_product_card_htmls'].find().next()['asin'])
    # print(keepa_db()['raw_htmls'].find().next())

