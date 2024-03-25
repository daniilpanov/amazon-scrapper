from .async_collect_products import *
import asyncio


def run(ev, _id, asins, list_name):
    if type(asins) is str:
        asins = chunk_asins(asins)
    asyncio.run(start(_id, asins, list_name))
