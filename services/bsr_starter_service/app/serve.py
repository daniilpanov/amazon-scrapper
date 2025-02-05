import time
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import quote

import requests
import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/bsrstarter.log')
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
                logger.warning('A task with no result or no data received: ' + task['_id'])
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
            logger.debug('Task acquiring result: ' + str(res))
            if not res.ok:
                continue

            department_document = None
            bsr_id = task['result'].get('bsr_id')
            bsr_url = task['result'].get('bsr_url')
            logger.info('Task ID: ' + task['_id'] + ', BSR ID: ' + str(bsr_id) + ', BSR URL: ' + str(bsr_url))
            if bsr_id:
                department_document_resp = requests.get('http://bsr_loader:8839/v1/bsr/' + str(bsr_id) + '?fields=items')
                logger.debug('Task ID: ' + task['_id'] + ', 1st resp: ' + str(department_document_resp))
                if department_document_resp.ok and department_document_resp.status_code < 300:
                    department_document = department_document_resp.json()
            if not department_document and bsr_url:
                department_document_resp = requests.get('http://bsr_loader:8839/v1/bsr/by_url?fields=items&bsr_url=' + quote(bsr_url))
                logger.debug('Task ID: ' + task['_id'] + ', 2nd resp: ' + str(department_document_resp))
                if department_document_resp.ok and department_document_resp.status_code < 300:
                    department_document = department_document_resp.json()
            logger.debug('Task ID: ' + task['_id'] + ', BSR Document: ' + str(department_document))
            if not department_document:
                requests.patch('http://server:8832/tasks/report/' + task['_id'], json={
                    'stop': True,
                    'confirm': True,
                    'errors': [
                        'There is an error on getting the department document',
                    ],
                }, headers={
                    'Content-Type': 'application/json',
                })
                continue

            asins = department_document.get('items', [])[:int(task['data'].get('count', 0))]
            logger.debug('Task ID: ' + task['_id'] + ', ASINs list: ' + str(asins))
            str_asins = [p['asin'] for p in asins]
            logger.debug('Task ID: ' + task['_id'] + ', string ASINs list: ' + str(str_asins))
            target = task['data'].get('target')
            if task['data'].get('category'):
                logger.debug(requests.post(
                    'http://server:8832/cmd/category/set',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json={
                        'asins': str_asins,
                        'top5_asins': str_asins[:5],
                        'cat_name': task['data'].get('category'),
                        'client_name': task['data'].get('client'),
                        'target': target,
                    },
                ))
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

            no_target_in_bsr = True
            for asin in asins[:int(task['data'].get('count', 0))]:
                is_target = no_target_in_bsr and asin == target
                data['asins'].append({'asin': asin['asin'], 'rank': asin.get('rank'), 'collect_media_config': is_target})
                if is_target and no_target_in_bsr:
                    no_target_in_bsr = False

            if no_target_in_bsr:
                data['asins'] = [{'asin': target, 'rank': None, 'collect_media_config': True}, *data['asins']]
            logger.info('Task ID: ' + task['_id'] + ', ASINs list: ' + str(data['asins']))
            if len(data['asins']):
                requests.post(
                    'http://server:8832/products/collect',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json=data,
                ).json()

            re1 = requests.patch('http://server:8832/tasks/finish/' + task['_id'])
            re2 = requests.post('http://server:8832/tasks/release/' + task['_id'])
            logger.debug('Task ID: ' + task['_id'] + ', Ending responses: ' + str(re1) + ' and ' + str(re2))


if __name__ == '__main__':
    run()
