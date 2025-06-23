import json
from itertools import chain

import pika
from pika import BasicProperties
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection


def get_data_iterator(col: Collection):
    yield from col.aggregate([
        { '$sort': { 'search_query': 1, 'date': -1 } },
        {
            '$group': {
                '_id': '$search_query',
                'search_query_volume': { '$max': '$search_query_volume' },
                'asin': { '$addToSet': '$asin' },
            },
        },
        { '$sort': { 'search_query_volume': -1 } },
        {
            '$project': {
                '_id': 0,
                'search_query': '$_id',
                'search_query_volume': 1,
                'asin': 1,
            },
        },
    ])


def run_keyword(conn: MongoClient, rabbit: pika.BlockingConnection):
    sqs = set()
    items = []
    with (rabbit.channel() as chan):
        for query in chain(get_data_iterator(conn['amazon_reports']['search_query_asin']),
                           get_data_iterator(conn['amazon_reports_dev']['search_query_asin']),
                           get_data_iterator(conn['amazon_reports']['search_query_brand']),
                           get_data_iterator(conn['amazon_reports_dev']['search_query_brand'])):
            old_l = len(sqs)
            sqs.add(query['search_query'])
            if len(sqs) > old_l:
                items.append(query)
        del sqs
        items.sort(key=lambda i: i['search_query_volume'], reverse=True)
        for sq in items:
            msg = json.dumps({
                "destination": "remote",
                "searchQuery": sq['search_query'],
                "timeLimit": 120000,
            } if sq.get('asin') else {
                "destination": "remote",
                "searchQuery": sq['search_query'],
                "timeLimit": 120000,
                "asins": sq['asin'],
            })
            chan.basic_publish(
                'tasks', 'kwt', msg.encode(),
                BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
            )
