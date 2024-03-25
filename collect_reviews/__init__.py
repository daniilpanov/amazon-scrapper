import os
from concurrent.futures import ThreadPoolExecutor

from helpers import get_all_asins_from_text
from .async_collect_reviews import *


threader = ThreadPoolExecutor(min(os.cpu_count(), 8))


async def _run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    for asin in asins:
        threader.submit(collect, _id, asin, keywords, domain, 0, current_format)


def run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    task.result = []
    asyncio.run(_run(ev, _id, asins, keywords, domain, current_format))
