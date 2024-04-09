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


async def start(r=None, link='/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_370783011_2', parent_id=0):
    semaphore = asyncio.Semaphore(20)
    await collect(r, link, parent_id, semaphore)


async def init(r, link, parent_link=None):
    try:
        html = await r.get_html(link, ref=parent_link)
    except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
            ConnectionAbortedError) as e:
        print(e)
        sleep(1)
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


async def collect(r=None, link='/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_370783011_2', parent_id=0, semaphore=None, parent_link=None):
    if not semaphore:
        semaphore = asyncio.Semaphore(20)
    async with semaphore:
        if not r:
            r = Requests()
            await r.init()
        group = None
        while not group:
            html = await init(r, link, parent_link)
            soup = BeautifulSoup(html, features='lxml')
            while Requests.check_captcha(soup):
                print('Kek.. captcha :)')
                if r.sessid in Requests.all_cookies:
                    del Requests.all_cookies[r.sessid]
                database.db('amazon_data')['__cookies'].delete_one({'session-id': r.sessid})
                sleep(20)
                html = await init(r, link, parent_link)
                soup = BeautifulSoup(html, features='lxml')
            group = soup.find('div', {'role': 'group'})
            items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
        data = []
        models = []
        for item in items:
            a = item.find('a')
            if not a:
                return None
            title = a.text
            link = a['href']
            internal_id = link.split('/')[-2]
            data.append((internal_id, title, link))
            models.append(Department(parent_id=parent_id, name=title, url=link, internal_id=internal_id))
        try:
            Department.bulk_create(models)
        except peewee.IntegrityError as e:
            print(e)
        models = {i.internal_id: i for i in Department.select().where(Department.parent_id == parent_id)}
        print('models: ', models)
        coroutines = []
        parent_link = link
        for internal_id, title, link in data:
            model = models.get(internal_id)
            if model:
                _id = model.id
            else:
                _id = 0
            coroutines.append(collect(r, link, _id, semaphore, parent_link))
        await r.request.close()
    await asyncio.gather(*coroutines)


if __name__ == '__main__':
    fl_d = Department.select().where(Department.parent_id == 0)
    for d in fl_d:
        if d.id < 643:
            continue
        print('*** collecting', d.name, '--', d.url, '--', d.id)
        asyncio.run(start(link=d.url, parent_id=d.id))
        with open('deps-log.txt', 'w') as f:
            f.write(d.name + '--' + d.url + '--' + str(d.id))
        print('*** end', d.name, '--', d.id)
    # asyncio.run(start(link='Best-Sellers-Beauty-Personal-Care-Perfumes-Fragrances/zgbs/beauty/11056591/ref=zg_bs_unv_beauty_2_11056761_1'))
