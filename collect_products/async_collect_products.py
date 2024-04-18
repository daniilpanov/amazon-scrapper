import asyncio

from bs4 import BeautifulSoup
from selenium.webdriver.common.devtools.v85.network import Request

import amazon_requests
import database as db
from functions import base_chrome_init, Amazon404Exception
from helpers import log
from parser import parse_product, parse_aspects
from video_downloader import collect_media


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
                media = collect_media(html=html, domain=sess.domain)
            if task:
                task.result['asins'].append(asin)
                task.add_progress(1)
            collected.add(asin)
            return True
        except Exception as e:
            log(f'ERROR when parsing asin: {asin} -- ', e)
            return False


if __name__ == '__main__':
    asyncio.run(get_item(None, 'B07LHL5NJT', amazon_requests.Requests(), None, set()))
