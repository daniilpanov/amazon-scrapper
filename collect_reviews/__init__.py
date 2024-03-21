from .async_collect_reviews import *


def run(ev, asin, keywords='', user=None, domain='amazon.com', current_format=True):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(collect(asin, keywords, user, domain, 0, current_format))
