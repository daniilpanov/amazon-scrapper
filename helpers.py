import asyncio
import os.path
import re
from functools import wraps, partial
from time import sleep

import orjson
from more_itertools import batched

import colorama
import requests
from starlette.responses import Response
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError

import settings

DEBUG = True


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


def get_proxy(only_alive=False):
    r = requests.get('http://localhost:8833/proxy/alive')
    if r.status_code == 200:
        return r.json()
    if not only_alive:
        return requests.get('http://localhost:8833/proxy/random').json()
    return None


def deprecate_proxy(ip):
    return requests.delete('http://localhost:8833/proxy/' + ip).status_code == 204


def deprecate_proxy_cookies(ip):
    res = requests.delete('http://localhost:8833/proxy/' + ip + '/cookies')
    if res.status_code == 200:
        return res.json()
    return None


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


def check_captcha(soup):
    return bool(soup.select('body > div > div[style*="width: 350px"]'))


def chunk_asins(asins_raw):
    return list(''.join(i) for i in batched(asins_raw, 10))


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('B0[A-Z0-9]{8}')
    asins = set()
    for line in text.strip().splitlines():
        found = pattern_find.findall(line)
        for item in found:
            asins.add(item)
    return list(asins)


def log(*args, **kwargs):
    if DEBUG:
        print(colorama.Back.GREEN, *args, colorama.Back.RESET, **kwargs)
    return True


def parse_args(argv: list[str]):
    params_dict = {}
    for arg in argv:
        row = arg.split('=', 1)
        if len(row) > 1:
            params_dict[row[0]] = row[1]
    return params_dict


def send_bot_msg(user, msg=None, files=None):
    if msg or files:
        try:
            requests.post('http://localhost:8080/send_msg', {'msg': msg, 'uid': user, 'files': files})
        except (ConnectionError, MaxRetryError, ConnectionRefusedError, ConnectionResetError, NewConnectionError):
            pass


def captcha_solve(url):
    try:
        result = requests.post('http://localhost:8090/solve/url', json={'url': url},
                               headers={'Content-Type': 'application/json'})
    except (ConnectionError, MaxRetryError, ConnectionRefusedError, ConnectionResetError, NewConnectionError):
        return None
    if result.status_code == 200:
        return result.content.decode('utf-8')
    return None


def path(*p: str, last_dir=False, filecontent: bool | str = ''):
    curr = ''
    dirs = p if last_dir else p[:-1]
    for item in dirs:
        curr = os.path.join(curr, item)
        if not os.path.exists(curr):
            os.mkdir(curr)
    if not last_dir:
        curr = os.path.join(curr, p[-1])
        if not os.path.exists(curr) and filecontent is not False:
            with open(curr, 'w') as f:
                f.write(filecontent if type(filecontent) is str else '')
    return curr
