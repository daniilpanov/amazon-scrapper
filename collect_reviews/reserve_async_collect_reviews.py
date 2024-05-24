import datetime
import json
import re
import urllib
from builtins import Exception
from concurrent.futures import ThreadPoolExecutor
from json import JSONDecodeError
from queue import Queue
from threading import Thread
from time import sleep

import pytz
import requests
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException, StaleElementReferenceException, WebDriverException

import db_mongo
import parser
import settings
import tasks_manager
from functions import base_chrome_init, WebDriver, Amazon404Exception
from helpers import log

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
wds: dict[str, WebDriver] = {}
threader = ThreadPoolExecutor(settings.THREADS['reviews'])


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


def send_request(asin, seed, page, keywords='', domain='amazon.com', current_format=True):
    if seed >= params_len:
        return True

    global wds
    if asin not in wds:
        return False
    wd = wds[asin]

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
        res = wd.execute_script("return " + ajax)
        if not res or 'BAAAAAAD ASIN!' in res:
            return False
        return process_data(asin, seed, res, domain)
    except Exception as e:
        log(f'[send_request({asin})] Exception occurred: {e}')
        return False


def wd_init(domain, asin):
    global wds
    if asin in wds:
        wds[asin].full_close()
    log('loading webdriver for', asin)
    try:
        wds[asin] = base_chrome_init(goto=f'https://{domain}/')
        wds[asin].change_loc(domain=domain)
        return wds[asin]
    except Exception as e:
        with open('log3', 'w', encoding='utf-8') as f:
            f.write('ASIN: ' + asin + '\nТип исключения: ' + type(e).__name__ + '\nСообщение: ' + str(e) + '\n\n')
            tb = e.__traceback__
            while tb:
                f.write(
                    f'Имя файла: {tb.tb_frame.f_code.co_filename}, строка {tb.tb_lineno}, метод: {tb.tb_frame.f_code.co_name}\n')
                tb = tb.tb_next
        sleep(5)
        return wd_init(domain, asin)


def collect(ev, _id, asin, keywords='', domain='amazon.com', params_seed=0, current_format=True):
    task = tasks.get_task(_id)
    wd = None
    try:
        global wds
        writer_thr = Thread(target=write_data, args=(data_queue,))
        logger_thr = Thread(target=logger, args=(logging_queue,))
        writer_thr.start()
        logger_thr.start()

        if params_seed == -1:
            return -1
        prod_link = None
        while True:
            try:
                wd = wd_init(domain, asin)
                prod_link = (wd.current_url
                             + f'product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
                wd.get(prod_link)
                canonical_link_item = wd.get_element('link[rel="canonical"]')
                if canonical_link_item:
                    canonical_link = canonical_link_item.get_attribute('href')
                    if canonical_link:
                        prod_link = canonical_link + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
                        wd.get(prod_link)
            except (NoSuchElementException, StaleElementReferenceException, KeyError):
                pass
            except WebDriverException:
                continue
            try:
                soup = BeautifulSoup(wd.get_page_source(), features='lxml')
            except WebDriverException:
                continue
            break
        reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
        reviews_count = 0
        reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
        if len(reviews_count_part) == 2:
            reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
        log('count:', reviews_count)

        try:
            log('COLLECTING REVIEWS FOR ASIN', asin + ':')
            while True:
                try:
                    wd.execute_script(
                        f'$.get("https://www.{domain}/hz/rhf?currentPageType=CustomerReviews'
                        f'&currentSubPageType=remoteProduct&excludeAsin={asin}&fieldKeywords='
                        f'&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias='
                        f'''&isAUI=1&cardJSPresent=true&pageUrl={urllib.parse.quote(
                            wd.current_url.replace(f"https://{domain}", "")
                            .replace(f"https://www.{domain}", "")
                        )}")'''
                    )
                    break
                except WebDriverException:
                    sleep(1)
                    wd = wd_init(domain, asin)
                    wd.get(prod_link)
                    continue

            def send_wrapper(a, _p, _i, k, d, cf):
                global wds
                if a in wds:
                    w = wds[a]
                else:
                    w = wd_init(d, a)
                res = send_request(a, _p, _i, k, d, cf)
                if not res:
                    u = w.driver.current_url
                    w.full_close()
                    while True:
                        try:
                            w = wd_init(d, a)
                            w.get('https://' + d)
                            w.get(u)
                            break
                        except Exception as e:
                            with open('log2', 'w', encoding='utf-8') as f:
                                f.write('ASIN: ' + a + '\nТип исключения: ' + type(e).__name__ + '\nСообщение: ' + str(e) + '\n\n')
                                tb = e.__traceback__
                                while tb:
                                    f.write(
                                        f'Имя файла: {tb.tb_frame.f_code.co_filename}, строка {tb.tb_lineno}, метод: {tb.tb_frame.f_code.co_name}\n')
                                    tb = tb.tb_next
                    return send_wrapper(a, _p, _i, k, d, cf)
                return res

            try:
                for params_seed in (range(params_seed, params_len) if reviews_count > 100 else [0]):
                    if ev and ev.is_set():
                        break
                    for i in range(1, 11):
                        log('seed:', params_seed)
                        send_wrapper(asin, params_seed, i, keywords, domain, current_format)
                    if task:
                        task.result['asins_progress'][asin] = params_seed
                wd.full_close()
                del wds[asin]
                if task:
                    requests.post('http://45.14.245.223:1802/new_collection/', json={
                        'name': task.alias,
                        'date': datetime.datetime.now(pytz.UTC).date().isoformat(),
                        'asins': [asin],
                    })
                    task.result['asins'].append(asin)
                    task.result['count'].append(
                        database.db('amazon_data')['customer_reviews'].count_documents({'asin': asin})
                    )
                    task.add_progress(1)
                data_queue.put(None)
                logging_queue.put(None)
                writer_thr.join()
                logger_thr.join()
                return -1
            except Exception as e:
                if 'Bad ASIN' not in str(e):
                    wd.full_close()
                    raise e
                log(f'Skip {asin}')
                wd.full_close()
                del wds[asin]
                task = tasks.get_task(_id)
                task.success = False
                task.ended_at = datetime.datetime.now(pytz.UTC)
                data_queue.put(None)
                logging_queue.put(None)
                writer_thr.join()
                logger_thr.join()
                return params_seed
        except KeyboardInterrupt:
            log('Script stopped')
            wd.full_close()
            del wds[asin]
            data_queue.put(None)
            logging_queue.put(None)
            writer_thr.join()
            logger_thr.join()
            raise
    except Amazon404Exception:
        if task:
            task.result['asins'].append(asin)
            task.result['count'].append('Not found')
            task.add_progress(1)
        if wd:
            wd.full_close()
        print('Not found:', asin)
    except Exception as e:
        with open('log', 'w', encoding='utf-8') as f:
            f.write('ASIN: ' + asin + '\nТип исключения: ' + type(e).__name__ + '\nСообщение: ' + str(e) + '\n\n')
            tb = e.__traceback__
            while tb:
                f.write(
                    f'Имя файла: {tb.tb_frame.f_code.co_filename}, строка {tb.tb_lineno}, метод: {tb.tb_frame.f_code.co_name}\n')
                tb = tb.tb_next


def start_sync(ev, _id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    threader.submit(collect, ev, _id, asin, keywords, domain, index, current_format)


async def start_async(ev, _id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    threader.submit(collect, ev, _id, asin, keywords, domain, index, current_format)
