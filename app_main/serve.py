import logging
import os
from functools import wraps
from os import environ as env
import importlib
import pkgutil

import certifi
import pika
from concurrent.futures import ThreadPoolExecutor
from pika.adapters.blocking_connection import BlockingChannel
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from app import handlers
from app.handlers.abstract_handler import AbstractHandler

from app.startup import startup

logger = logging.getLogger("msgbroker_handler")

log_level = os.getenv("MSGBROKER_HANDLER_LOG_LEVEL", "INFO")
if isinstance(log_level, str):
    log_level = logging.getLevelName(log_level)
    if isinstance(log_level, str):
        log_level = logging.INFO

logger.setLevel(log_level)
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(log_handler)

# Call 'on startup'
startup(logger)


def handler_wrapper(handler_cls, method, config, *args, **kwargs):
    @wraps(method)
    def wrapper(chan: BlockingChannel, deliver: pika.spec.Basic.Deliver, _, msg):
        try:
            if 'validator' in config:
                msg = config['validator'](msg)
            elif 'array_validator' in config:
                msg = config['array_validator'](msg)

            instance = handler_cls(chan, msg, *args, **kwargs)
            res = method(instance)

            if res is None or res:
                chan.basic_ack(deliver.delivery_tag)
            else:
                chan.basic_reject(deliver.delivery_tag, requeue=True)
        except Exception as e:
            logger.exception(e)
            chan.basic_reject(deliver.delivery_tag, requeue=False)

    return wrapper


def build_mongo_config():
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
    return {'url': url, 'username': username, 'password': password}


def start_consumer(handler: type[AbstractHandler]):
    with (
        get_pika() as broker,
        get_mongo(**build_mongo_config()) as db,
    ):
        chan = broker.channel()
        chan.basic_qos(prefetch_count=handler.get_prefetch_count())
        for queue, conf in handler.get_handlers().items():
            logger.info('MSG Handler module loaded: ' + queue)
            chan.basic_consume(
                queue,
                handler_wrapper(handler, conf['handler'], conf, db, logger),
                auto_ack=conf.get('auto_ack', False),
                arguments=conf.get('arguments')
            )
        chan.start_consuming()


def get_pika():
    return pika.BlockingConnection(pika.ConnectionParameters(env.get('RABBITMQ_HOST', 'localhost'), heartbeat=1800))


def get_mongo(url, username, password):
    return MongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where())


def run():
    with (ThreadPoolExecutor() as executor):
        futures = []

        for handler in pkgutil.iter_modules(handlers.__path__):
            module_path = 'app.handlers.' + handler.name + '.main'
            try:
                module = importlib.import_module(module_path)
                if not getattr(module, 'handler', None):
                    continue
            except ModuleNotFoundError as e:
                logger.error('Module not found: ' + module_path + ' [error: ' + str(e) + ']')
                continue
            except AttributeError as e:
                logger.error('Module ' + module_path + ' has no attribute: ' + str(e))
                continue

            logger.info('Handler module loaded: ' + module_path)
            futures.append(executor.submit(
                start_consumer,
                module.handler,
            ))

        for future in futures:
            future.result()


if __name__ == '__main__':
    run()
