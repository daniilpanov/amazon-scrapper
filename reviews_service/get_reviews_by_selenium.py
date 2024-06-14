import datetime
import time
import typing
from threading import Thread

import pytz
from selenium.common import WebDriverException

import helpers
import settings
from proxies_service.proxies_manager import AmazonProxy
from .parse import *
from functions import WebDriver, base_chrome_init


class ScrapError(Exception):
    pass


class BadAsinError(Exception):
    pass


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
    # current process
    page: int = 1
    index: int = 0
    # collect reviews config
    asin: str
    keywords: str
    domain: str
    index: int
    current_format: bool
    canonical_link: str | None
    # products ?
    is_full: bool = False
    aspects_collect: bool
    media_collect: bool
    target_task_create: bool
    # queue helping to do async results loading
    data_queue: Queue
    # automotive
    automotive: bool = True  # auto send request to AI
    # END objprops

    def __new__(cls, queue, asin, keywords='', domain='amazon.com', index=0, current_format=True, canonical_link=None,
                full_collect_config=False, auto_send_to_ai=False):
        if not cls._inst:
            cls._inst = super(ReviewsCollector, cls).__new__(cls)
        inst = cls._inst
        inst.data_queue = queue
        inst.asin = asin
        inst.keywords = keywords
        inst.domain = domain
        inst.index = index
        inst.current_format = current_format
        inst.canonical_link = canonical_link
        # optional: full product parsing
        print(full_collect_config)
        if isinstance(full_collect_config, dict):
            print('ok')
            inst.is_full = True
            inst.aspects_collect = full_collect_config.get('aspects_collect', False)
            inst.media_collect = full_collect_config.get('media_collect', False)
            inst.target_task_create = full_collect_config.get('target_task_create', False)
        # automatic send data to AI
        inst.automotive = auto_send_to_ai
        return cls._inst

    @classmethod
    def get_default(cls):
        return cls._inst

    def _update_proxy_conf(self, proxy_conf=None):
        if isinstance(proxy_conf, dict):
            self.proxy = AmazonProxy.to_str(proxy_conf)
            self.cookies = proxy_conf.get('cookies')
            self.ua = proxy_conf.get('useragent', settings.ua.random)
        else:
            self.proxy = proxy_conf or settings.WEB_PROXY
            self.ua = settings.ua.random
            self.cookies = None

    def update_wd(self):
        url = self.wd.current_url if self.wd else f'https://www.{self.domain}'
        proxy = helpers.get_proxy()
        self._update_proxy_conf(proxy)
        self.wd = base_chrome_init(
            False,
            goto=url,
            proxy=self.proxy,
            user_agent=self.ua,
            cookies=self.cookies,
        )
        self.wd.change_loc()
        return self.wd

    def send_request(self):
        current_params = {
            'formatType': 'current_format' if self.current_format else '',
            'filterByAge': '',
            'pageNumber': self.page,
            'filterByLanguage': '',
            'filterByKeyword': self.keywords,
            'shouldAppend': 'undefined',
            'deviceType': 'desktop',
            'canShowIntHeader': 'undefined',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 10,
            'asin': self.asin,
            'scope': 'reviewsAjax{}'.format(ReviewsCollector.requests_counter),
        }
        ReviewsCollector.requests_counter += 1
        s = self.index
        for i in ReviewsCollector.params:
            length = len(ReviewsCollector.params[i])
            current_params[i] = ReviewsCollector.params[i][s % length]
            s //= length

        try:
            ajax = f"$.post(\"https://www.{self.domain}/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt\", " \
                   + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in current_params.items()]) + "\"}" \
                   + ", null, 'text');"
            res = self.wd.execute_script('return ' + ajax)
            if not res or 'BAAAAAAD ASIN!' in res:
                raise BadAsinError
            try:
                return process_req1(self.asin, res, self.domain, self.data_queue)
            except UnknownParseError as e:
                raise ScrapError from e
        except Exception as e:
            print(f'[send_request({self.asin})] Exception occurred: {e}')
            raise ScrapError

    def iteration(self, index, page):
        self.index = index
        self.page = page
        try:
            if not self.send_request():
                if not self.send_request():
                    return None
        except ScrapError:
            return False
        return True


def load_reviews(asin, keywords='', domain='amazon.com', index=0, current_format=True, canonical_link=None, full=None):
    queue = Queue()
    writer_thr = Thread(target=write_data, args=(queue,))
    writer_thr.start()
    scraper = ReviewsCollector(queue, asin, keywords, domain, index, current_format, canonical_link, full)
    scraper.update_wd()
    if scraper.is_full:
        scraper.wd.get('https://www.' + domain + '/dp/' + asin)
        html = scraper.wd.get_page_source()
        soup = BeautifulSoup(html, features='lxml')
        data = parser.parse_product(asin, soup, domain=domain)
        json_data = dict(
            zip(('asin', 'product_url', 'canonical_link', 'product_title', 'product_descr', 'picture_url',
                 'parse_datetime', 'features', 'top_5_phrases', 'product_price'), data))
        json_data['parse_datetime'] = json_data['parse_datetime'].isoformat()

        if scraper.aspects_collect:
            aspects = parser.parse_aspects(asin, soup)
            if aspects:
                aspects = [dict(zip(('Aspect', 'positive', 'negative'), aspect)) for aspect in aspects]
                requests.post('http://localhost:8832/products/set_result/aspects/' + asin, json=aspects)

        if scraper.media_collect:
            media_data = parser.parse_media_links(soup)
            if media_data:
                json_data['media_data'] = media_data
        else:
            media_data = None
        requests.post('http://localhost:8832/products/set_result/card/' + asin, json=json_data)

        if media_data and scraper.target_task_create:
            requests.post('http://localhost:8832/products/target/collect/' + asin)

        if not canonical_link:
            scraper.canonical_link = canonical_link = json_data['canonical_link'].replace('/dp/', '/product-reviews/', 1)
    scraper.wd.get(canonical_link or 'https://www.' + domain + '/product-reviews/' + asin)
    page = 1
    try:
        while ReviewsCollector.params_len - index > 5:
            try:
                for index in range(index, ReviewsCollector.params_len):
                    _break = False
                    for page in range(page, 11):
                        _iter = scraper.iteration(index, page)
                        if not _iter:
                            if _iter is False:
                                _break = True
                            break
                    page = 1
                    if _break:  # change proxy
                        break
            except WebDriverException:
                pass
            time.sleep(5)
            scraper.update_wd()
    finally:
        if ReviewsCollector.params_len - index < 5:
            print(requests.post(
                'http://45.14.245.223:1802/new_collection/',
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                json={
                    'name': 'Collected-' + asin,
                    'date': datetime.datetime.now(pytz.UTC).date().isoformat(),
                    'asins': [asin],
                },
            ))
        queue.put(None)
        writer_thr.join()


def close():
    inst = ReviewsCollector.get_default()
    if inst and inst.wd:
        inst.wd.full_close()
