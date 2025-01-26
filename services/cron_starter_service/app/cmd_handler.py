#!/usr/bin/env python
from run_keyword import run_keyword

actions = {
    'KW': run_keyword,
}

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Run the autostart scripts by cron', add_help=True)
    parser.add_argument('-s', '--script', choices=actions.keys(), help='The script name to run')
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv('.env') or load_dotenv('../.env') or load_dotenv('../../.env') or load_dotenv('../../../.env')
    from pymongo import MongoClient
    from os import environ as env
    import certifi
    from pymongo.server_api import ServerApi

    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
    # Create a new client and connect to the server_service
    with MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'),
                     password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db:
        actions[args.script](db)
