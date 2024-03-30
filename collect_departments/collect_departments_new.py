import asyncio
from queue import Queue
from threading import Thread

import peewee
from bs4 import BeautifulSoup

from amazon_requests import Requests
from db import Department

domain = 'amazon.com'


def data_writing(q: Queue):
    models = q.get()
    while models is not None:
        try:
            Department.bulk_create(models)
        except peewee.IntegrityError as e:
            print(e)
        models = q.get()


def data_logging(q: Queue):
    s = q.get()
    while s is not None:
        print(s)
        s = q.get()


data_q = Queue()
data_thr = Thread(target=data_writing, args=(data_q,))
data_log_q = Queue()
data_log_thr = Thread(target=data_logging, args=(data_log_q,))


semaphore = asyncio.Semaphore(30)


async def collect(r=None, link='/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_370783011_2', parent_id=None):
    async with semaphore:
        if not r:
            r = Requests()
            await r.init()
        html = await r.get_html(link)
        while not html:
            r = Requests()
            await r.init()
            html = await r.get_html(link)
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
            data.append((title, link))
            models.append(Department(parent_id=parent_id, name=title, url=link))
        data_q.put(models)
        models = {i.name: i for i in Department.select().where(Department.parent_id == parent_id)}
        data_log_q.put(data)
        coroutines = []
        for title, link in data:
            model = models.get(title)
            if model:
                _id = model.id
            else:
                _id = None
            coroutines.append(collect(r, link, _id))
    await asyncio.gather(*coroutines)


if __name__ == '__main__':
    data_thr.start()
    data_log_thr.start()
    # asyncio.run(collect())
    asyncio.run(collect(link='/Best-Sellers-Health-Household-Shoe-Inserts-Insoles/zgbs/hpc/3780081/ref=zg_bs_nav_hpc_3_3779911', parent_id=9628))
    data_q.put(None)
    data_log_q.put(None)
    data_thr.join()
    data_log_thr.join()
