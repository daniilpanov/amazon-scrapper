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
            'result.success.kwt': {'handler': self.handle_success},
            'result.error.kwt': {'handler': self.handle_error},
        }

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
        else:
            try:
                data['id'] = entity_id
                data['scrap_date'] = date
                self.db['Kalodata_new'][entity].insert_one(data)
            except (DuplicateKeyError, BulkWriteError):
                pass

        chan.basic_ack(deliver.delivery_tag)

    def handle_error(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        print(msg)
        chan.basic_ack(deliver.delivery_tag)
