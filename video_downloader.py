import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

import amazon_requests
import database
from amazon_requests import Requests


async def get_res(sess, arr, link):
    res = await sess.get(link)
    content = await res.content.read()
    arr.append((link, content))


async def collect_media(asin=None, html=None, domain='amazon.com'):
    if not html and not asin:
        raise ValueError('collect_media needs one of arguments: asin or html!')
    sess = amazon_requests.Requests(domain)
    if not html:
        await sess.init()
        while not html:
            html = await sess.get_html('dp/' + asin)
            await asyncio.sleep(1)
    soup = BeautifulSoup(html, features='lxml')
    if Requests.check_captcha(soup):
        await sess.request.close()
        print('Kek.. kaptcha :)')
        database.db('amazon_data')['__cookies'].delete_one({'session-id': sess.sessid})
        return await collect_media(asin, None, domain)
    js = soup.find('div', id='imageBlockVariations_feature_div').find('script').text
    media_links = re.findall(r'(?:https?://|ftps?://|www\.)(?:(?![.,?!;:()]*(?:\s|"|$))[^\s"]){2,}', js)
    first_video_link = None
    if sess.request:
        await sess.request.close()
    images_links = []
    for ml in media_links:
        if ml.endswith('.jpg') or ml.endswith('.png') or ml.endswith('.gif'):
            images_links.append(ml)
        elif ml.endswith('.mp4'):
            if first_video_link is None:
                first_video_link = ml
                break
    # async with aiohttp.ClientSession() as sess:
    #     coroutines = []
    #     for ml in media_links:
    #         if ml.endswith('.jpg') or ml.endswith('.png') or ml.endswith('.gif'):
    #             coroutines.append(get_res(sess, images_links, ml))
    #         elif ml.endswith('.mp4'):
    #             if first_video_link is None:
    #                 first_video_link = ml
    #     await asyncio.gather(*coroutines)
    #
    #     if first_video_link:
    #         first_video = await (await sess.get(first_video_link)).content.read()
    #
    # return *images_links, (first_video_link, first_video)
    return images_links, [first_video_link]


if __name__ == '__main__':
    asyncio.run(collect_media('B08YKB6VMN'))
