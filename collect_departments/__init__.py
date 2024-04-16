from .collect_asins_nearby import collect_nearby
import asyncio


def run(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com', target=None):
    if bsr:
        asyncio.run(collect_asins_nearby.collect_nearby(ev, _id, bsr, limit, unique_brands, count, domain, target))


async def arun(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com', target=None):
    if bsr:
        return await collect_asins_nearby.collect_nearby(ev, _id, bsr, limit, unique_brands, count, domain, target)


def get_runnable(ev, _id, bsr=None, limit=False, unique_brands=False, count=5, domain='amazon.com', target=None):
    if bsr:
        return [collect_asins_nearby.collect_nearby(ev, _id, bsr, limit, unique_brands, count, domain, target)]
