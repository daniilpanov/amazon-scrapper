import asyncio
import json
import re
from builtins import Exception
from json import JSONDecodeError
from queue import Queue
from threading import Thread
from time import sleep

from bs4 import BeautifulSoup
from pandas import DataFrame

import database
import parser
from amazon_requests import Requests

from helpers import log, parse_args, send_bot_msg, end_task


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
        if not data_res:
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
        print(data_res)
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


async def send_request(sess: Requests, asin, seed, page, keywords='', domain='amazon.com', current_format=True):
    if seed >= params_len:
        return True

    current_params = {}
    s = seed
    for i in params:
        length = len(params[i])
        current_params[i] = params[i][s % length]
        s //= length

    try:
        res = await sess.get_reviews(asin, page, current_params, keywords, False, current_format=current_format)
        if not res or 'BAAAAAAD ASIN!' in res:
            log(f'broken result. ASIN: {asin}')
            return False
        return process_data_from_page(asin, seed, res, domain)
    except Exception as e:
        log(e)
        log('something went wrong. send this ASIN to the end of a queue')
        return False


async def collect(asin, keywords, user, domain, index=0, current_format=True):
    if index == -1:
        return -1
    log('loading Requests')
    sess = Requests(domain)

    soup = BeautifulSoup(await sess.get_reviews(asin, params={
        'formatType': 'current_format' if current_format else '',
    }, xmlhttp=False), features='lxml')
    reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
    while not reviews_count_element:
        soup = BeautifulSoup(await sess.get_reviews(asin, params={
            'formatType': 'current_format' if current_format else '',
        }, xmlhttp=False), features='lxml')
        reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')

    reviews_count = 0
    reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
    if len(reviews_count_part) == 2:
        reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
    print('count:', reviews_count)

    try:
        log('COLLECTING REVIEWS FOR ASIN', asin + ':')
        await sess.req(
            f'hz/rhf?currentPageType=CustomerReviews&currentSubPageType=remoteProduct&excludeAsin'
            f'={asin}&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns='
            f'&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl=https://{domain}'
            f'/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews',
            xmlhttp=True,
        )
        try:
            tasks = []
            for params_seed in (range(index, params_len) if reviews_count > 100 else [0]):
                for i in range(1, 11):
                    tasks.append(send_request(sess, asin, params_seed, i, keywords, domain, current_format))
                index += 1
            await asyncio.gather(*tasks)
            await sess.request.close()
            return -1
        except Exception as e:
            if 'Bad ASIN' not in str(e):
                await sess.request.close()
                raise e
            log(f'Skip {asin}')
            await sess.request.close()
            return index
    except KeyboardInterrupt:
        log('Script stopped')
        await sess.request.close()
        raise


async def start_reviews_collect(params_dict):
    res = 0
    try:
        res = await collect(
            params_dict['asin'], params_dict.get('keywords', ''),
            params_dict.get('user'), params_dict.get('domain', 'amazon.com'),
            res, params_dict.get('current_format', True),
        )
    except KeyError:
        log('No ASIN error!')
    except KeyboardInterrupt:
        log('Stop task')
        raise
    else:
        if 'user' in params_dict:
            if res == -1:
                send_bot_msg(
                    params_dict['user'],
                    f'Reviews of ASIN {params_dict["asin"]} collected!',
                )
            else:
                send_bot_msg(
                    params_dict['user'],
                    f'Reviews of ASIN {params_dict["asin"]} did NOT collected [max retry limit].',
                )
    finally:
        if 'id' in params_dict:
            end_task(params_dict['_id'])
    return res


if __name__ == '__main__':
    import sys
    p = parse_args(sys.argv)
    p.setdefault('asin', 'B094TDK36S')
    p.setdefault('domain', 'amazon.com')
    p.setdefault('current_format', False)
    writer_thr.start()
    logger_thr.start()
    asyncio.run(start_reviews_collect(p))
    data_queue.put(None)
    logging_queue.put(None)
    writer_thr.join()
    logger_thr.join()
