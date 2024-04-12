import asyncio
import re

import aiohttp
import requests
from bs4 import BeautifulSoup


async def get_res(sess, arr, link):
    res = await sess.get(link)
    content = await res.content.read()
    arr.append((link, content))


async def main():
    with open('test.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, features='lxml')
    js = soup.find('div', id='ajaxBlockComponents_feature_div').find('script').text
    media_links = re.findall(r'(?:https?://|ftps?://|www\.)(?:(?![.,?!;:()]*(?:\s|"|$))[^\s"]){2,}', js)
    first_video_link = None
    # video_links = []
    images_links = []
    async with aiohttp.ClientSession() as sess:
        coroutines = []
        for ml in media_links:
            if ml.endswith('.jpg') or ml.endswith('.png') or ml.endswith('.gif'):
                coroutines.append(get_res(sess, images_links, ml))
            else:
                if first_video_link is None:
                    first_video_link = ml
                # coroutines.append(get_res(sess, video_links, ml))
        await asyncio.gather(*coroutines)

        if first_video_link:
            first_video = await (await sess.get(first_video_link)).content.read()
            ext = first_video_link.split('.')[-1]

        bin_content = await (await sess.get(first_video_link)).content.read()
    with open('res.' + ext, 'wb') as rf:
        rf.write(bin_content)


if __name__ == '__main__':
    asyncio.run(main())
