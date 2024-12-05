import time

import requests
import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def run():
    print('Script started!')
    while True:
        time.sleep(5)  # low payload
        try:
            ready_bsrs = requests.get('http://server:8832/tasks/get_available/bsr?stage=2')
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError, requests.exceptions.RequestException):
            continue
        if ready_bsrs.status_code != 200:
            continue
        bsr_tasks = ready_bsrs.json()
        for task in bsr_tasks:
            if 'data' not in task or 'result' not in task:
                continue  # TODO: make report
            res = requests.post(
                'http://server:8832/tasks/acquire/' + task['script'] + '/' + task['header_id'] + '/' + task['_id'])
            if res.status_code == 409:
                continue
            asins = task['result'].get('asins', [])
            str_asins = [p['asin'] for p in asins[:5]]
            if task['data'].get('category'):
                requests.post(
                    'http://server:8832/cmd/category/set',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json={
                        'asins': str_asins,
                        'top5_asins': str_asins[:5],
                        'cat_name': task['data'].get('category'),
                        'client_name': task['data'].get('client'),
                        'target': task['data'].get('target'),
                    },
                )
            if isinstance(task['result'].get('bsr'), dict) and isinstance(task['result']['bsr'].get('bsrLink'), str):
                bsr_link = '/'.join(task['result']['bsr']['bsrLink'].split('/')[3:-1])
            else:
                bsr_link = None
            task_alias = task.get('taskHeader', {}).get('alias')
            if task_alias:
                task_alias += '#reviews'
            data = {
                'alias': task_alias,
                'asins': [],
                'current_format': True,
                'collect_aspects': True,
                'collect_media_config': False,
                'collect_reviews': True,
                'domain': task['data'].get('domain', 'amazon.com'),
                'bsr_link': bsr_link,
            }
            data2 = {
                'alias': task_alias,
                'asins': [],
                'current_format': False,
                'collect_aspects': True,
                'collect_media_config': False,
                'collect_reviews': False,
                'domain': task['data'].get('domain', 'amazon.com'),
                'bsr_link': bsr_link,
            }

            for asin in asins[:int(task['data'].get('count', 0))]:
                data['asins'].append({'asin': asin['asin'], 'rank': asin.get('rank'), 'collect_media_config': asin == task['data'].get('target')})
            for asin in asins[int(task['data'].get('count', 0)):]:
                data2['asins'].append({'asin': asin['asin'], 'rank': asin.get('rank'), 'collect_media_config': asin == task['data'].get('target')})

            if len(data['asins']):
                requests.post(
                    'http://server:8832/products/collect',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json=data,
                ).json()
            if len(data2['asins']):
                requests.post(
                    'http://server:8832/products/collect',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json=data2,
                )
            requests.patch('http://server:8832/tasks/finish/' + task['_id'])
            requests.post('http://server:8832/tasks/release/' + task['_id'])


if __name__ == '__main__':
    run()
