import asyncio
import functools
from time import sleep

import requests
from bs4 import BeautifulSoup

from functions import base_chrome_init


class ProxyConf(dict):
    def __hash__(self):
        return hash((self['proxy_address'], self['port']))


@functools.cache
def check_proxy(proxy):
    if proxy['country_code'] != 'US':
        return False
    try:
        proxy_str = proxy.get('protocol', 'socks5') + '://'
        if 'username' in proxy and 'password' in proxy:
            proxy_str += proxy['username'] + ':' + proxy['password'] + '@'
        proxy_str += proxy['proxy_address'] + ':' + str(proxy.get('port', 80))
        res = requests.get('https://2ip.ru', proxies={
            'http': proxy_str,
            'https': proxy_str,
        })
        soup = BeautifulSoup(res.text, features='lxml')
        link_addr = soup.find(attrs={'id': 'ip-info-country'})
        if not link_addr:
            return False
        return ' США' in link_addr.text or ' US' in link_addr.text
    except (ValueError, RuntimeError):
        return False


def get_csv(asins):
    r = requests.get('https://proxy.webshare.io/api/v2/proxy/list/?mode=direct', headers={
        'Authorization': 'Token 5c847yo2t58sg0r9hvjjhr2vajjq413zxirqz3wf',
    })
    proxies = r.json()
    us_proxy = next(filter(check_proxy, [ProxyConf(x) for x in proxies['results']]))
    print(us_proxy)
    wd = base_chrome_init(
        False,
        proxy_conf={
            'user': us_proxy['username'],
            'pass': us_proxy['password'],
            'addr': us_proxy['proxy_address'],
            'port': us_proxy['port'],
        },
        capsolver_api_key='012e7e2f937d9fc673a3d0db5adba77c',
    )
    wd.get('https://members.helium10.com/user/signin', wait=False)
    while wd.current_url == 'https://members.helium10.com/user/signin':
        wd.wait_for_loading('#loginform-email')
        wd.type('#loginform-email', 'info@nyle.ai', clear=True)
        wd.wait_for_loading('#loginform-password')
        wd.type('#loginform-password', 'Gnomio7&', clear=True)
        print(asyncio.run(wd.recaptcha_solve_capsolver()))
        wd.submit('#loginform-password')
        sleep(2)
    wd.get('https://members.helium10.com/cerebro?accountId=1545531519')

    # wd.type('', ','.join(asins))

    # Scrap
    input('end?')

    wd.full_close()


get_csv(('', ''))
