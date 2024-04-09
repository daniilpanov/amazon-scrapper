from helpers import get_all_asins_from_text
import settings
# from .async_collect_reviews import *
from .reserve_async_collect_reviews import *


active_asins = []


async def __run(coro, asin):
    while len(active_asins) >= settings.THREADS['reviews']:
        await asyncio.sleep(0)
    active_asins.append(asin)
    print('active:', asin)
    r = await coro
    active_asins.remove(asin)
    return r


async def _run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    collect_tasks = []
    for asin in asins:
        collect_tasks.append(asyncio.shield(asyncio.create_task(__run(collect(_id, asin, keywords, domain, 0, current_format), asin))))
    return await asyncio.gather(*collect_tasks)


def run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    task.result = {'asins': [], 'count': []}
    asyncio.run(_run(ev, _id, asins, keywords, domain, current_format))


async def arun(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    task.result = {'asins': [], 'count': []}
    return await _run(ev, _id, asins, keywords, domain, current_format)


def get_runnable(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    task.result = {'asins': [], 'count': []}
    return [collect(_id, asin, keywords, domain, 0, current_format) for asin in asins]
