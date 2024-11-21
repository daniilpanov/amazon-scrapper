import time

import requests
from pymongo.errors import DuplicateKeyError

import s3helper
import controller
from db_mongo import db

import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

media_collection = db('amazon_data')['products_media']


def load_video(asin, variant, mimetype, path, filename, prefix):
    if s3helper.upload_file(path, filename, prefix) and asin:
        if mimetype == 'm3u':
            mimetype = 'video/mp4'
        try:
            media_collection.insert_one({
                'asin': asin,
                'media_url': 'https://https://daniilbucket.s3.us-east-2.amazonaws.com/' + prefix + filename,
                'mimetype': mimetype,
                'variant': variant,
            })
        except DuplicateKeyError:
            pass


def do_task(task):
    requests.post('http://server:8832/tasks/acquire/s3load/' + task['header_id'] + '/' + task['_id'])

    data = task['data']

    video_url = data['videoUrl']
    asin = data.get('asin', None)
    variant = data.get('variant', 0)
    filename = data.get('filename', asin or 'fileobj')
    mimetype = data.get('mimetype', filename.rsplit('.', maxsplit=1)[-1])
    prefix = data.get('prefix', '')

    try:
        # if video uploads from YouTube
        if data['media_type'] == 'yt':
            controller.process_youtube(
                [video_url],
                lambda path: load_video(asin, variant, mimetype, path, filename, prefix),
            )
        elif data['media_type'] == 'm3u':
            controller.process_usual(
                controller.mp.parse_res_m3u(controller.mp.parse_root_m3u(mimetype)),
                lambda path: load_video(asin, variant, mimetype, path, filename, prefix),
            )
        else:
            controller.process_usual(
                [video_url],
                lambda path: load_video(asin, variant, mimetype, path, filename, prefix),
            )
        requests.patch('http://server:8832/tasks/finish/' + task['_id'], json={
            'confirm': True,
        })
    except Exception as e:
        requests.patch('http://server:8832/tasks/report/' + task['_id'], json={
            'confirm': True,
            'stop': True,
            'errors': [f'[{filename}]:[s3_upl] ' + str(e)],
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
