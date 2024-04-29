import asyncio

import peewee
from bs4 import BeautifulSoup

import database
from amazon_requests import Requests
from db import Department

domain = 'amazon.com'


async def start(deps: list[Department] | None = None):
    if not deps:
        deps = list(Department.select().where(Department.checked == False))
    semaphore = asyncio.Semaphore(20)
    coro = []
    for dep in deps:
        coro.append(collect(dep.url, dep.parent_id, semaphore))
    await asyncio.gather(*coro)


async def init(link, parent_link=None):
    r = Requests()
    await r.init()
    try:
        html = await r.get_html(link, ref=parent_link)
    except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
            ConnectionAbortedError) as e:
        print(e)
        await asyncio.sleep(1)
        html = None
    while not html:
        await r.request.close()
        await asyncio.sleep(1)
        r = Requests()
        await r.init()
        try:
            html = await r.get_html(link, ref=parent_link)
        except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
                ConnectionAbortedError) as e:
            print(e)
            await asyncio.sleep(1)
            html = None
    return html


async def collect(link='/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_370783011_2', parent_id=0, semaphore=None, parent_link=None):
    if not semaphore:
        semaphore = asyncio.Semaphore(20)
    async with semaphore:
        r = Requests()
        await r.init()
        while True:
            html = await init(link, parent_link)
            soup = BeautifulSoup(html, features='lxml')
            while Requests.check_captcha(soup):
                print('Kek.. captcha :)')
                if r.sessid in Requests.all_cookies:
                    del Requests.all_cookies[r.sessid]
                    database.db('amazon_data')['__cookies'].delete_one({'session-id': r.sessid})
                await asyncio.sleep(5)
                html = await init(link, parent_link)
                soup = BeautifulSoup(html, features='lxml')
            group = soup.find('div', {'role': 'group'})
            if group:
                items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
                break
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
        try:
            parent = Department.get_by_id(parent_id)
            parent.checked = True
            parent.save()
        except peewee.DoesNotExist:
            pass
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
            coroutines.append(collect(link, _id, semaphore, parent_link))
        await r.request.close()
    await asyncio.gather(*coroutines)


if __name__ == '__main__':
    asyncio.run(start())
    # asyncio.run(start(link='Best-Sellers-Beauty-Personal-Care-Perfumes-Fragrances/zgbs/beauty/11056591/ref=zg_bs_unv_beauty_2_11056761_1'))
