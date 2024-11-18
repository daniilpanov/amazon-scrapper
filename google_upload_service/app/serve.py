import os
import tempfile
import time
from io import BytesIO

import ffmpeg
import requests
from pytube import YouTube

import google_drive_helper


def do_task(task):
    requests.post(
        'http://localhost:8832/tasks/acquire/gdrive/' + task['header_id'] + '/' + task['_id'])
    data = task['data']
    # if video uploads from YouTube
    if data['media_type'] == 'yt':
        yt = YouTube(data['media_url'])
        yt_streams = yt.streams
        # Initialize QueryBuilder
        if 'filter' in data:
            try:
                yt_streams = yt_streams.filter(**data['filter'])
            except Exception as e:
                requests.patch('http://localhost:8832/tasks/report/' + task['_id'], json={
                    'confirm': False,
                    'stop': False,
                    'errors': [
                        f'[{data["filename"]}]:[filter] ' + str(e),
                    ],
                })
        if 'order' in data:
            if data['order'] == 'desc':
                yt_streams = yt_streams.desc()
            else:
                yt_streams = yt_streams.asc()
        if 'order_by' in data:
            yt_streams = yt_streams.order_by(data['order_by'])
        # Get final result
        if 'resolution' in data:
            yt_streams = yt_streams.get_by_resolution(data['resolution'])
        elif data.get('last', False):
            yt_streams = yt_streams.last()
        else:
            yt_streams = yt_streams.first()
        # Write to the buffer to upload this bytes
        file_buffer = BytesIO()
        yt_streams.stream_to_buffer(file_buffer)
        # uploading
        google_drive_helper.load_file(file_buffer, data['filename'], data.get('mimetype', 'text/plain'), serv=data.get('service'))
        google_drive_helper.delete_duplicate_files(serv=data.get('service'))
        # finish report
        requests.patch('http://localhost:8832/tasks/finish/' + task['_id'], json={
            'confirm': True,
        })
    else:
        # if it is just link
        res = requests.get(task['data']['media_url'])
        if res.status_code == 200:
            if data.get('media_type') == 'zipvid':
                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp:
                    temp.write(res.content)
                resolution = data.get('resolution', 360)
                input_stream = ffmpeg.input(temp.name)
                output_stream = ffmpeg.output(input_stream, temp.name + '-compressed', format='mp4',
                                              vf=f'scale=-2:{resolution}')
                try:
                    ffmpeg.run(output_stream, input=res.content, capture_stdout=True, capture_stderr=True)
                    os.remove(temp.name)
                    with open(temp.name + '-compressed', 'rb') as f:
                        video_data = f.read()
                    os.remove(temp.name + '-compressed')
                except ffmpeg._run.Error as e:
                    os.remove(temp.name)
                    os.remove(temp.name + '-compressed')
                    print(e.stderr.decode('utf-8'))
            else:
                video_data = res.content
            # uploading
            google_drive_helper.load_file(BytesIO(video_data), data['filename'], data.get('mimetype', 'video/mp4'), serv=data['service'])
            google_drive_helper.delete_duplicate_files(serv=data['service'])
            # finish report
            requests.patch('http://localhost:8832/tasks/finish/' + task['_id'], json={
                'confirm': True,
            })
        else:
            requests.patch('http://localhost:8832/tasks/report/' + task['_id'], json={
                'confirm': True,
                'stop': True,
                'errors': [
                    f'[{data["filename"]}]:[load] Can not get access to the server by link',
                ],
            })


def run():
    while True:
        try:
            tasks = requests.get('http://localhost:8832/tasks/get_available/gdrive').json()
            for task in tasks:
                do_task(task)
        except (ConnectionError, requests.ConnectionError, TimeoutError, requests.Timeout) as e:
            print('Connection error:', e)
        time.sleep(5)


if __name__ == '__main__':
    run()
