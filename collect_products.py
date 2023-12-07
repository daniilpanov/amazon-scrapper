from json import JSONDecoder

import database as db
import state
from functions import chrome_init, user_emulate, captcha_solve, WebDriver
from parser import parse_product

import logging

logger = logging.getLogger('products')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'products.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def collect_products_info(products_info_list, conn_reader=None):
    if conn_reader and conn_reader.poll() and conn_reader.recv() is False:
        return -1
    products_info_list = list([asin for asin in products_info_list if state.get_asin(asin, 'products') != -1])
    if not products_info_list:
        return -1
    webdriver = chrome_init(goto='https://amazon.com')
    webdriver.change_loc()
    collected = set()

    for el in products_info_list:
        if state.get_asin(el, 'products') == -1:
            collected.add(el)
            continue
        if conn_reader and conn_reader.poll() and conn_reader.recv() is False:
            return webdriver.driver.quit()
        webdriver.get('https://amazon.com/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()

        if product_info_write(el, webdriver.get_page_source()):
            state.write_asin(el, 960, 'products')
            collected.add(el)

    webdriver.driver.quit()
    return collected


def asin_write(data, products_queue=None, filename='products-list.txt'):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    rows = []
    asins = []

    for item in raw_data:
        if len(item) > 1 and 'data-main-slot:search-result-' in item[1] and 'asin' in item[2]:
            rows.append(item[2]['asin'] + '\n')
            asins.append(item[2]['asin'])
            if products_queue:
                products_queue.put(item[2]['asin'])
    with open(filename, 'a') as f:
        f.writelines(rows)


def product_info_write(asin, html):
    db.write_product_html(asin, html)
    try:
        data = parse_product(asin, html)
        db.write_product_parsed(*data)
        return True
    except Exception as e:
        print(f'ERROR when parsing asin: {asin} -- ', e)
        return False
