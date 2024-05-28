import itertools
import random
import time
from fastapi import HTTPException
from threading import Thread

import fastapi
import requests
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

import db_mongo
import settings


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

    def __init__(self, proxy_address, port, username, password):
        self.addr = proxy_address
        self.port = port
        self.username = username
        self.password = password
        self.ua = settings.ua.random

    def __hash__(self):
        return hash(self.addr)

    @classmethod
    def update_proxies(cls, query_builder):
        cls.proxies = set()
        _next = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct"
        while True:
            res = requests.get(
                _next,
                headers={
                     "Authorization": "Token " + settings.PROXY_AUTH_TOKEN,
                },
            ).json()
            for item in res['results']:
                inst = cls(item['proxy_address'], item['port'], item['username'], item['password'])
                cls.proxies.add(inst)
            if not res.get('next'):
                break

        cookies = itertools.cycle(list(query_builder.limit(len(cls.proxies))))
        try:
            for proxy in cls.proxies:
                proxy.cookies = next(cookies)
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


def updating():
    while True:
        cookies = db_mongo.db('amazon_data')['__cookies'].find({})
        AmazonProxy.update_proxies(cookies)
        time.sleep(2000)


app = fastapi.FastAPI()


@app.get('/proxy/alive')
def get_alive_proxy():
    try:
        return AmazonProxy.get_proxy().to_dict()
    except AttributeError:
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.get('/proxy/random')
def get_random_proxy():
    try:
        return random.choice(list(AmazonProxy.proxies)).to_dict()
    except (KeyError, IndexError):
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.delete('/proxy/{addr}')
def deprecate_proxy(addr: str):
    found = False
    for proxy in AmazonProxy.proxies:
        if proxy.addr == addr:
            proxy.deprecated = True
            return Response(status_code=HTTP_204_NO_CONTENT)
    if not found:
        raise HTTPException(HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    import uvicorn

    upd_thr = Thread(target=updating, daemon=True)
    upd_thr.start()
    uvicorn.run(app, host='0.0.0.0', port=8833)
