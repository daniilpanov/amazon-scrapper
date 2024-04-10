import asyncio
import re

import requests
from bs4 import BeautifulSoup


async def main():
    with open('test.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, features='lxml')
    js = soup.find('div', id='ajaxBlockComponents_feature_div').find('script').text
    media_links = re.findall(r'(?:https?://|ftps?://|www\.)(?:(?![.,?!;:()]*(?:\s|"|$))[^\s"]){2,}', js)
    first_video_link = next(filter(lambda i: not i.endswith('.jpg') and not i.endswith('.png'), media_links))
    print(first_video_link)
    ext = first_video_link.split('.')[-1]
    with open('res.' + ext, 'wb') as rf:
        rf.write(requests.get(first_video_link).content)


if __name__ == '__main__':
    asyncio.run(main())
