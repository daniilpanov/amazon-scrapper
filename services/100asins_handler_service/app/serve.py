import time
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import quote

import requests
import logging

from future.backports.email.feedparser import headerRE
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
            query = data['type'] + ' ' + data['query']

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
            else:
                requests.patch('http://server:8832/tasks/finish/' + task['_id'])
                requests.post('http://server:8832/tasks/release/' + task['_id'])


if __name__ == '__main__':
    with MongoClient() as db:
        try:
            run(db['Keywords']['keyword_tracking_new'])
        finally:
            pass
