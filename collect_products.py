import datetime
import os.path
import urllib
from json import JSONDecoder
from queue import Queue
from threading import Thread, Event
from time import sleep

import pytz
from bs4 import BeautifulSoup
from pandas import DataFrame
from selenium.common import JavascriptException

from database import write_product_parsed, write_product_html
from functions import chrome_init, user_emulate, captcha_solve, WebDriver
import keepa_functions as kf


def collect_asins(query, writer_queue, products_info_queue, reviews_queue, market_niche=None, page=1):
    # Emulation user switcher
    ev = Event()

    webdriver: WebDriver = chrome_init(goto='https://amazon.com')
    webdriver.change_loc()

    webdriver.sleep(1)
    webdriver.refresh()
    # Emulate user mouse moves
    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev))
    user_emulate_thread.start()
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
                writer_queue.put((-1, None))
                products_info_queue.put(None)
                reviews_queue.put(None)
                ev.set()
                webdriver.driver.close()
                sleep(30)
                return collect_asins(query, writer_queue, products_info_queue, reviews_queue, market_niche, page)
            writer_queue.put((0, (result, reviews_queue, products_info_queue)))
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
        writer_queue.put((-1, None))
        products_info_queue.put(None)
        reviews_queue.put(None)
        ev.set()
        webdriver.driver.close()


def collect_products_info(products_info_list, writer_queue):
    # Initializing webdriver with extension 'Keepa - Amazon Price Tracker'
    webdriver = chrome_init(False, goto='https://amazon.com', extension='./keepa-extension')
    webdriver.change_loc()

    for el in products_info_list:
        webdriver.get('https://amazon.com/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()
        # Checking if not login
        kf.keepa_login(webdriver)
        # saving html + keepa data
        writer_queue.put((1, [
            el, webdriver.get_page_source(),
            # kf.keepa__price_history(webdriver),
            # kf.keepa__statistics(webdriver),
            # kf.keepa__comparing(webdriver),
            # kf.keepa__data(webdriver),
        ]))

    webdriver.driver.quit()


def collect_reviews(reviews_queue):
    el = reviews_queue.get()
    while el:
        # cr.main(el)
        reviews_queue.task_done()
        el = reviews_queue.get()


def parse_product(asin, html):
    bs = BeautifulSoup(html, features='html.parser')
    title = bs.select_one('#titleSection, #title, #productTitle').text.strip()
    descr = bs.find(id='feature-bullets').text.strip()
    pic = bs.find(id='landingImage')['src']
    features = {}
    top5 = []
    try:
        features_els = bs.select(
            '[data-hook="cr-widget-SummaryAttribute"] #cr-summarization-attributes-list > div'
        )
        for feat in features_els:
            features[feat.find('div > div > div:first-child span').text.strip()] = \
                feat.select_one('div > div > div:last-child > span:last-child').text.strip()
    except:
        pass
    try:
        top5_els = bs.select('[data-hook="lighthut-terms-list"] > div')[:5]
        for lighthum in top5_els:
            top5.append(lighthum.find('span').text.strip())
    except:
        pass
    price = bs.select_one('.a-price.a-text-price')
    if price:
        price = price.text.strip()
    else:
        price = None
    return [
        asin, f'https://amazon.com/dp/{asin}',
        title, descr, pic, datetime.datetime.now(pytz.UTC),
        features, top5, price
    ]


# 0 - asin, 1 - product info, 2 - review(s)
def writer(writer_queue, filenames):
    while True:
        item, data = writer_queue.get()
        if item == -1:
            break
        writer_funcs[item](*data, filename=filenames[item])
        writer_queue.task_done()


def asin_write(data, reviews_queue, products_queue):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    rows = []
    asins = []

    with open('products-list.txt', 'a') as f:
        for item in raw_data:
            if len(item) > 1 and 'data-main-slot:search-result-' in item[1] and 'asin' in item[2]:
                rows.append(item[2]['asin'] + '\n')
                asins.append(item[2]['asin'])
                products_queue.put(item[2]['asin'])
        f.writelines(rows)
    # load reviews collecting for a page of products
    reviews_queue.put(asins)


def product_info_write(asin, html, keepa_ph=None, keepa_stats=None, keepa_comparing=None, keepa_data=None, filename='products-list.csv'):
    # columns = 'asin,html,keepa_price_history,keepa_statistics,keepa_comparing,keepa_data'
    columns = 'asin,html'
    if not os.path.exists(filename + '--raw.csv'):
        f = open(filename + '--raw.csv', 'w', encoding='utf-8')
        f.write(columns + '\n')
        f.close()
    # data = [asin, html, keepa_ph, keepa_stats, keepa_comparing, keepa_data]
    data = [asin, html]
    df = DataFrame([data], columns=columns.split(','))
    write_product_html(*data)
    df.to_csv(filename + '--raw.csv', index=False, header=False, mode='a', encoding='utf-8')
    columns = ('asin,product_url,product_title,product_descr,'
               'picture_url,parse_datetime,features,top_5_phrases,product_price')
    if not os.path.exists(filename):
        f = open(filename, 'w', encoding='utf-8')
        f.write(columns + '\n')
        f.close()

    data = parse_product(asin, html)
    df = DataFrame([data], columns=columns.split(','))
    write_product_parsed(*data)
    df.to_csv(filename, index=False, header=False, mode='a', encoding='utf-8')


writer_funcs = (asin_write, product_info_write)

if __name__ == '__main__':
    wq = Queue()
    piq = Queue()
    rq = Queue()
    # Threads
    writer_thr = Thread(target=writer, args=(wq,))
    products_info_thr = Thread(target=collect_products_info, args=(piq, wq))
    reviews_thr = Thread(target=collect_reviews, args=(rq,))
    # Start
    writer_thr.start()
    products_info_thr.start()
    reviews_thr.start()
    # Collect
    print(collect_asins('hair gummies', wq, piq, rq, 'Beauty & Personal Care'))
