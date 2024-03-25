from helpers import get_all_asins_from_text
from .async_collect_reviews import *


async def _run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    return await asyncio.gather(*(collect(_id, asin, keywords, domain, 0, current_format) for asin in asins))


def run(ev, _id, asins, keywords='', domain='amazon.com', current_format=True):
    task = tasks.get_task(_id)
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task.all = len(asins)
    asyncio.run(_run(ev, _id, asins, keywords, domain, current_format))
    if task.success is None:
        task.success = True
    task.progress = 100
    task.result = asins
