from itertools import chain
from os import environ as env

import pika
from pika import BasicProperties
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection


def get_data_iterator(col: Collection):
    yield from col.distinct('search_query')


def run_keyword(conn: MongoClient, rabbit: pika.BlockingConnection):
    sqs = set()
    with rabbit.channel() as chan:
        for query in chain(get_data_iterator(conn['amazon_reports']['search_query_brand']),
                           get_data_iterator(conn['amazon_reports_dev']['search_query_brand'])):
            sqs.add(query)
        for sq in sqs:
            chan.basic_publish('tasks', 'kwt', ('{"destination": "remote", "searchQuery": "' + sq + '", "timeLimit": 120000}').encode(), BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
