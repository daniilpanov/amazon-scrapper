import json
import re
from json import JSONDecodeError
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup

import helpers
import parser
from proxies_service.proxies_manager import AmazonProxy


def write_data(q: Queue):
    data = -1
    try:
        while data:
            data = q.get()
            # requests.post('http://localhost:8832/products/set_result/reviews', json=data)
            print('[write_res]:', data)
    except KeyboardInterrupt:
        print('ok??')
        while not q.empty() and data:
            data = q.get()
            # requests.post('http://localhost:8832/products/set_result/reviews', json=data)
            print('[__write_res__]', data)
        raise


class RequestsEndedException(Exception):
    pass


params = {
    'sortBy': ['', 'recent'],
    'reviewerType': ['', 'avp_only_reviews'],
    'filterByStar': ['', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
    'mediaType': ['', 'media_reviews_only'],
}
requests_counter = 0
params_len = 1
for key in params:
    params_len *= len(params[key])


def get_curr_params(asin, page, keywords, curr_format, seed):
    p = {
        'formatType': 'current_format' if curr_format else '',
        'filterByAge': '',
        'pageNumber': page,
        'filterByLanguage': '',
        'filterByKeyword': keywords,
        'shouldAppend': 'undefined',
        'deviceType': 'desktop',
        'canShowIntHeader': 'undefined',
        'reftag': 'cm_cr_arp_d_viewopt_srt',
        'pageSize': 10,
        'asin': asin,
        'scope': 'reviewsAjax{}'.format(requests_counter),
    }
    s = seed
    for i in params:
        length = len(params[i])
        p[i] = params[i][s % length]
        s //= length
    return p


def req1(asin, keywords, domain, index, current_format, page, proxy, canonical_link=None):
    global requests_counter
    requests_counter += 1
    res = requests.post(
        f'https://www.{domain}/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt',
        get_curr_params(asin, page, keywords, current_format, index),
        headers=helpers.get_request_headers(True, domain, canonical_link, proxy['useragent']),
        cookies=proxy['cookies'],
        proxies={
            'http://': AmazonProxy.to_str(proxy),
            'https://': AmazonProxy.to_str(proxy),
        },
    )
    if not res or res.status_code != 200:
        return None
    return res.text


def process_req1(asin, response, domain, q):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', response.strip())
        try:
            raw = []
            for s in [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()]:
                try:
                    raw.append(json.loads(s.strip()))
                except JSONDecodeError:
                    pass
        except Exception as e:
            print(e)
            return False
        data_with_quantity = None
        for item in raw:
            if len(item) >= 3 and item[1] == '#filter-info-section':
                data_with_quantity = item[2]
                break
        if not data_with_quantity:
            return False

        res = []

        for item in raw:
            if len(item) < 3 or item[1] != "#cm_cr-review_list" or not item[2].strip():
                continue
            item_parser = BeautifulSoup(item[2].strip(), features='lxml')
            if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
                    or item_parser.find('div', class_='a-divider-section') \
                    or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                continue
            res.append(parser.parse_reviews(asin, item[2].strip(), domain))
        if not res:
            print(process_data_res)
        q.put(res)
        return bool(res) - (not bool(res))
    except Exception as ex:
        print(ex)
        return False


def req2(asin, keywords, domain, index, current_format, page, proxy, canonical_link=None):
    global requests_counter
    requests_counter += 1
    res = requests.get(
        canonical_link or f'https://www.{domain}/product-reviews/{asin}',
        get_curr_params(asin, page, keywords, current_format, index),
        headers=helpers.get_request_headers(True, domain, canonical_link, proxy['useragent']),
        cookies=proxy['cookies'],
        proxies={
            'http://': AmazonProxy.to_str(proxy),
            'https://': AmazonProxy.to_str(proxy),
        },
    )
    if not res or res.status_code != 200:
        return None
    return res.text


def process_req2(asin, response, domain, q):
    soup = BeautifulSoup(response, features='lxml')
    if soup.find(attrs={'id': 'authportal-center-section'}) or soup.select('body > div > div[style*="width: 350px"]'):
        return None
    reviews = soup.find_all('div', {'data-hook': 'review'})
    res = []
    for review in reviews:
        res.append(parser.parse_reviews(asin, review, domain))
    if res:
        q.put(res)
    return bool(res) - (not bool(res))


def load_reviews(asin, keywords='', domain='amazon.com', index=0, current_format=True, canonical_link=None):
    queue = Queue()
    writer_thr = Thread(target=write_data, args=(queue,))
    writer_thr.start()
    while proxy := helpers.get_proxy(True):
        print('[current_proxy]:', proxy)
        _exit = True
        for index in range(index, params_len):
            print('[current_index]:', index)
            _break = False
            for i in range(1, 11):
                print('[current_page]:', i)
                print('req2')
                reqq = res = req2(asin, keywords, domain, index, current_format, i, proxy, canonical_link)
                if res:
                    if not canonical_link:
                        print('[try to found canonical]')
                        soup = BeautifulSoup(res, features='lxml')
                        canonical_link_item = soup.select_one('link[rel="canonical"]')
                        if canonical_link_item:
                            print('found!')
                            canonical_link = canonical_link_item['href'] + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
                            print(canonical_link)
                            helpers.deprecate_proxy(proxy['addr'])
                            _exit = False
                            _break = True
                            break
                    res = process_req2(asin, res, domain, queue)
                if res == -1:
                    print('no data')
                    with open('test.html', 'w', encoding='utf-8') as f:
                        f.write(reqq)
                    break
                if not res:
                    print('captcha!')
                    helpers.deprecate_proxy(proxy['addr'])
                    _exit = False
                    _break = True
                    break
            if _break:
                break
        if _exit:
            break
    queue.put(None)
    writer_thr.join()
    raise RequestsEndedException


if __name__ == '__main__':
    load_reviews('B08YKB6VMN', canonical_link='https://www.amazon.com/SIMO-Portable-International-Multi-Carrier-Connected/product-reviews/B08YKB6VMN/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
