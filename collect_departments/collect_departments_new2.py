import asyncio
from queue import Queue
from threading import Thread
from time import sleep

import colorama
import peewee
from bs4 import BeautifulSoup

import database
from amazon_requests import Requests
from db import Department

domain = 'amazon.com'


async def start():
    models = await iteration('bestsellers', 0, 'https://www.amazon.com/')
    if not models:
        print('No one department can be found :/')
        return
    coros = []
    for internal_id, model in models.items():
        if model:
            _id = model.id
        else:
            _id = 0
        coros.append(collect(model.url, _id, 'https://www.amazon.com/bestsellers'))
    await asyncio.gather(*coros)


async def get_html(r, link, parent_link=None):
    try:
        html = await r.get_html(link, ref=parent_link)
    except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
            ConnectionAbortedError) as e:
        print(e)
        await asyncio.sleep(1)
        html = None
    while not html:
        await r.request.close()
        sleep(1)
        r = Requests()
        await r.init()
        try:
            html = await r.get_html(link, ref=parent_link)
        except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
                ConnectionAbortedError) as e:
            print(e)
            sleep(1)
            html = None
    return html


async def iteration(link, parent_id, parent_link):
    r = Requests()
    await r.init()
    while True:
        html = await get_html(r, link, parent_link)
        soup = BeautifulSoup(html, features='lxml')
        while Requests.check_captcha(soup):
            print('Kek.. captcha :)')
            if r.sessid in Requests.all_cookies:
                del Requests.all_cookies[r.sessid]
            database.db('amazon_data')['__cookies'].delete_one({'session-id': r.sessid})
            await asyncio.sleep(1)
            html = await get_html(r, link, parent_link)
            soup = BeautifulSoup(html, features='lxml')
        group = soup.find('div', {'role': 'group'})
        if group:
            items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
            break
    models = []
    for item in items:
        a = item.find('a')
        if not a:
            print('Not found at:', link)
            return None
        title = a.text
        link = a['href']
        internal_id = link.split('/')[-2]
        models.append(Department(parent_id=parent_id, name=title, url=link, internal_id=internal_id))
    try:
        Department.bulk_create(models)
    except peewee.IntegrityError as e:
        print(e)
    return {i.internal_id: i for i in Department.select().where(Department.parent_id == parent_id)}


async def collect(link='/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_370783011_2', parent_id=0, parent_link=None):
    models = await iteration(link, parent_id, parent_link)
    if models is None:
        return None
    print('models: ', models)
    parent_link = link
    for internal_id, model in models.items():
        if model:
            _id = model.id
        else:
            _id = 0
        await collect(model.url, _id, 'https://www.amazon.com/' + parent_link)


if __name__ == '__main__':
    asyncio.run(start())
