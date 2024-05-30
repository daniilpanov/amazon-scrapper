import time
import requests
from bs4 import BeautifulSoup

import db_mongo
import helpers
import settings
from proxies_service.proxies_manager import AmazonProxy


def get_html_by_request(asin, full_link=None, domain='amazon.com'):
    cookie = db_mongo.db('amazon_data')['__cookies'].find_one({'session-id': {'$exists': True}, 'sp-cdn': {'$exists': False}})
    del cookie['_id']
    r = requests.get(
        full_link or 'https://www.' + domain + '/dp/' + asin,
        cookies=cookie,
        headers=helpers.get_request_headers(domain=domain),
    )
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, features='lxml')
        if not helpers.check_captcha(soup):
            return soup
    r = requests.get(
        full_link or 'https://www.' + domain + '/dp/' + asin,
        cookies=cookie,
        headers=helpers.get_request_headers(domain=domain),
        proxies={
            'http': settings.WEB_PROXY,
            'https': settings.WEB_PROXY,
        },
    )
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, features='lxml')
        if not helpers.check_captcha(soup):
            return soup
    while proxy := helpers.get_proxy(True):
        print(proxy)
        try:
            for i in range(5):
                r = requests.get(
                    full_link or 'https://www.' + domain + '/dp/' + asin,
                    cookies=proxy['cookies'],
                    headers=helpers.get_request_headers(domain=domain),
                    proxies={
                        'http': AmazonProxy.to_str(proxy),
                        'https': AmazonProxy.to_str(proxy),
                    },
                )
                if r.status_code != 200:
                    time.sleep(1)
                    continue
                soup = BeautifulSoup(r.text, features='lxml')
                if helpers.check_captcha(soup):
                    break
                print(proxy)
                return soup
        except requests.exceptions.RequestException as e:
            print(e)
        helpers.deprecate_proxy(proxy['addr'])
        time.sleep(2)
    return None


if __name__ == '__main__':
    with open('test.html', 'w', encoding='utf-8') as f:
        res = get_html_by_request('B08YKB6VMN')
        print(res.find(attrs={'id': 'title'}))
        f.write(str(res))
