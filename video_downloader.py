import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

import amazon_requests
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
        return await collect_media(asin, None, domain)
    with open('test2.html', 'w', encoding='utf-8') as f:
        f.write(html)
    js = soup.find('div', id='ajaxBlockComponents_feature_div').find('script').text
    media_links = re.findall(r'(?:https?://|ftps?://|www\.)(?:(?![.,?!;:()]*(?:\s|"|$))[^\s"]){2,}', js)
    first_video_link = None
    images_links = []
    async with aiohttp.ClientSession() as sess:
        coroutines = []
        for ml in media_links:
            if ml.endswith('.jpg') or ml.endswith('.png') or ml.endswith('.gif'):
                coroutines.append(get_res(sess, images_links, ml))
            else:
                if first_video_link is None:
                    first_video_link = ml
        print(first_video_link)
        await asyncio.gather(*coroutines)

        if first_video_link:
            first_video = await (await sess.get(first_video_link)).content.read()

    return *images_links, (first_video_link, first_video)


if __name__ == '__main__':
    asyncio.run(collect_media('B08YKB6VMN'))
