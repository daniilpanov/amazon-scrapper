import datetime
import time

import pytz
import requests
from bson import ObjectId
from pymongo.errors import BulkWriteError

import db_mongo
import tasks_manager

results_collection = db_mongo.db('amazon_data')['product_targeting']
asins_collection = db_mongo.db('amazon_data')['product_card']


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def run():
    print('Script started!')
    while True:
        time.sleep(5)  # low payload
        try:
            ready_100asins = requests.get('http://localhost:8832/tasks/get_available/100asins?stage=2')
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError, requests.exceptions.RequestException):
            continue
        if ready_100asins.status_code != 200:
            continue
        bsr_tasks = ready_100asins.json()
        for task in bsr_tasks:
            res = requests.post(
                'http://localhost:8832/tasks/acquire/' + task['script'] + '/' + task['header_id'] + '/' + task['_id'])
            if res.status_code == 409:
                continue
            asins = set(task['result'])
            cards = []
            duplicated_rows = []
            new_data = []
            for asins_chunk in chunks(asins, 25):
                finding_condition = {'asin': {'$in': asins_chunk}}
                duplicated_rows.extend(results_collection.find(finding_condition))
                cards.extend(asins_collection.find(finding_condition))
            for row in duplicated_rows:
                row['reference'] = task['reference']
                new_data.append(row)
                asins.remove(row['asin'])
            for card in cards:
                new_data.append({
                    'reference': task['reference'],
                    'asin': card['asin'],
                    'title': card['product_title'],
                    'description': card['product_descr'],
                })
                asins.remove(card['asin'])
            if new_data:
                try:
                    results_collection.insert_many(new_data, ordered=False)
                except BulkWriteError:
                    pass
            task_id = ObjectId(task['_id'])
            tasks_manager.TasksBodies.update_one({'_id': task_id}, {'$set': {'asins_count': len(asins)}})
            for asin in asins:
                res = requests.post('http://localhost:8832/product-targeting/start/item', json={
                    'root_task_id': str(task['_id']),
                    'query': task['label'],
                    'reference': task.get('reference'),
                    'asin': asin,
                }, headers={
                    'Content-Type': 'application/json',
                })
                if res.status_code != 200:
                    print('ASIN', asin, 'dropped with error', res.status_code, ':', res.text)
                    tasks_manager.report_task(
                        task_id,
                        [datetime.datetime.now(pytz.UTC).isoformat() + ' [PT] ' + str(res.status_code) + ': ' + res.text],
                        stop=True,
                        confirm=True,
                    )
                    break


if __name__ == '__main__':
    run()
