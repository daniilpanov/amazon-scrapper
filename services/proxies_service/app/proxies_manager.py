import itertools
import random
import time
from fastapi import HTTPException

import fastapi
import requests
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

import db_mongo
import config


class AmazonProxy:
    # @classprop
    proxies: set = set()

    addr: str
    port: int
    username: str
    password: str
    ua: str
    cookies: dict[str, str] = None
    deprecated: bool = False
    headers: dict[str, str] = {
        'Authorization': 'Token ' + config.PROXY_AUTH_TOKEN,
    }
    user_id: int | None = None

    def __init__(self, proxy_address, port, username, password):
        self.addr = proxy_address
        self.port = port
        self.username = username
        self.password = password
        self.ua = config.ua.random

    def __hash__(self):
        return hash(self.addr)

    def __str__(self):
        return f'{self.username}:{self.password}@{self.addr}:{self.port}'

    @classmethod
    def update_proxies(cls, query_builder):
        cls.proxies = set()
        # _next = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=backbone'
        _next = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct'
        while True:
            res = requests.get(
                _next,
                headers=cls.headers,
            ).json()
            for item in res['results']:
                inst = cls(item['proxy_address'], item['port'], item['username'], item['password'])
                cls.proxies.add(inst)
            if not res.get('next'):
                break
            _next = res['next']

        cookies = itertools.cycle(list(query_builder.limit(len(cls.proxies))))
        try:
            for proxy in cls.proxies:
                proxy.cookies = next(cookies)
                del proxy.cookies['_id']
                del proxy.cookies['session-id-time']
        finally:
            return cls.proxies

    @classmethod
    def get_proxy(cls):
        for proxy in cls.proxies:
            if proxy.deprecated:
                continue
            return proxy
        raise HTTPException(HTTP_404_NOT_FOUND)

    def to_dict(self):
        return {
            'addr': self.addr,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'useragent': self.ua,
            'cookies': self.cookies,
        }

    @staticmethod
    def to_str(obj):
        return f'socks5://{obj["username"]}:{obj["password"]}@{obj["addr"]}:{obj["port"]}'


def updating():
    res = requests.get(
        'https://proxy.webshare.io/api/v2/subuser/',
        headers=AmazonProxy.headers,
    )
    res = res.json()
    for user in res.get('results', []):
        if user['label'] == 'Scraper':
            AmazonProxy.user_id = user['id']
            AmazonProxy.headers['X-Subuser'] = str(user['id'])
            break

    while True:
        cookies = db_mongo.db('amazon_data')['__cookies'].find(
            {'session-id': {'$exists': True}, 'sp-cdn': {'$exists': False}})
        print(list(str(i) for i in AmazonProxy.update_proxies(cookies)))
        for i in range(60):
            if all([proxy.deprecated for proxy in AmazonProxy.proxies]):
                time.sleep(5)
                break
            time.sleep(1)


app = fastapi.FastAPI()


@app.get('/proxy/alive')
async def get_alive_proxy():
    try:
        return AmazonProxy.get_proxy().to_dict()
    except AttributeError:
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.get('/proxy/random')
async def get_random_proxy():
    try:
        return random.choice(list(AmazonProxy.proxies)).to_dict()
    except (KeyError, IndexError):
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.delete('/proxy/{addr}')
async def deprecate_proxy(addr: str):
    found = False
    for proxy in AmazonProxy.proxies:
        if proxy.addr == addr:
            proxy.deprecated = True
            await deprecate_cookie(addr)
            return Response(status_code=HTTP_204_NO_CONTENT)
    if not found:
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.delete('/proxy/{addr}/cookies')
async def deprecate_cookie(addr: str):
    found = False
    i = 0
    for proxy in AmazonProxy.proxies:
        if proxy.addr == addr:
            db_mongo.db('amazon_data')['__cookies'].delete_one({'session-id': proxy.cookies['session-id']})
            cookies = list(db_mongo.db('amazon_data')['__cookies'].find(
                {'session-id': {'$exists': True}, 'sp-cdn': {'$exists': False}}).limit(1).skip(10 + i))
            if cookies:
                del cookies[0]['_id']
                del cookies[0]['session-id-time']
                proxy.cookies = cookies[0]
            return proxy.to_dict()
        i += 1
    if not found:
        raise HTTPException(HTTP_404_NOT_FOUND)
