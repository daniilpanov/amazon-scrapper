import datetime
import urllib
from time import sleep

import pytz
import requests
from selenium.common import NoSuchElementException, StaleElementReferenceException, WebDriverException

import tasks
from functions import base_chrome_init, WebDriver, Amazon404Exception

from .parse import process_data, process_data_from_page, count_reviews
from .write import reviews_collection
from .logger import logger

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


def send_request(asin, seed, page, keywords='', domain='amazon.com', current_format=True):
    if seed >= params_len:
        return True

    global wd
    if not wd:
        return False

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
    except Exception:
        logger('collect.send_request').exception()
        return False


def wd_init(domain, asin):
    global wd
    if wd:
        wd.full_close()
    logger().info(f'loading webdriver for {asin}')
    try:
        wd = base_chrome_init(goto=f'https://{domain}/')
        wd.change_loc(domain=domain)
        return wd
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


def collect(_id, view_id, asin, keywords='', domain='amazon.com', params_seed=0, current_format=True):
    global wd
    try:
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
                reviews_count = count_reviews(wd.get_page_source())
            except WebDriverException:
                continue
            break

        logger('collect').info(f'ASIN: {asin}; count: {reviews_count}')

        try:
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
                global wd
                if not wd:
                    wd = wd_init(d, a)
                res = send_request(a, _p, _i, k, d, cf)
                if not res:
                    u = wd.driver.current_url
                    wd.full_close()
                    while True:
                        try:
                            wd = wd_init(d, a)
                            wd.get('https://' + d)
                            wd.get(u)
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
                    for i in range(1, 11):
                        logger('collect').debug('seed: ' + str(params_seed))
                        send_wrapper(asin, params_seed, i, keywords, domain, current_format)
                    if _id:
                        task['result']['asins_progress'][asin] = params_seed
                wd.full_close()
                wd = None
                if task:
                    requests.post('http://45.14.245.223:1802/new_collection/', json={
                        'name': task['alias'],
                        'date': datetime.datetime.now(pytz.UTC).date().isoformat(),
                        'asins': [asin],
                    })
                    task['result']['asins'].append(asin)
                    task['result']['count'].append(
                        reviews_collection.count_documents({'asin': asin})
                    )
                    task.add_progress(1)
                return -1
            except Exception as e:
                wd.full_close()
                wd = None
                if 'Bad ASIN' not in str(e):
                    raise e
                logger('collect').warn('Skip ' + asin)
                task = tasks.get_task(_id)
                task.success = False
                task.ended_at = datetime.datetime.now(pytz.UTC)
                return params_seed
        except KeyboardInterrupt:
            logger('collect').info('Script stopped')
            wd.full_close()
            wd = None
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
