from .collect_asins_nearby import collect_nearby
from .collect_departments import start
import asyncio


def run(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com'):
    if bsr:
        asyncio.run(collect_asins_nearby.collect_nearby(_id, bsr, limit, unique_brands, count, domain))
    else:
        asyncio.run(collect_departments.start(_id))


async def arun(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com'):
    if bsr:
        return await collect_asins_nearby.collect_nearby(_id, bsr, limit, unique_brands, count, domain)
    else:
        return await collect_departments.start(_id)


def get_runnable(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com'):
    if bsr:
        return [collect_asins_nearby.collect_nearby(_id, bsr, limit, unique_brands, count, domain)]
    else:
        return [collect_departments.start(_id)]
