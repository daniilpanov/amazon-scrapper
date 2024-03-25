from .async_collect_products import *
import asyncio


def run(ev, _id, asins, collect_aspects=True):
    if type(asins) is str:
        asins = chunk_asins(asins)
    print('ok1', _id, asins, collect_aspects)
    asyncio.run(start(_id, asins, collect_aspects))
