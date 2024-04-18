import asyncio

import database as db
from helpers import log
from parser import parse_product, parse_aspects
from video_downloader import collect_media

domain = 'amazon.com'


async def get_item(asin, sess, task, collected, collect_aspects, collect_videos):
    await asyncio.sleep(0)
    html = await sess.get_html(f'dp/{asin}')
    await asyncio.sleep(1)

    if product_info_write(asin, html, collect_aspects):
        if task:
            task.result['asins'].append(asin)
            task.add_progress(1)
        collected.add(asin)


def product_info_write(asin, html, write_aspects=True, get_media=False):
    try:
        data = parse_product(asin, html, domain=domain)
        db.write_product_parsed(*data)
        if write_aspects:
            aspects = parse_aspects(asin, html)
            if aspects:
                db.write_aspects(asin, aspects)
        if get_media:
            media = collect_media(html=html, domain=domain)
            
        return True
    except Exception as e:
        log(f'ERROR when parsing asin: {asin} -- ', e)
        return False


