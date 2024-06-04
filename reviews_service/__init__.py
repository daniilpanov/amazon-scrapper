import requests

import parser
from . import get_reviews_by_selenium
from . import get_reviews_by_requests


def do_task(task):
    requests.post(
        'http://localhost:8832/tasks/acquire/products/' + task['header_id']['$oid'] + '/' + task['_id']['$oid'])
    try:
        res = get_reviews_by_requests.load_reviews(task['data']['asin'], task['data'].get('keywords', ''), task['data'].get('domain', 'amazon.com'), task['data'].get('index', 0), task['data'].get('current_format', True))
        if 'error' in res:
            res = get_reviews_by_selenium.load_reviews(task['data']['asin'], task['data'].get('keywords', ''), task['data'].get('domain', 'amazon.com'), task['data'].get('index', 0), task['data'].get('current_format', True))
        if 'error' in res:
            requests.patch('http://localhost:8832/tasks/report/' + task['_id']['$oid'], json={
                'confirm': True,
                'stop': True,
                'errors': [
                    '[' + task['data']['asin'] + '] ' + res['error'],
                ],
            })
            return
        requests.patch('http://localhost:8832/tasks/finish/' + task['_id']['$oid'], json={
            'confirm': True,
        })
    except Exception as e:
        requests.patch('http://localhost:8832/tasks/report/' + task['_id']['$oid'], json={
            'confirm': True,
            'stop': True,
            'errors': [
                '[' + task['data']['asin'] + '] ' + str(e),
            ],
        })
        raise e


def run():
    try:
        while True:
            tasks = requests.get('http://localhost:8832/tasks/get_available/products?stage=2').json()
            for task in tasks:
                do_task(task)
            tasks = requests.get('http://localhost:8832/tasks/get_available/reviews?stage=0').json()
            for task in tasks:
                do_task(task)
    except KeyboardInterrupt:
        get_reviews_by_selenium.close()
        raise


if __name__ == '__main__':
    run()
