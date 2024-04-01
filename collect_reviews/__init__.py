from helpers import get_all_asins_from_text
from asyncio import Semaphore
from .async_collect_reviews import *

global_reviews_limit_sem = Semaphore(2)


async def __run(coroutine):
    async with global_reviews_limit_sem:
        r = await coroutine
    return r


async def _run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    collect_tasks = []
    for asin in asins:
        collect_tasks.append(__run(collect(_id, asin, keywords, domain, 0, current_format)))
    return await asyncio.gather(*collect_tasks)


def run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    task.result = {
        'asins': asins,
        'count': [database.db('amazon_data')['customer_reviews'].count_documents({'asin': asin}) for asin in asins],
    }
    asyncio.run(_run(ev, _id, asins, keywords, domain, current_format))
