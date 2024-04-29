import certifi

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
    'proxy': 'http://proxydb:StdInp0101@95.216.25.100:3128',
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
    # Create a new client and connect to the server_module
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
    except (BulkWriteError, DuplicateKeyError):
        return True


def write_aspects(asin, aspects):
    data = []
    for aspect in aspects:
        data.append({'ASIN': asin, 'Aspect': aspect[0], 'positive': aspect[1], 'negative': aspect[2]})
    try:
        return db()['amazon_aspects'].insert_many(data, False)
    except (BulkWriteError, DuplicateKeyError):
        return True


if __name__ == '__main__':
    dab = db('amazon_data')
    dab['categories'].find()	
    # dab['categories_all'].delete_many({})
    #
    # def d(group, cat=None):
    #     r = DataFrame(list(dab[cat or ('categories_for_' + group)].find()))
    #     r['relation_to_category'] = group
    #     return r
    #
    # groups = [c[15:] for c in dab.list_collection_names() if c.startswith('categories_for_')]
    # df = pandas.concat([
    #     DataFrame(columns=['Category', 'ASIN', 'relation_to_category', 'relation_to_TOP5']),
    #     *(d(group) for group in groups),
    #     d('1', 'categories'),
    # ], ignore_index=True).drop_duplicates('ASIN').drop('_id', axis=1)
    # df['relation_to_TOP5'] = False
    # dab['categories_all'].insert_many(list(df.T.to_dict().values()))
