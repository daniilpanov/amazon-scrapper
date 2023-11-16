import urllib
from json import JSONDecoder
from queue import Queue
from threading import Thread, Event
from time import sleep

from selenium.common import JavascriptException

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


def collect_asins(query, products_info_queue=None, market_niche=None, page=1, callback=None, filename='products-list.txt'):
    # Emulation user switcher
    ev = Event()

    webdriver: WebDriver = chrome_init(goto='https://amazon.com')
    webdriver.change_loc()

    webdriver.sleep(1)
    webdriver.refresh()
    # Emulate user mouse moves
    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev))
    user_emulate_thread.start()
    # Callback if exists
    if callback:
        callback_queue = Queue()
        callback_thread = Thread(target=callback_wait, args=(callback, callback_queue))
        callback_thread.start()
    # Main scrap
    try:
        webdriver.select_option_by_text('#searchDropdownBox', market_niche)
        webdriver.sleep(10)
        webdriver.type('#twotabsearchtextbox,#nav-bb-search', query)
        webdriver.submit('#twotabsearchtextbox,#nav-bb-search')

        webdriver.click('a.s-pagination-item.s-pagination-button')
        webdriver.sleep(1)
        params_str = webdriver.get_current_url().split('?')[1]
        args = dict(list(tuple(map(lambda x: urllib.parse.quote(urllib.parse.unquote(x)),
                                   map(lambda x: x.replace('+', ' '), item.split('='))))
                         for item in params_str.split('&')))
        webdriver.activate_jquery()
        # BEGIN COLLECTING
        q = '&'.join('='.join(map(str, keyval)) for keyval in args.items())
        # get the last page (and later we need to update it)
        max_page_el = webdriver.get_element('span.s-pagination-item.s-pagination-disabled')
        if 'Next' in max_page_el.text:
            max_page = 1
        else:
            max_page = int(max_page_el.text.strip())
        while True:
            p = args
            p['page'] = str(page)
            p = p.items()
            try:
                result = webdriver.execute_script(f"return $.post(\"https://www.amazon.com/s/query?{q}\", "
                                                  "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in p]) + "\"}, null, 'text');")
            except JavascriptException:
                # if error - reload webdriver
                ev.set()
                if products_info_queue:
                    products_info_queue.put(None)
                if callback:
                    callback_queue.put(None)
                    callback_thread.join()
                user_emulate_thread.join()
                webdriver.driver.close()
                sleep(10)
                return collect_asins(query, products_info_queue, market_niche, page, callback, filename)
            asin_write(result, products_info_queue, filename)
            page += 1
            if page >= max_page:
                max_page_el = webdriver.get_element('span.s-pagination-item.s-pagination-disabled')
                if 'Next' in max_page_el.text:
                    break
                max_page = int(max_page_el.text.strip())
        return True
    except:
        return False
    finally:
        ev.set()
        products_info_queue.put(None)
        if callback:
            callback_queue.put(None)
            callback_thread.join()
        user_emulate_thread.join()
        webdriver.driver.close()


def callback_wait(callback, queue):
    while callback:
        data = queue.get()
        if not data:
            break
        callback(data)


def collect_products_info(products_info_list, conn_reader=None):
    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        return
    products_info_list = list([asin for asin in products_info_list if state.get_asin(asin, 'products') != -1])
    if not products_info_list:
        return
    webdriver = chrome_init(goto='https://amazon.com')
    webdriver.change_loc()

    for el in products_info_list:
        if state.get_asin(el, 'products') == -1:
            continue
        if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
            return webdriver.driver.quit()
        webdriver.get('https://amazon.com/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()

        webdriver.save_page_source('html')
        state.write_asin(el, 960, 'products')
        product_info_write(el, webdriver.get_page_source())

    webdriver.driver.quit()



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
    except Exception as e:
        print(f'ERROR when parsing asin: {asin} -- ', e)
