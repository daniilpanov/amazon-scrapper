import datetime
import json

import pika.spec
from pika.adapters.blocking_connection import BlockingChannel
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError


class Handler:
    db: MongoClient

    def __init__(self, db):
        self.db = db
        self.handlers = {
            'result.success.kalodata': {'handler': self.handle_success},
            'result.error.kalodata': {'handler': self.handle_error},
        }

    def start_chained_list(self, chan, data, entity):
        for item in data:
            chan.basic_publish('tasks', 'kalodata', ('{"destination": "remote", "id": ' + str(item['id']) + ', "entity": "' + entity + '"}').encode(), pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))

    def start_chained_entities(self, chan, data, entity):
        mapping = {
            'product': {'searchProducts', 'products', 'product', 'searchNewProducts'},
            'video': {'video', 'similarVideos'},
            'creator': {'creator', 'searchCooperativeCreators'},
            'shop': {'shop', 'searchShopList', 'searchCooperativeShops'},
        }
        if entity == 'shop':
            needle = {'product': mapping['product']}
        elif entity == 'product':
            needle = {'video': mapping['video'], 'shop': mapping['shop']}
        elif entity == 'video':
            needle = {'creator': mapping['creator']}
        else:
            needle = {}
        for name, keys in needle.items():
            for key in keys:
                for item in data.get(key, []):
                    print('tasks', 'kalodata', ('{"destination": "remote", "id": ' + str(item['id']) + ', "entity": "' + name + '"}').encode())
                    chan.basic_publish('tasks', 'kalodata', ('{"destination": "remote", "id": ' + str(item['id']) + ', "entity": "' + name + '"}').encode(), pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
        if entity == 'video':
            print('tasks', 'kalodata', ('{"destination": "remote", "id": ' + str(data['details']['creator_id']) + ', "entity": "creator"}').encode())
            chan.basic_publish('tasks', 'kalodata', ('{"destination": "remote", "id": ' + str(data['details']['creator_id']) + ', "entity": "creator"}').encode(), pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))

    def handle_success(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        data = json.loads(msg.decode())
        entity = data.get('entity')
        entity_id = data.get('entity_id')
        is_list = data.get('is_list', False)
        query = data.get('query')
        data = data.get('data')
        date = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time())
        if is_list:
            try:
                self.db['Kalodata_new'][entity + 'List'].insert_many([{**item, 'search_query': query, 'scrap_date': date} for item in data], ordered=False)
            except (DuplicateKeyError, BulkWriteError):
                pass
            self.start_chained_list(chan, data, entity)
        else:
            try:
                data['id'] = entity_id
                data['scrap_date'] = date
                self.db['Kalodata_new'][entity].insert_one(data)
            except (DuplicateKeyError, BulkWriteError):
                pass
            self.start_chained_entities(chan, data, entity)

        chan.basic_ack(deliver.delivery_tag)

    def handle_error(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        print(msg)
        chan.basic_ack(deliver.delivery_tag)
