import datetime
import json

with open('resultKWT.json', encoding='UTF-8') as f:
    data = json.loads(f.read())

sq = input('Enter the search query: ')
new_data = []


def setdefaultmany(obj, keys, func, default = None):
    for k in keys:
        obj[k] = func(obj[k]) if obj.get(k) else default


organic_count = 0
sponsored_count = 0

for item in filter(lambda i: i, data):
    item['searchQuery'] = sq
    setdefaultmany(item, ('score', 'price', 'itemPrice', 'oldPrice', 'subscriptionDiscount', 'subscriptionDiscountPercents'), float)
    setdefaultmany(item, ('BestSellerIn', 'image', 'title', 'asin'), str, None)
    item['sponsored_rank'] = None
    item['organic_rank'] = None
    if item.get('isSponsored'):
        sponsored_count += 1
        item['sponsored_rank'] = sponsored_count
    else:
        organic_count += 1
        item['organic_rank'] = organic_count
    del item['isSponsored']
    # print(item)
    new_data.append(item)

with open('reskwt.json', 'w', encoding='UTF-8') as f:
    f.write(json.dumps(new_data))

if int(input('Need load this data to database? [1 - yes, 0 - no]')):
    from dotenv import load_dotenv
    load_dotenv() or load_dotenv('.env') or load_dotenv('../.env')
    from os import environ as env
    import certifi
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi

    new_optimized_data = []

    for item in new_data:
        item['date'] = datetime.datetime.fromisoformat(item['date'])
        new_optimized_data.append(item)

    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
    with MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'), password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db_inst:
        db_inst['Keywords']['keyword_tracking_new'].insert_many(new_optimized_data)
