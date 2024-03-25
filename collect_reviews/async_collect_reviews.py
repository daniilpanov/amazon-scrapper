import asyncio
import json
import re
import urllib
from builtins import Exception
from json import JSONDecodeError
from queue import Queue
from threading import Thread

from bs4 import BeautifulSoup
from pandas import DataFrame

import database
import parser
from functions import base_chrome_init, WebDriver

from helpers import log
import tasks


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
data_queue = Queue()
logging_queue = Queue()


def write_data(q: Queue):
    while True:
        data_res = q.get()
        if data_res is None:
            return
        df = DataFrame(data_res, columns=[
            'review_id', 'product_url', 'asin',
            'date', 'country', 'name', 'title',
            'content', 'rating', 'helpful', 'options',
            'scrap_datetime',
        ])
        database.write_reviews(df)


def logger(q: Queue):
    while True:
        data_res = q.get()
        if not data_res:
            return


writer_thr = Thread(target=write_data, args=(data_queue,))
logger_thr = Thread(target=logger, args=(logging_queue,))


def process_data(asin, seed, process_data_res, domain):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', process_data_res.strip())
        try:
            raw = []
            for s in [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()]:
                try:
                    raw.append(json.loads(s.strip()))
                except JSONDecodeError:
                    pass
        except Exception as e:
            log(e)
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
            logging_queue.put(process_data_res)
        data_queue.put(res)
        return bool(res) - (not bool(res))
    except Exception as ex:
        log(ex)
        return False


def process_data_from_page(asin, seed, process_data_res, domain):
    soup = BeautifulSoup(process_data_res, features='lxml')
    reviews = soup.find_all('div', {'data-hook': 'review'})
    res = []
    for review in reviews:
        res.append(parser.parse_reviews(asin, review, domain))
        data_queue.put(res)
        logging_queue.put(res)
    return bool(res) - (not bool(res))


def send_request(sess: WebDriver, asin, seed, page, keywords='', domain='amazon.com', current_format=True):
    if seed >= params_len:
        return True

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
        res = sess.execute_script("return " + ajax)
        if not res or 'BAAAAAAD ASIN!' in res:
            return False
        return process_data(asin, seed, res, domain)
    except Exception as e:
        log(e)
        log('something went wrong. send this ASIN to the end of a queue')
        return False


async def collect(_id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    if index == -1:
        return -1
    log('loading Requests')
    webdriver = base_chrome_init(goto=f'https://{domain}/')
    webdriver.change_loc(domain=domain)
    webdriver.get(webdriver.current_url
                  + f'product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
    try:
        webdriver.get(webdriver.get_element('link[rel="canonical"]').get_attribute('href')
                      + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
    except Exception:
        pass

    soup = BeautifulSoup(webdriver.get_page_source(), features='lxml')
    reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
    reviews_count = 0
    reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
    if len(reviews_count_part) == 2:
        reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
    print('count:', reviews_count)

    try:
        log('COLLECTING REVIEWS FOR ASIN', asin + ':')
        webdriver.execute_script(f'$.get("https://www.{domain}/hz/rhf?currentPageType=CustomerReviews&currentSubPageType=remoteProduct&excludeAsin={asin}&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl={urllib.parse.quote(webdriver.current_url.replace(f"https://{domain}", "").replace(f"https://www.{domain}", ""))}")')

        def send_wrapper(s, a, _p, _i, k, d, cf, retry=True):
            res = send_request(s, a, _p, _i, k, d, cf)
            if not res and retry:
                # await sess.init()
                return send_wrapper(s, a, _p, _i, k, d, cf, False)
            return res

        try:
            for params_seed in (range(index, params_len) if reviews_count > 100 else [0]):
                for i in range(1, 11):
                    send_wrapper(webdriver, asin, params_seed, i, keywords, domain, current_format)
                index += 1
            webdriver.full_close()
            tasks.get_task(_id).add_progress(1)
            return -1
        except Exception as e:
            if 'Bad ASIN' not in str(e):
                webdriver.full_close()
                raise e
            log(f'Skip {asin}')
            webdriver.full_close()
            tasks.get_task(_id).success = False
            return index
    except KeyboardInterrupt:
        log('Script stopped')
        webdriver.full_close()
        raise
