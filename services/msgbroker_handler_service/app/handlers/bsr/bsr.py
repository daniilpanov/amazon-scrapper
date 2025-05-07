import datetime
import json
import uuid

import pika.spec
import pytz
from bson import ObjectId
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import PERSISTENT_DELIVERY_MODE
from pymongo import MongoClient, UpdateOne, InsertOne
from pymongo.errors import BulkWriteError


class Handler:
    db: MongoClient

    def __init__(self, db):
        self.db = db
        self._categories_collection = self.db['amazon_dev']['cat_tmp2']
        self._product_categories_collection = self.db['amazon_dev']['product_categories2']
        self.handlers = {
            'result.success.bsr': {'handler': self.handle_success, 'arguments': {'prefetch-count': 6}},
            'result.error.bsr': {'handler': self.handle_error},
        }

    def handle_success(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        # parent_list, current, neighbours, products_data
        data = json.loads(msg.decode())
        tree = data.get('tree', [])
        current_bsr = data.get('currentBSR', None)
        start_new_tree_tasks = data.get('startNewTreeTasks', False)
        start_new_prod_tasks = data.get('startNewProdTasks', False)
        start_new_prod_tasks_with_reviews = data.get('startNewProdTasksWithReview', False)
        target_asins = data.get('targetAsins', [])
        products = data.get('ASINs', [])
        tree_items_chains = []
        last_level = None

        if not current_bsr:
            return chan.basic_ack(delivery_tag=deliver.delivery_tag)

        for item in reversed(tree):
            if item['level'] <= 0:
                break
            url_split = item['bsrLink'].split('/')
            item['domain'] = url_split[2].lstrip('www.')
            item['type'] = 'DEPARTMENT' if item['level'] < 2 else 'CATEGORY' if item['level'] < 3 else 'SUB'
            if url_split[-1][0] == '#':
                url_split = url_split[:-1]
            if url_split[-1].startswith('ref='):
                url_split = url_split[:-1]
            item['amazon_id'] = None
            for url_part in reversed(url_split[2:]):
                if url_part.isnumeric():
                    item['amazon_id'] = int(url_part)
            item['url'] = '/'.join(url_split)
            del item['bsrLink']
            item['name'] = item['bsrName']
            del item['bsrName']
            del item['index']

            if not last_level:
                last_level = item['level']
            if last_level == item['level']:
                item['level'] -= 1
                tree_items_chains.append([item])
            else:
                item['level'] -= 1
                for chain in tree_items_chains:
                    chain.append(item)

        needle_chain = None

        parsed_curr_bsr_url = current_bsr['bsrLink'].split('/')
        curr_domain = parsed_curr_bsr_url[2].lstrip('www.')
        if parsed_curr_bsr_url[-1][0] == '#':
            parsed_curr_bsr_url = parsed_curr_bsr_url[:-1]
        if parsed_curr_bsr_url[-1].startswith('ref='):
            parsed_curr_bsr_url = parsed_curr_bsr_url[:-1]
        curr_amazon_id = None
        for url_part in reversed(parsed_curr_bsr_url[2:]):
            if url_part.isnumeric():
                curr_amazon_id = int(url_part)
        if last_level == current_bsr['level']:
            for chain in tree_items_chains:
                item = chain[0]
                if item['domain'] == curr_domain and (item['amazon_id'] and item['amazon_id'] == curr_amazon_id or item['name'] == current_bsr['bsrName']):
                    needle_chain = chain
                    break
        else:
            needle_chain = tree_items_chains[0][1:]

        if not needle_chain:
            print(':-/')
            return chan.basic_nack(deliver.delivery_tag)

        skipped_items = []
        for chain_item in needle_chain:
            match_rules = {
                'amazon_id': chain_item['amazon_id'],
                'level': chain_item['level'],
                'domain': chain_item['domain'],
            }
            if not match_rules['amazon_id']:
                match_rules['name'] = chain_item['name']
            flat_tree_from_db = list(self._categories_collection.aggregate([
                {'$match': match_rules},
                {'$graphLookup': {
                    'from': self._categories_collection.name,
                    'startWith': '$parent',
                    'connectFromField': 'parent',
                    'connectToField': 'uuid',
                    'as': 'parent_chain',
                }},
                {'$addFields': {
                    'parent_chain': {
                        '$concatArrays': [
                            '$parent_chain',
                            [{
                                '_id': '$_id',
                                'name': '$name', 'level': '$level',
                                'uuid': '$uuid', 'parent': '$parent',
                                'amazon_id': '$amazon_id', 'type': '$type',
                                'url': '$url', 'domain': '$domain',
                            }]
                        ],
                    },
                }},
                {'$unwind': '$parent_chain'},
                {'$replaceRoot': {'newRoot': '$parent_chain'}},
                {'$sort': {'level': 1}},
            ]))
            if flat_tree_from_db:
                break
            skipped_items.append(chain_item)
        else:
            flat_tree_from_db = []

        skipped_items.reverse()
        needle_chain.reverse()
        last_uuid = None
        operations = []
        while len(flat_tree_from_db) or len(skipped_items):
            if len(skipped_items) and len(flat_tree_from_db):
                if skipped_items[0]['level'] < flat_tree_from_db[0]['level']:
                    item = skipped_items.pop(0)
                    db_item = None
                else:
                    db_item = flat_tree_from_db.pop(0)
                    item = needle_chain[db_item['level']] if db_item['level'] < len(needle_chain) else None
            elif len(skipped_items):
                item = skipped_items.pop(0)
                db_item = None
            else:
                db_item = flat_tree_from_db.pop(0)
                item = needle_chain[db_item['level']] if db_item['level'] < len(needle_chain) else None
            if db_item:
                if item:
                    changes = dict(set(item.items()) - set(db_item.items()))
                    item['parent'] = db_item['parent']
                    item['uuid'] = db_item['uuid']
                    if len(changes):
                        operations.append(UpdateOne({'_id': db_item['_id']}, {'$set': changes}))
                last_uuid = db_item['uuid']
            else:
                item['parent'] = last_uuid
                item['uuid'] = str(uuid.uuid4())
                operations.append(InsertOne(item))
                last_uuid = item['uuid']
        if operations:
            try:
                self._categories_collection.bulk_write(operations, ordered=False)
            except BulkWriteError:
                pass

        target_asins = set(target_asins)
        lost_asins = target_asins - set(prod['asin'] for prod in products)
        if lost_asins:
            products.extend({'asin': asin, 'rank': None} for asin in lost_asins)

        if products:
            self._product_categories_collection.delete_many({'category': needle_chain[-1]['uuid']})
            try:
                self._product_categories_collection.insert_many(({
                    'product_id': prod['asin'],
                    'category': needle_chain[-1]['uuid'],
                    'bsr_number': prod['rank'],
                    'product_source': 'AMAZON',
                } for prod in products), ordered=False)
            except BulkWriteError:
                pass

        if start_new_tree_tasks and last_level - 1 > needle_chain[-1]['level']:
            for item in reversed(tree):
                if item['level'] < last_level - 1:
                    break
                chan.basic_publish('tasks', 'bsr', json.dumps({
                    'BSR_URL': item['url'],
                    'startNewTreeTasks': True,
                    'startNewProdTasks': start_new_prod_tasks,
                    'startNewProdTasksWithReview': start_new_prod_tasks_with_reviews,
                    'targetAsins': list(target_asins),
                }).encode(), BasicProperties(delivery_mode=PERSISTENT_DELIVERY_MODE))

        if start_new_prod_tasks and products:
            header_res = self.db['scrap_process']['tasks_headers'].insert_one({
                'script': 'products',
                'visible': True,
                'created_at': datetime.datetime.now(pytz.UTC),
                'started_at': None,
                'ended_at': None,
                'alias': needle_chain[-1]['name'] + ' Scrap',
            })
            tasks = []
            for prod in products:
                is_target = prod['asin'] in target_asins
                tasks.append({
                    'script': 'products',
                    'header_id': ObjectId(header_res.inserted_id),
                    'data': {
                        'asin': prod['asin'],
                        'keywords': '',
                        'current_format': True,
                        'collect_aspects': True,
                        'collect_media_config': is_target,
                        'target': is_target,
                        'domain': needle_chain[-1]['domain'],
                    },
                    'status': 0,
                    'confirmed_status': 0,
                    'stage': int(start_new_prod_tasks_with_reviews),
                    'errors': [],
                    'created_at': datetime.datetime.now(pytz.UTC),
                    'started_at': None,
                    'ended_at': None,
                    'result': {},
                })
            self.db['scrap_process']['tasks_bodies'].insert_many(tasks)

        chan.basic_ack(deliver.delivery_tag)

    def handle_error(self, chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, props, msg):
        print(msg)
        chan.basic_ack(deliver.delivery_tag)
