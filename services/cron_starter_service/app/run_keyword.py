from itertools import chain
from os import environ as env

from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from tasks_api import TasksGroup


def get_data_iterator(col: Collection):
    yield from col.distinct('search_query')


def run_keyword(conn: MongoClient):
    group = TasksGroup(conn, '100asins', 1, type='', limit=env.get('KEYWORD_PAGES_LIMIT', 10),
                       domain=env.get('AMZ_DOMAIN', 'amazon.com'))

    for query in chain(get_data_iterator(conn['amazon_reports']['search_query_brand']),
                       get_data_iterator(conn['amazon_reports_dev']['search_query_brand'])):
        group.add_task(label=query)

    group.create_group(f'KW.daily({group.dt.isoformat()})')
    print(group.group_id)
    print(group.submit_tasks())


if __name__ == '__main__':
    from dotenv import load_dotenv

    print(load_dotenv('.env') or load_dotenv('../.env') or load_dotenv('../../.env') or load_dotenv('../../../.env'))
    import certifi
    from pymongo.server_api import ServerApi

    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
    # Create a new client and connect to the server_service
    with MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'),
                     password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db:
        run_keyword(db)
