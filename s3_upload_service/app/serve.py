import time

import requests

import s3helper
import controller

import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def load_video(path, filename, prefix):
    s3helper.upload_file(path, filename, prefix)


def do_task(task):
    requests.post(
        'http://server:8832/tasks/acquire/s3load/' + task['header_id'] + '/' + task['_id'])
    data = task['data']
    try:
        # if video uploads from YouTube
        if data['media_type'] == 'yt':
            controller.process_youtube(
                [data['videoUrl']],
                lambda path: load_video(path, data['filename'], data['prefix']),
            )
            requests.patch('http://server:8832/tasks/finish/' + task['_id'], json={
                'confirm': True,
            })
        elif data['media_type'] == 'm3u':
            controller.process_usual(
                controller.mp.parse_res_m3u(controller.mp.parse_root_m3u(data['videoUrl'])),
                lambda path: load_video(path, data['filename'], data['prefix']),
            )
            requests.patch('http://server:8832/tasks/finish/' + task['_id'], json={
                'confirm': True,
            })
        else:
            controller.process_usual(
                [data['videoUrl']],
                lambda path: load_video(path, data['filename'], data['prefix']),
            )
    except Exception as e:
        requests.patch('http://server:8832/tasks/report/' + task['_id'], json={
            'confirm': False,
            'stop': False,
            'errors': [f'[{data["filename"]}]:[filter] ' + str(e)],
        })


def run():
    while True:
        try:
            tasks = requests.get('http://server:8832/tasks/get_available/s3load').json()
            for task in tasks:
                do_task(task)
        except Exception as e:
            logger.warning(e)
        finally:
            time.sleep(5)


if __name__ == '__main__':
    run()
