import time

import requests

import parser
from . import get_data_by_requests, get_data_by_selenium


def do_task(task):
    requests.post('http://localhost:8832/tasks/acquire/products/' + task['header_id'] + '/' + task['_id'])
    try:
        asin = task['data']['asin']
        domain = task['data']['domain']
        html = get_data_by_requests.get_html_by_request(asin, domain=domain)
        if not html:
            html = get_data_by_selenium.get_html_by_selenium(asin, domain=domain)
        data = parser.parse_product(asin, html, domain=domain)
        if not data:
            print('NO DATA: ' + task['data']['asin'])
            requests.patch('http://localhost:8832/tasks/report/' + task['_id'], json={
                'confirm': True,
                'stop': True,
                'errors': [
                    'No data: asin ' + task['data']['asin'],
                    ],
            })
            return False
        json_data = dict(zip(('asin', 'product_url', 'canonical_link', 'product_title', 'product_descr', 'picture_url', 'parse_datetime', 'features', 'top_5_phrases', 'product_price'), data))
        json_data['parse_datetime'] = json_data['parse_datetime'].isoformat()
        if json_data.get('aspects_collect'):
            aspects = parser.parse_aspects(asin, html)
            if aspects:
                aspects = [dict(zip(('Aspect', 'positive', 'negative'), aspect)) for aspect in aspects]
                requests.post('http://localhost:8832/products/set_result/aspects/' + asin, json=aspects)

        if json_data.get('media_collect'):
            media_data = parser.parse_media_links(html)
            if media_data:
                json_data['media_data'] = media_data
        else:
            media_data = None
        requests.post('http://localhost:8832/products/set_result/card/' + asin, json=json_data)

        if media_data and json_data.get('target_task_create'):
            requests.post('http://localhost:8832/products/target/collect/' + asin)
        print('json data made')
        requests.post('http://localhost:8832/products/set_result/card/' + task['data']['asin'], json=json_data)
        requests.patch('http://localhost:8832/tasks/stage/' + task['_id'], json={
            'release': True,
            'stage': 2 if task.get('stage', 0) > 0 else 0,
        })
        # requests.patch('http://localhost:8832/tasks/finish/' + task['_id'], json={
        #     'confirm': True,
        # })
    except Exception as e:
        requests.patch('http://localhost:8832/tasks/report/' + task['_id'], json={
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
            tasks = requests.get('http://localhost:8832/tasks/get_available/products?stage=1').json()
            print('1', tasks)
            for task in tasks:
                do_task(task)
            tasks = requests.get('http://localhost:8832/tasks/get_available/products?stage=0').json()
            print('0', tasks)
            for task in tasks:
                do_task(task)
            time.sleep(5)
    except KeyboardInterrupt:
        get_data_by_selenium.close()
        raise


if __name__ == '__main__':
    run()
