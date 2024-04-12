import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

import amazon_requests


async def get_res(sess, arr, link):
    res = await sess.get(link)
    content = await res.content.read()
    arr.append((link, content))


async def main(asin, domain='https://amazon.com'):
    sess = amazon_requests.Requests(domain)
    html = None
    while not html:
        html = await sess.req('dp/' + asin)
        if html:
            html = html.content
        await asyncio.sleep(1)
    soup = BeautifulSoup(html, features='lxml')
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
        await asyncio.gather(*coroutines)

        if first_video_link:
            first_video = await (await sess.get(first_video_link)).content.read()

    return *images_links, (first_video_link, first_video)


if __name__ == '__main__':
    asyncio.run(main('B08YKB6VMN'))
