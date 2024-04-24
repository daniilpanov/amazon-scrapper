import asyncio
import io
from pprint import pprint

import aiohttp
from bs4 import BeautifulSoup
from pymongo.errors import BulkWriteError

import amazon_requests
import database as db
from functions import base_chrome_init, Amazon404Exception
from google_drive_helper import load_file, get_files
from helpers import log
from parser import parse_product, parse_aspects
from video_downloader import collect_media


async def get_and_put_media_content(i, link, arr):
    async with aiohttp.ClientSession() as sess:
        res = await sess.get(link)
        if 400 >= res.status >= 200:
            arr[i] = io.BytesIO(await res.content.read())


async def get_item(ev, asin, sess, task, collected, collect_aspects=True, need_collect_media=False):
    await asyncio.sleep(0)
    while not ev or not ev.is_set():
        html = None
        for i in range(50):
            if html or ev and ev.is_set():
                break
            html = await sess.get_html(f'dp/{asin}')
            if not html:
                continue
            if amazon_requests.Requests.check_captcha(BeautifulSoup(html, features='lxml')):
                html = None
        if not html:
            try:
                wd = base_chrome_init(goto=f'https://{sess.domain}')
                wd.change_loc()
                wd.get(f'https://{sess.domain}/dp/{asin}')
                html = wd.get_page_source()
                wd.full_close()
            except Amazon404Exception:
                if task:
                    task.add_progress(1)
                return False
        await asyncio.sleep(1)

        if ev and ev.is_set():
            return
        try:
            data = parse_product(asin, html, domain=sess.domain)
            if not data:
                return
            if data == -1:
                continue
            db.write_product_parsed(*data)
            if collect_aspects:
                aspects = parse_aspects(asin, html)
                if aspects:
                    db.write_aspects(asin, aspects)
            if need_collect_media:
                media = await collect_media(asin, html, sess.domain)
                try:
                    db.db('amazon_data')['products_media'].insert_many([{'asin': asin, 'type': 'img', 'media_link': lnk} for lnk in media[0]], ordered=False)
                except BulkWriteError:
                    pass
                try:
                    db.db('amazon_data')['products_media'].insert_many([{'asin': asin, 'type': 'vid', 'media_link': lnk} for lnk in media[1]], ordered=False)
                except BulkWriteError:
                    pass
                coro = []
                images_content = [None for _ in range(len(media[0]))]
                for i, image in enumerate(media[0]):
                    coro.append(get_and_put_media_content(i, image, images_content))
                video_content = [None for _ in range(len(media[1]))]
                for i, video in enumerate(media[1]):
                    coro.append(get_and_put_media_content(i, video, video_content))
                await asyncio.gather(*coro)
                for i, (lnk, img) in enumerate(zip(media[0], images_content)):
                    name = lnk.split('/')[-1]
                    ext = name.split('.')[-1]
                    load_file(img, asin + '-' + str(i) + '.' + ext, f'image/{ext}')
                for i, (lnk, vid) in enumerate(zip(media[1], video_content)):
                    name = lnk.split('/')[-1]
                    ext = name.split('.')[-1]
                    load_file(vid, asin + '-' + str(i) + '.' + ext, f'video/{ext}')
            if task:
                task.result['asins'].append(asin)
                task.add_progress(1)
            collected.add(asin)
            return True
        except Exception as e:
            log(f'ERROR when parsing asin: {asin} -- ', e)
            return False
