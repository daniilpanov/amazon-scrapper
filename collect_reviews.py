import re
from builtins import Exception
from json import JSONDecoder, JSONEncoder
from threading import Thread, Event
from time import sleep

import requests

from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium.common import JavascriptException, InvalidSessionIdException, TimeoutException

import database
import parser
import state
from functions import RetryException, user_emulate, base_chrome_init

import logging

from helpers import log, parse_args

logger = logging.getLogger('reviews')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'reviews.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


params = {
    'sortBy': ['helpful', 'recent'],
    'reviewerType': ['all_reviews', 'avp_only_reviews'],
    'filterByStar': ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
    'formatType': ['all_formats', 'current_format'],
    'mediaType': ['all_contents', 'media_reviews_only'],
    'pageNumber': list(range(1, 11)),
}
requests_counter = 0
params_len = 1
for key in params:
    params_len *= len(params[key])

url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt'

jsd = JSONDecoder()
jse = JSONEncoder()


def write_data(asin, seed, write_data_res):
    df = DataFrame(write_data_res, columns=[
        'review_id', 'product_url', 'asin',
        'date', 'country', 'name', 'title',
        'content', 'rating', 'helpful', 'options',
        'scrap_datetime',
    ])
    database.write_reviews(df)
    state.write_asin(asin, seed)


def process_data(asin, seed, process_data_res):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', process_data_res.strip())
        try:
            raw = list(map(
                lambda s: jsd.decode(s.strip()),
                [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()],
            ))
        except Exception as e:
            logger.error(f'Exception on div revs of [{asin}] [seed={seed}]', exc_info=True)
            log(e)
            return False
        data_with_quantity = None
        for item in raw:
            if len(item) >= 3 and item[1] == '#filter-info-section':
                data_with_quantity = item[2]
                break
        if not data_with_quantity:
            logger.warning(f'{asin} has noone review [params={seed}]')
            return False

        res = []

        for item in raw:
            if len(item) < 3 or item[1] != "#cm_cr-review_list" or not item[2].strip():
                continue
            item_parser = BeautifulSoup(item[2].strip(), features='html.parser')
            if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
                    or item_parser.find('div', class_='a-divider-section') \
                    or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                continue
            res.append(parser.parse_reviews(asin, item[2].strip()))
        write_data(asin, seed, res)
        return True
    except Exception as ex:
        log(ex)
        return False


def send_request(webdriver, asin, seed):
    if seed >= params_len:
        return True

    global requests_counter

    current_params = {
        'scope': 'reviewsAjax{}'.format(requests_counter),
        'reftag': 'cm_cr_arp_d_viewopt_srt',
        'pageSize': 13,
        'asin': asin,
    }
    requests_counter += 1
    s = seed
    for i in params:
        length = len(params[i])
        current_params[i] = params[i][s % length]
        s //= length

    ajax = f"$.post(\"{url}\", " \
           + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in current_params.items()]) + "\"}" \
           + ", null, 'text');"

    try:
        res = webdriver.execute_script("return " + ajax)
        if not res or 'BAAAAAAD ASIN!' in res:
            logger.warning(f'Broken result! ASIN: {asin}, SEED: {seed}')
            log(f'broken result. ASIN: {asin}')
            return False
    except (JavascriptException, RetryException, TimeoutException) as e:
        logger.error('Exception', exc_info=True, stack_info=True)
        log(e)
        log('something went wrong. send this ASIN to the end of a queue')
        return False

    process_data(asin, seed, res)


def collect(asin):
    if state.get_asin(asin) == -1:
        return True
    log('loading webdriver')
    ev = Event()
    webdriver = base_chrome_init(goto='https://amazon.com/product-reviews/B08JPS4554')
    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev), daemon=True)

    try:
        webdriver.activate_jquery()
        user_emulate_thread.start()

        index = state.get_asin(asin)
        log(f'current asin: {asin} with index {index}')
        if index == -1:
            return True
        log('COLLECTING REVIEWS FOR ASIN', asin + ':')
        for params_seed in range(index, params_len):
            try:
                if not send_request(webdriver, asin, params_seed):
                    logger.error(f'Skip {asin}; seed={params_seed}', exc_info=True, stack_info=True)
                    log(f'Skip {asin}')
                    return False
            except Exception as e:
                if 'Bad ASIN' not in str(e):
                    raise e
                logger.error(f'Skip {asin}; seed={params_seed}', exc_info=True, stack_info=True)
                log(f'Skip {asin}')
                return False
        return True
    except (InvalidSessionIdException, RetryException) as e:
        logger.error(f'Error!', exc_info=True, stack_info=True)
        log('ERROR: invalid session. ASIN will be collected later')
        try:
            ev.set()
            if user_emulate_thread.is_alive():
                user_emulate_thread.join()
        except:
            pass
        try:
            webdriver.driver.close()
        except:
            pass
        sleep(10)
        return False
    except KeyboardInterrupt:
        log('Script stopped')
        return False
    finally:
        try:
            ev.set()
            if user_emulate_thread.is_alive():
                user_emulate_thread.join()
        except:
            pass
        try:
            webdriver.driver.close()
        except:
            pass


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)

    res = False
    c = 99
    try:
        while not res and c > 0:
            res = collect(params_dict['asin'])
            c -= 1
    except KeyError:
        log('No ASIN error!')
    else:
        if 'user' in params_dict:
            if res or c == 99:
                requests.post('http://localhost:8080/send_msg', {
                    'msg': f'Reviews of ASIN {params_dict["asin"]} collected!',
                    'uid': params_dict['user'],
                })
            else:
                requests.post('http://localhost:8080/send_msg', {
                    'msg': f'Reviews of ASIN {params_dict["asin"]} did NOT collected.',
                    'uid': params_dict['user'],
                })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
