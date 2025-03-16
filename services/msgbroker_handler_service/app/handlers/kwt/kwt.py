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

        sq = data['searchQuery']
        organic_count = data.get('co', 0)
        sponsored_count = data.get('cs', 0)
        data = data['chunk']
        new_data = []

        for item in data:
            if not item:
                continue
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
            item['date'] = datetime.datetime.fromisoformat(item['date'])
            new_data.append(item)

        if new_data:
            try:
                self.db['Keywords']['keyword_tracking_new'].insert_many(new_data, ordered=False)
            except (DuplicateKeyError, BulkWriteError):
                pass

        chan.basic_ack(deliver.delivery_tag)

    def handle_error(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        print(msg)
        chan.basic_ack(deliver.delivery_tag)


def setdefaultmany(obj, keys, func, default = None):
    for k in keys:
        obj[k] = func(obj[k]) if obj.get(k) else default
