import asyncio
import re
from functools import wraps, partial

import orjson
from starlette.responses import Response

from . import settings


def to_async(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def orjson_response(res):
    return Response(orjson.dumps(res, default=str), headers={'Content-Type': 'application/json'})


def get_request_headers(xmlhttp=False, domain='amazon.com', ref=None, ua: str = None, headers=None):
    return {
        'User-Agent': ua or settings.ua.random,
        'Access-Control-Allow-Origin': '*',
        'Origin': f'https://{domain}',
        'Referer': ref or f'https://{domain}/',
    } | ({
        'Rtt': '100',
        'Sec-Ch-Device-Memory': '8',
        'Sec-Ch-Dpr': '1.25',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'Windows',
        'Sec-Ch-Ua-Platform-Version': '14.0.0',
        'Sec-Ch-Viewport-Width': '810',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Viewport-Width': '810',
        'X-Requested-With': 'XMLHttpRequest',
    } if xmlhttp else {}) | (headers or {})


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('B0[A-Z0-9]{8}')
    asins = set()
    for line in text.strip().splitlines():
        found = pattern_find.findall(line)
        for item in found:
            asins.add(item)
    return list(asins)
