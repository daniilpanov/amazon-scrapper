import time
from logging.handlers import TimedRotatingFileHandler

import requests
import logging

from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/100asinshandler.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def run(collection):
    print('Script started!')
    while True:
        time.sleep(5)  # low payload
        try:
            ready_bsrs = requests.get('http://server:8832/tasks/get_available/100asins?stage=2')
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError, requests.exceptions.RequestException):
            continue
        if ready_bsrs.status_code != 200:
            continue
        bsr_tasks = ready_bsrs.json()
        for task in bsr_tasks:
            if 'data' not in task or 'result' not in task:
                requests.patch('http://server:8832/tasks/report/' + task['_id'], json={
                    'stop': True,
                    'confirm': True,
                    'errors': [
                        'This task has no data or no result',
                    ],
                }, headers={
                    'Content-Type': 'application/json',
                })
                continue
            res = requests.post(
                'http://server:8832/tasks/acquire/' + task['script'] + '/' + task['header_id'] + '/' + task['_id'])
            if res.status_code == 409:
                continue

            data = task['data']
            result = task['result']
            collection_data = []
            query = (data['type'] + ' ' + data['label']).strip()

            for i in range(len(result)):
                collection_data.append({
                    'query': query,
                    'pos': i + 1,
                    **result[i],
                })

            try:
                collection.insert_many(collection_data, ordered=False)
            except DuplicateKeyError:
                pass
            except BulkWriteError:
                pass
            except Exception as e:
                requests.patch('http://server:8832/tasks/report/' + task['_id'], json={
                    'stop': True,
                    'confirm': True,
                    'errors': [str(e)],
                }, headers={
                    'Content-Type': 'application/json',
                })
                continue
            requests.patch('http://server:8832/tasks/finish/' + task['_id'])
            requests.post('http://server:8832/tasks/release/' + task['_id'])


if __name__ == '__main__':
    import certifi
    from os import environ as env
    from pymongo.server_api import ServerApi

    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
    # Create a new client and connect to the server_service
    with MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'), password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db:
        try:
            run(db[env.get('DB_GLOBAL_PREFIX', '') + 'Keywords'][env.get('COLLECTIONS_GLOBAL_PREFIX', '') + 'keyword_tracking_new'])
        finally:
            pass
