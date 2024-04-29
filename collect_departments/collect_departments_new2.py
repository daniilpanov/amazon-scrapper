import asyncio
from time import sleep

import peewee
from bs4 import BeautifulSoup

import database
from amazon_requests import Requests
from db import Department

domain = 'amazon.com'


async def reverse_start(deps=None):
    limit = 30
    while True:
        if not deps:
            deps = list(Department.select().where(Department.collected == False).limit(limit))
        if not deps:
            try:
                Department.get()
                print('Collected!')
                return
            except peewee.DoesNotExist:
                deps = await iteration(link='bestsellers', _id=0, parent_link='https://www.amazon.com/')
        coro = []
        count = limit
        for dep in deps:
            coro.append(iteration(model=dep, parent_link=dep.url))
            count -= 1
            if count <= 0:
                await asyncio.gather(*coro)
                count = limit
                coro = []
        await asyncio.gather(*coro)


async def get_html(link, parent_link=None):
    r = Requests()
    try:
        await r.init()
        html = await r.get_html(link, ref=parent_link)
    except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
            ConnectionAbortedError) as e:
        print(e)
        await asyncio.sleep(1)
        html = None
    while not html:
        await r.close()
        sleep(1)
        r = Requests()
        await r.init()
        try:
            html = await r.get_html(link, ref=parent_link)
            await r.close()
        except (asyncio.exceptions.CancelledError, asyncio.TimeoutError, TimeoutError, ConnectionResetError,
                ConnectionAbortedError) as e:
            print(e)
            sleep(1)
            html = None
    await r.close()
    return r, html


async def iteration(*, link=None, _id=0, model=None, parent_link=None):
    if not any((model, _id + 1, link)):
        raise ValueError('One of arguments must be sent! [iteration]')
    if _id:
        model = Department.get_by_id(_id)
    if not link:
        link = model.url
        _id = model.id
    while True:
        r, html = await get_html(link, parent_link)
        soup = BeautifulSoup(html, features='lxml')
        while Requests.check_captcha(soup):
            print('Kek.. captcha :)')
            if r.sessid in Requests.all_cookies:
                del Requests.all_cookies[r.sessid]
                database.db('amazon_data')['__cookies'].delete_one({'session-id': r.sessid})
            await asyncio.sleep(1)
            r, html = await get_html(link, parent_link)
            soup = BeautifulSoup(html, features='lxml')
        group = soup.find('div', {'role': 'group'})
        if group:
            items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
            break
    model.collected = True
    model.save()
    models = []
    for item in items:
        a = item.find('a')
        if not a:
            print('Not found at:', link)
            return None
        title = a.text
        link = a['href']
        internal_id = link.split('/')[-2]
        models.append(Department(parent_id=_id, name=title, url=link, internal_id=internal_id))
    try:
        Department.bulk_create(models)
    except peewee.IntegrityError as e:
        print(e)


if __name__ == '__main__':
    # asyncio.run(start())
    asyncio.run(reverse_start())
