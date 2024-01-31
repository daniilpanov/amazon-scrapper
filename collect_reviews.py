import re
import urllib
from builtins import Exception
from json import JSONDecoder, JSONEncoder, JSONDecodeError
from threading import Thread, Event
from time import sleep

import requests

from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium.common import JavascriptException, InvalidSessionIdException, TimeoutException, NoSuchElementException

import database
import helpers
import parser
import state
from functions import RetryException, user_emulate, base_chrome_init

import logging

from helpers import log, parse_args, send_bot_msg

logger = logging.getLogger('reviews')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'reviews.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


params = {
    'sortBy': ['', 'recent'],
    'reviewerType': ['', 'avp_only_reviews'],
    'filterByStar': ['', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
    'formatType': ['', 'current_format'],
    'mediaType': ['', 'media_reviews_only'],
}
requests_counter = 0
params_len = 1
for key in params:
    params_len *= len(params[key])

url = '/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt'

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


def process_data(asin, seed, process_data_res, domain):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', process_data_res.strip())
        try:
            raw = []
            for s in [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()]:
                try:
                    raw.append(jsd.decode(s.strip()))
                except JSONDecodeError:
                    pass
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
            logger.warning(f'{asin} has none review [params={seed}]')
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
            res.append(parser.parse_reviews(asin, item[2].strip(), domain))
        write_data(asin, seed, res)
        return bool(res) - (not bool(res))
    except Exception as ex:
        log(ex)
        return False


def send_request(webdriver, asin, seed, page, keywords='', domain='amazon.com'):
    if seed >= params_len:
        return True

    global requests_counter

    current_params = {
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

    ajax = f"$.post(\"https://www.{domain}{url}\", " \
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

    return process_data(asin, seed, res, domain)


def collect(asin, keywords, user, domain):
    if state.get_asin(asin) == -1:
        return True
    log('loading webdriver')
    ev = Event()
    webdriver = base_chrome_init(goto=f'https://{domain}/')
    webdriver.change_loc(domain=domain)
    webdriver.get(webdriver.current_url
                  + f'product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
    try:
        webdriver.get(webdriver.get_element('link[rel="canonical"]').get_attribute('href')
                      + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
    except Exception as e:
        send_bot_msg(user, f'WARNING: canonical link not found for ASIN {asin}; error: {e}')

    reviews_count_element = webdriver.get_element('[data-hook="cr-filter-info-review-rating-count"]')
    reviews_count = 0
    if reviews_count_element:
        reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
        if len(reviews_count_part) == 2:
            reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
    print('count:', reviews_count)

    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev), daemon=True)

    try:
        webdriver.activate_jquery()
        user_emulate_thread.start()
        webdriver.activate_jquery()

        index = state.get_asin(asin)
        log(f'current asin: {asin} with index {index}')
        if index == -1:
            return True
        log('COLLECTING REVIEWS FOR ASIN', asin + ':')
        params_seed = None
        first = True
        try:
            for params_seed in (range(index, params_len) if reviews_count > 100 else [0]):
                for i in range(1, 11):
                    response = send_request(webdriver, asin, params_seed, i, keywords, domain)
                    if first:
                        webdriver.execute_script(f'$.get("https://www.{domain}/hz/rhf?currentPageType=CustomerReviews&currentSubPageType=remoteProduct&excludeAsin={asin}&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl={urllib.parse.quote(webdriver.current_url.replace(f"https://{domain}", "").replace(f"https://www.{domain}", ""))}")')
                        first = False
                    if response == -1:
                        break
                    if not response:
                        logger.error(f'Skip {asin}; seed={params_seed}', exc_info=True, stack_info=True)
                        log(f'Skip {asin}')
                        return False
            state.write_asin(asin, -1, 'reviews')
            return True
        except Exception as e:
            if 'Bad ASIN' not in str(e):
                raise e
            logger.error(f'Skip {asin}; seed={params_seed}', exc_info=True, stack_info=True)
            log(f'Skip {asin}')
            return False
    except (InvalidSessionIdException, RetryException) as e:
        logger.error(f'Error!', exc_info=True, stack_info=True)
        log('ERROR: invalid session. ASIN will be collected later')
        close(ev, user_emulate_thread, webdriver)
        sleep(10)
        return False
    except KeyboardInterrupt:
        log('Script stopped')
        close(ev, user_emulate_thread, webdriver)
        return False
    finally:
        close(ev, user_emulate_thread, webdriver)


def close(ev, uemu, wd):
    try:
        ev.set()
        if uemu.is_alive():
            uemu.join()
    except:
        pass
    try:
        wd.driver.close()
    except:
        pass


def start_reviews_collect(params_dict):
    res = False
    c = 99
    try:
        while not res and c > 0:
            res = collect(
                params_dict['asin'], params_dict.get('keywords', ''),
                params_dict.get('user'), params_dict.get('domain', 'amazon.com'),
            )
            c -= 1
    except KeyError:
        log('No ASIN error!')
    else:
        if 'user' in params_dict:
            if res or c == 99:
                send_bot_msg(
                    params_dict['user'],
                    f'Reviews of ASIN {params_dict["asin"]} collected!',
                )
            else:
                send_bot_msg(
                    params_dict['user'],
                    f'Reviews of ASIN {params_dict["asin"]} did NOT collected.',
                )
    finally:
        if 'id' in params_dict:
            requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
    return res


if __name__ == '__main__':
    import sys
    p = parse_args(sys.argv)
    p.setdefault('domain', 'amazon.com')
    start_reviews_collect(p)
