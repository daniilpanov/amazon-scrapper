from async_collect_products import *
import asyncio


def run(ev, asins, _id, user, list_name):
    if type(asins) is str:
        asins = chunk_asins(asins)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start(asins, user, list_name, _id))
