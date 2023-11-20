import datetime
import re
from builtins import Exception
from json import JSONDecoder, JSONEncoder
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Union

from alive_progress import alive_bar

from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium.common import JavascriptException, InvalidSessionIdException, TimeoutException

import database
import parser
import state
from functions import RetryException, user_emulate, chrome_init, captcha_solve, WebDriver

import logging


logger = logging.getLogger('reviews')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'reviews.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class StopScript(Exception):
    pass


params = {
    'sortBy': ['helpful', 'recent'],
    'reviewerType': ['all_reviews', 'avp_only_reviews'],
    'filterByStar': ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
    'formatType': ['all_formats', 'current_format'],
    'mediaType': ['all_contents', 'media_reviews_only'],
    'pageNumber': list(range(1, 11)),
}
params_len = 1
for key in params:
    params_len *= len(params[key])
ev = Event()

webdriver: Union[None, WebDriver] = None
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
            print(e)
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
        print(ex)
        return False


def send_request(asin, seed):
    if seed < params_len:
        current_params = {
            'scope': 'reviewsAjax3',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 13,
            'asin': asin,
        }
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
                print(f'broken result. asin: {asin}')
                raise RetryException('Broken result')
        except (JavascriptException, RetryException, TimeoutException) as e:
            logger.error('Exception', exc_info=True, stack_info=True)
            print(e)
            print('something went wrong. retry... ')
            sleep(1)
            try:
                webdriver.reload()
                print('reloaded')
                if not captcha_solve(webdriver):
                    logger.error('Captcha error')
                    raise Exception('Captcha error')
                webdriver.reload()
                webdriver.activate_jquery()
                res = webdriver.execute_script("return " + ajax)
                if not res or 'BAAAAAAD ASIN!' in res:
                    print(f'bad asin :( {asin}, seed={seed}')
                    logger.error(f'Bad ASIN={asin}, seed={seed}; params={current_params}')
                    raise Exception('Bad ASIN')
                print('success. continue')
            except Exception as e:
                logger.error(f'Exception: ASIN={asin}, seed={seed}; params={current_params}', exc_info=True, stack_info=True)
                print('ERROR:', e)
                return False

        process_data(asin, seed, res)
    return True


def main(asin, conn_reader=None):
    print('loading webdriver')
    global webdriver, ev

    ev = Event()
    webdriver = chrome_init(goto='https://amazon.com/product-reviews/B08JPS4554')
    webdriver.activate_jquery()

    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        try:
            webdriver.driver.close()
        except:
            pass

    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev), daemon=True)
    user_emulate_thread.start()

    try:
        if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
            raise StopScript
        index = state.get_asin(asin)
        print(f'current asin: {asin} with index {index}')
        if index == -1:
            return True
        print('COLLECTING REVIEWS FOR ASIN', asin + ':')
        for params_seed in range(index, params_len):
            if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
                raise StopScript
            try:
                return send_request(asin, params_seed)
            except Exception as e:
                if 'Bad ASIN' not in str(e):
                    raise e
                logger.error(f'Skip {asin}; seed={params_seed}', exc_info=True, stack_info=True)
                print(f'Skip {asin}')
                continue
        return True
    except (InvalidSessionIdException, RetryException) as e:
        logger.error(f'Error!', exc_info=True, stack_info=True)
        print('ERROR: invalid session. ASIN will be collected later')
        try:
            ev.set()
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
        print('Script stopped')
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

