import time

import requests


def run():
    print('Script started!')
    while True:
        time.sleep(5)  # low payload
        try:
            ready_products = requests.get('http://localhost:8832/tasks/get_available/products?stage=2')
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError, requests.exceptions.RequestException):
            continue
        if ready_products.status_code != 200:
            continue
        products_tasks = ready_products.json()
        for task in products_tasks:
            res = requests.post(
                'http://localhost:8832/tasks/acquire/' + task['script'] + '/' + task['header_id'] + '/' + task['_id'])
            if res.status_code == 409:
                continue
            asins = list(task['result']['asins_links'].keys())
            if task['data'].get('category'):
                requests.post(
                    'http://localhost:8832/cmd/category/set',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json={
                        'asins': asins,
                        'top5_asins': asins[:5],
                        'cat_name': task['data'].get('category'),
                        'client_name': task['data'].get('client'),
                        'target': task['data'].get('target'),
                    },
                )
            task_alias = task.get('taskHeader', {}).get('alias')
            data = {
                'alias': (task_alias + '#reviews') if task_alias else None,
                'asins': [],
                'current_format': True,
                'collect_aspects': True,
                'collect_media_config': False,
                'collect_reviews': True,
                'domain': task['data'].get('domain', 'amazon.com'),
            }
            for asin in asins:
                if asin == task['data'].get('target'):
                    data['asins'].append({'asin': asin, 'collect_media_config': True})
                else:
                    data['asins'].append({'asin': asin})
            requests.post(
                'http://localhost:8832/products/collect',
                headers={
                    'Content-Type': 'application/json',
                },
                json=data,
            )
            requests.patch('http://localhost:8832/tasks/finish/' + task['_id'])
            requests.post('http://localhost:8832/tasks/release/' + task['_id'])


if __name__ == '__main__':
    run()
