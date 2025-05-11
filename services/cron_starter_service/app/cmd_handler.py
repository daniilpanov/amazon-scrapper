#!/usr/bin/env python
from logging import StreamHandler

from run_keyword import run_keyword
from run_spfd import run_spfd

actions = {
    'KW': run_keyword,
    'SPFD': run_spfd,
}

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Run the autostart scripts by cron', add_help=True)
    parser.add_argument('-s', '--script', choices=actions.keys(), help='The script name to run')
    parser.add_argument('-p', '--params', help='The script execution params', default=None)
    args = parser.parse_args()

    func_args = {}
    if args.params:
        items = args.params.split(';')
        for item in items:
            k, v = item.strip().split('=')
            func_args[k] = v

    import logging
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Create a handler that logs to the Docker logs
    handler = StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.info(args)

    import importlib.util
    if importlib.util.find_spec('dotenv'):
        from dotenv import load_dotenv
        load_dotenv('.env') or load_dotenv('../.env') or load_dotenv('../../.env') or load_dotenv('../../../.env')
    
    from inspect import signature
    from contextlib import ExitStack
    
    import pika
    from pymongo import MongoClient
    from os import environ as env
    import certifi
    from pymongo.server_api import ServerApi
    
    func = actions[args.script]
    params = signature(func).parameters.items()
    kwargs = {}
    
    with ExitStack() as es:
        for name, sign in params:
            if sign.annotation is MongoClient:
                url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
                client = MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'),
                     password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where())
                es.enter_context(client)
                kwargs[name] = client
            elif sign.annotation is pika.BlockingConnection:
                try:
                    client = pika.BlockingConnection(pika.ConnectionParameters(env.get('RABBITMQ_HOST', 'localhost')))
                except:
                    client = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                es.enter_context(client)
                kwargs[name] = client
        func(**(kwargs | func_args))
