import typing
from threading import Thread

from selenium.common import WebDriverException

import helpers
import settings
from proxies_service.proxies_manager import AmazonProxy
from .parse import *
from functions import WebDriver, base_chrome_init


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
wd: WebDriver | None = None


class ReviewsCollector:
    # BEGIN classprops
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
    _inst: typing.Self | None = None
    # END classprops
    # BEGIN objprops
    wd: WebDriver | None = None
    proxy: str | None = None
    ua: str
    cookies: dict | None = None
    domain: str = 'amazon.com'
    # END objprops

    def __new__(cls, domain='amazon.com'):
        if not cls._inst:
            cls._inst = super(ReviewsCollector, cls).__new__(cls)
        return cls._inst

    def update_proxy_conf(self, proxy_conf=None):
        if isinstance(proxy_conf, dict):
            self.proxy = AmazonProxy.to_str(proxy_conf)
            self.cookies = proxy_conf.get('cookies')
            self.ua = proxy_conf.get('useragent', settings.ua.random)
        else:
            self.proxy = proxy_conf or settings.WEB_PROXY
            self.ua = settings.ua.random
            self.cookies = None

    def update_wd(self):
        proxy = helpers.get_proxy()
        self.update_proxy_conf(proxy)
        self.wd = base_chrome_init(
            False,
            goto=f'https://www.{self.domain}',
            proxy=self.proxy,
            user_agent=self.ua,
            cookies=self.cookies,
        )
        wd.change_loc()
        return wd


def send_request(asin, seed, page, keywords='', domain='amazon.com', current_format=True, q=None):
    global requests_counter

    current_params = {
        'formatType': 'current_format' if current_format else '',
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
    requests_counter += 1
    s = seed
    for i in params:
        length = len(params[i])
        current_params[i] = params[i][s % length]
        s //= length

    try:
        ajax = f"$.post(\"https://www.{domain}/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt\", " \
               + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in current_params.items()]) + "\"}" \
               + ", null, 'text');"
        res = wd.execute_script('return ' + ajax)
        if not res or 'BAAAAAAD ASIN!' in res:
            return False
        return process_req1(asin, res, domain, q)
    except Exception as e:
        print(f'[send_request({asin})] Exception occurred: {e}')
        return False


def load_reviews(asin, keywords='', domain='amazon.com', index=0, current_format=True, canonical_link=None, retry=True, full=False):
    if not wd or not retry:
        update_wd()
    queue = Queue()
    writer_thr = Thread(target=write_data, args=(queue,))
    writer_thr.start()
    if isinstance(full, dict):
        wd.get('https://www.' + domain + '/dp/' + asin)
        html = wd.get_page_source()
        data = parser.parse_product(asin, html, domain=domain)
        if full.get('aspects'):
            aspects = parser.parse_aspects(asin, html)
            # if aspects:

        json_data = dict(zip(('asin', 'product_url', 'canonical_link', 'product_title', 'product_descr', 'picture_url',
                              'parse_datetime', 'features', 'top_5_phrases', 'product_price'), data))
        json_data['parse_datetime'] = json_data['parse_datetime'].isoformat()
        requests.post('http://localhost:8832/products/set_result/card/' + asin, json=json_data)
        if not canonical_link:
            canonical_link = json_data['canonical_link']
    wd.get(canonical_link or 'https://www.' + domain + '/product-reviews/' + asin)
    try:
        for index in range(index, params_len):
            for i in range(1, 11):
                if not send_request(asin, index, i, keywords, domain, current_format, queue):
                    return load_reviews(asin, keywords, domain, index, current_format, canonical_link, retry - 1)
    except WebDriverException as e:
        if retry:
            return load_reviews(asin, keywords, domain, index, current_format, canonical_link, retry - 1)
        print(e)
        return {'error': e, 'index': index}
    queue.put(None)
    writer_thr.join()
    return {}


def iteration(asin, keywords, domain, index, current_format, canonical_link, full, proxy, retry=True):
    try:
        if not wd or not retry:
            update_wd()
    except Exception as e:
        if retry:
            return iteration(asin, keywords, domain, index, current_format, canonical_link, full, proxy, False)
        return {'error': e, 'index': index}


def load_reviews(asin, keywords='', domain='amazon.com', index=0, current_format=True, canonical_link=None, full=False):
    queue = Queue()
    writer_thr = Thread(target=write_data, args=(queue,))
    writer_thr.start()
    while proxy := helpers.get_proxy(True):
        if iteration(asin, keywords, domain, index, current_format, canonical_link, full, proxy):
            break
    iteration(asin, keywords, domain, index, current_format, canonical_link, full, settings.WEB_PROXY)


def close():
    global wd
    if wd:
        wd.full_close()
        wd = None
