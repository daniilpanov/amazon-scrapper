import asyncio
import json
import re
from bs4 import BeautifulSoup

import amazon_requests
import db_mongo
import tasks_manager
from amazon_requests import Requests


async def get_res(sess, arr, link):
    res = await sess.get(link)
    content = await res.content.read()
    arr.append((link, content))


async def collect_media(asin, html=None, domain='amazon.com'):
    if not asin:
        raise ValueError('collect_media requires ASIN!')
    sess = None
    if not html:
        sess = amazon_requests.Requests(domain)
        await sess.init()
        while not html:
            html = await sess.get_html('dp/' + asin)
            await asyncio.sleep(1)
    soup = BeautifulSoup(html, features='lxml')
    if Requests.check_captcha(soup):
        if sess:
            await sess.request.close()
            database.db('amazon_data')['__cookies'].delete_one({'session-id': sess.sessid})
        print('Kek.. kaptcha :)')
        return await collect_media(asin, None, domain)
    try:
        js = soup.find('div', id='imageBlockVariations_feature_div').find('script').text
    except AttributeError:
        with open('../error-parse-video.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return [], []
    data_json = re.search(r"var obj = jQuery.parseJSON\('(.+)'\)", js)
    if not data_json:
        with open('../error-parse-video.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return [], []
    data = json.loads(data_json.group(1))
    titles_mapping = data['colorToAsin']
    title = None
    for t, value in titles_mapping.items():
        if value['asin'] == asin:
            title = t
            break
    if not title:
        with open('../error-parse-video.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return [], []
    images_links = []
    for img in data['colorImages'][title]:
        if 'hiRes' in img:
            images_links.append(img['hiRes'])
        else:
            res_max = 0
            media_link = None
            for link, resolution in img['main'].items():
                if int(resolution[0]) > res_max:
                    res_max = int(resolution[0])
                    media_link = link
            if media_link:
                images_links.append(media_link)
    video_links = []
    if data['videos']:
        video_links.append(data['videos'][0]['url'])
    if sess and sess.request:
        await sess.request.close()
    return images_links, video_links


def loop_iter(task_data):
    asyncio.run(collect_media(task_data['data']['asin'], domain=task_data['data'].get('domain', 'amazon.com')))


def run():
    tasks_manager.get_task_loop(loop_iter, 'video_downloader')


if __name__ == '__main__':
    run()
