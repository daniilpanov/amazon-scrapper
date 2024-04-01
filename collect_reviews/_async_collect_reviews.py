import asyncio
import json
import re
import urllib
from asyncio import Semaphore
from builtins import Exception
from json import JSONDecodeError
from queue import Queue
from threading import Thread

from bs4 import BeautifulSoup
from pandas import DataFrame

import amazon_requests
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
        database.write_reviews(data_res)


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


async def send_request(sess: amazon_requests.Requests, asin, seed, page, keywords='', domain='amazon.com', current_format=True):
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
        res = await sess.get_reviews(asin, page, current_params, keywords, xmlhttp=True)
        if not res or 'BAAAAAAD ASIN!' in res:
            log('bad request! use full page')
            res = await sess.get_reviews(asin, page, current_params, keywords, xmlhttp=False)
            if not res or 'BAAAAAAD ASIN!' in res:
                return False
            return process_data_from_page(asin, seed, res, domain)
        return process_data(asin, seed, res, domain)
    except Exception as e:
        log(e)
        log('something went wrong. send this ASIN to the end of a queue')
        return False


async def collect(_id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    writer_thr.start()
    logger_thr.start()

    if index == -1:
        return -1
    log('loading Requests')
    sess = amazon_requests.Requests(domain)
    await sess.init()
    html = await sess.get_reviews(asin, xmlhttp=False)
    print(html)
    while not html:
        await sess.init()
        html = await sess.get_reviews(asin, xmlhttp=False)
    soup = BeautifulSoup(html, features='lxml')
    reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
    reviews_count = 0
    reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
    if len(reviews_count_part) == 2:
        reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
    print('count:', reviews_count)

    limit_semaphore = Semaphore(30)

    try:
        log('COLLECTING REVIEWS FOR ASIN', asin + ':')
        ru = f'www.{domain}/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
        await sess.req(f'hz/rhf?currentPageType=CustomerReviews&currentSubPageType=remoteProduct&excludeAsin={asin}&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl={ru}')

        async def send_wrapper(s, a, _p, _i, k, d, cf, retry=True):
            async with limit_semaphore:
                res = await send_request(s, a, _p, _i, k, d, cf)
                if not res and retry:
                    await sess.init()
                    return await send_wrapper(s, a, _p, _i, k, d, cf, False)
            return res

        try:
            req_tasks = []
            for params_seed in (range(index, params_len) if reviews_count > 100 else [0]):
                for i in range(1, 11):
                    req_tasks.append(send_wrapper(sess, asin, params_seed, i, keywords, domain, current_format))
                index += 1
            await asyncio.gather(*req_tasks)
            await sess.request.close()
            task = tasks.get_task(_id)
            task.add_progress(1)
            task.result.append(asin)
            data_queue.put(None)
            logging_queue.put(None)
            writer_thr.join()
            logger_thr.join()
            return -1
        except Exception as e:
            if 'Bad ASIN' not in str(e):
                if sess.request:
                    await sess.request.close()
                raise e
            log(f'Skip {asin}')
            if sess.request:
                await sess.request.close()
            tasks.get_task(_id).success = False
            data_queue.put(None)
            logging_queue.put(None)
            writer_thr.join()
            logger_thr.join()
            return index
    except KeyboardInterrupt:
        log('Script stopped')
        if sess.request:
            await sess.request.close()
        data_queue.put(None)
        logging_queue.put(None)
        writer_thr.join()
        logger_thr.join()
        raise
