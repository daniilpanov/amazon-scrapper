import inspect
import os
from os import environ as env
import importlib
import pkgutil

import certifi
import pika
from pymongo import MongoClient
from pymongo.server_api import ServerApi

import handlers

url = os.environ.get('MONGO_DB_HOST_SCHEMA', 'mongodb') + '://'
username = None
password = None
if 'MONGO_DB_USER' in os.environ:
    username = os.environ['MONGO_DB_USER']
    url += username
    if 'MONGO_DB_PASS' in os.environ:
        password = os.environ['MONGO_DB_PASS']
        url += ':' + password
    url += '@'
url += os.environ.get('MONGO_DB_HOST', 'localhost')

with (pika.BlockingConnection(pika.ConnectionParameters(env.get('RABBITMQ_HOST', 'localhost'))) as msgbroker,
    MongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where()) as db):

    channel = msgbroker.channel()

    for handler in pkgutil.iter_modules(handlers.__path__):
        module_path = 'handlers.' + handler.name + '.' + handler.name
        try:
            module = importlib.import_module(module_path)
            params = set(map(lambda i: i[0], inspect.getmembers(module)))
            if 'Handler' not in params:
                continue
        except ModuleNotFoundError as e:
            print(e)
            print('Module not found:', module_path)
            continue
        except AttributeError as e:
            print('Module', module_path, 'has no attribute:', e)
            continue
        for path, conf in module.Handler(db).handlers.items():
            channel.basic_consume(path, conf['handler'], auto_ack=conf.get('auto_ack', False), consumer_tag=conf['handler'].__doc__ or None, arguments={'prefetch-count': 10} | conf.get('arguments', {}))

    channel.start_consuming()
