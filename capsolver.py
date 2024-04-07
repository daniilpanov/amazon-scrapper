from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests

import database
from functions import base_chrome_init


def get_proxies_list():
    r = requests.get(
        'https://proxy.webshare.io/api/v2/proxy/list/download/fylqlgwtujdvttnfaorztplrphexumivqxzmwiof/-/any/username/direct/-/')
    if r.status_code == 200:
        res = []
        for i in r.text.splitlines():
            res.append(i.split(':'))
        return res
    sleep(10)
    return get_proxies_list()


def chrome_init(arr, proxy):
    ch = base_chrome_init(goto='https://amazon.com', proxy=proxy)
    processed = {}
    for datum in ch.driver.get_cookies():
        processed[datum['name']] = datum['value']
    try:
        database.db('amazon_data')['__cookies'].insert_one(processed)
    except Exception:
        pass
    arr.append(ch)


def main():
    old_proxy_list = None
    proxies = get_proxies_list()
    chromes = []

    while True:
        print(proxies, old_proxy_list)
        if old_proxy_list != proxies:
            print('Proxies need update!')
            with ThreadPoolExecutor(len(proxies)) as threader:
                for chrome in chromes:
                    threader.submit(chrome.full_close)
            print('Chromes closed!')
            chromes = []
            with ThreadPoolExecutor(len(proxies)) as threader:
                for i in proxies:
                    threader.submit(chrome_init, chromes, f'socks5://{i[2]}:{i[3]}@{i[0]}:{i[1]}')
            print('Chromes inited!')
            sleep(5)
        with ThreadPoolExecutor(len(proxies)) as threader:
            for chrome in chromes:
                threader.submit(chrome.get, 'https://amazon.com')
        print('Captcha solved!')
        sleep(1)
        old_proxy_list = proxies.copy()
        proxies = get_proxies_list()


if __name__ == '__main__':
    main()
