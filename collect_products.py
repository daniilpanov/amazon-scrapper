import requests

import database as db
import state
from functions import base_chrome_init, captcha_solve
from helpers import parse_args, log
from parser import parse_product

import logging

from state import chunk

logger = logging.getLogger('products')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'products.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

domain = 'amazon.com'


def collect(products_info_list):
    products_info_list = list([asin for asin in products_info_list if state.get_asin(asin, 'products') != -1])
    if not products_info_list:
        return -1
    webdriver = base_chrome_init(goto=f'https://{domain}')
    webdriver.change_loc(domain=domain)
    collected = set()

    for el in products_info_list:
        if state.get_asin(el, 'products') == -1:
            collected.add(el)
            continue
        webdriver.get(f'https://{domain}/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()

        if product_info_write(el, webdriver.get_page_source()):
            state.write_asin(el, -1, 'products')
            collected.add(el)

    webdriver.driver.quit()
    return collected


def product_info_write(asin, html):
    db.write_product_html(asin, html, domain)
    try:
        data = parse_product(asin, html, domain=domain)
        db.write_product_parsed(*data)
        return True
    except Exception as e:
        log(f'ERROR when parsing asin: {asin} -- ', e)
        return False


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)
    domain = params_dict.get('domain', 'amazon.com')
    asins = chunk(params_dict.get('asins', ''))
    res = False
    c = 99
    try:
        if asins:
            while not res and c > 0:
                res = collect(asins)
                c -= 1
        else:
            log('No ASINs error!')
    except:
        pass
    else:
        if 'user' in params_dict:
            if res or c == 99:
                requests.post('http://localhost:8080/send_msg', {
                    'msg': f'Product cards of list "{params_dict.get("list_name", params_dict["asins"])}"'
                           ' collected!',
                    'uid': params_dict['user'],
                })
            else:
                requests.post('http://localhost:8080/send_msg', {
                    'msg': f'Product cards of list "{params_dict.get("list_name", params_dict["asins"])}"'
                           ' did NOT collected.',
                    'uid': params_dict['user'],
                })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
