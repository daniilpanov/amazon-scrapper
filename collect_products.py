import os.path
import urllib
from json import JSONDecoder
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Union

from pandas import DataFrame
from selenium.common import JavascriptException
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from functions import chrome_init, user_emulate, captcha_solve
import keepa_functions as kf


def collect_asins(query, market_niche=None, page=1):
    webdriver: Union[BaseCase, None] = None
    # Queues
    writer_queue = Queue()
    products_info_queue = Queue()
    reviews_queue = Queue()
    # Emulation user switcher
    ev = Event()
    # Threads
    writer_thr = Thread(target=writer, args=(writer_queue,))
    products_info_thr = Thread(target=collect_products_info, args=(products_info_queue, writer_queue))
    reviews_thr = Thread(target=collect_reviews, args=(reviews_queue,))

    webdriver = chrome_init(goto='https://amazon.com')
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
        # START THREADS
        writer_thr.start()
        products_info_thr.start()
        reviews_thr.start()
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
                return collect_asins(query, market_niche, page)
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


def collect_products_info(products_info_queue, writer_queue):
    # Initializing webdriver with extension 'Keepa - Amazon Price Tracker'
    webdriver = chrome_init(goto='https://amazon.com', extension='./keepa-extension')
    webdriver.change_loc()

    el = products_info_queue.get()
    while el:
        print(el)
        webdriver.get('https://amazon.com/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()
        # Checking if not login

        # INFO
        webdriver.switch_to_default_content()
        title = webdriver.get_element('#titleSection, #title, #productTitle').text.strip()
        cost = None
        try:
            cost = webdriver.get_element('.a-price.a-text-price').text.strip()
        except:
            webdriver.switch_to_frame('#keepa')
            webdriver.sleep(.6)
            webdriver.click('#compareChart')
            webdriver.sleep(.6)
            try:
                rows = webdriver.find_elements('div[ref="eCenterViewport"] div[role="row"]')
            except:
                webdriver.click('#compareChart')
                webdriver.sleep(.6)
                rows = webdriver.find_elements('div[ref="eCenterViewport"] div[role="row"]')
            for row in rows:
                els = row.find_elements(By.CSS_SELECTOR, 'div[role="gridcell"]')
                if len(els) <= 0:
                    continue
                if 'America' in els[0]:
                    cost = els[2].text.strip() or els[4].text.strip()
                    break
            webdriver.click('#comparePricesOverlay-close')
            webdriver.switch_to_default_content()
        webdriver.switch_to_frame('#keepa')
        categories = [None, None, None]
        try:
            webdriver.click('#tabMore')
            webdriver.wait_for_element_visible('#MoreTab1')
            webdriver.sleep(.6)
            for row in webdriver.find_elements('div[ref="eCenterViewport"] div[role="row"]'):
                items = row.find_elements(By.CSS_SELECTOR, 'div[role="cell"]')
                if len(items) <= 0:
                    continue
                if 'Categories - Tree' in items[0].text:
                    cat = items[1].find_elements('.cell-wrap div span a:first-child')
                    if len(categories) > 2:
                        categories = [cat[0], cat[1], cat[-1]]
                    elif len(categories) > 1:
                        categories = [cat[0], cat[1], None]
                    elif len(categories) > 2:
                        categories = [cat[-1], None, None]
                    break
        except Exception as e:
            raise e
            pass

        features = {}
        lighthums = []
        try:
            webdriver.switch_to_default_content()
            webdriver.click('#acrCustomerReviewText')
            webdriver.sleep(.6)
            try:
                features_els = webdriver.get_element(
                    '[data-hook="cr-widget-SummaryAttribute"] #cr-summarization-attributes-list > div'
                )
                for feat in features_els:
                    features[feat.find_element(By.CSS_SELECTOR, 'div > div > div:first-child span').text.strip()] = \
                        feat.find_element(By.CSS_SELECTOR, 'div > div > div:last-child > span:last-child').text.strip()
            except:
                pass
            try:
                lighthums_els = webdriver.find_elements('[data-hook="lighthut-terms-list"] > div')
                for lighthum in lighthums_els:
                    lighthums.append(lighthum.find_element(By.TAG_NAME, 'span').text.strip())
            except:
                pass
        except:
            pass

        writer_queue.put((1, [el, title, cost, features, lighthums, categories]))
        el = products_info_queue.get()

    webdriver.driver.quit()


def collect_reviews(reviews_queue):
    el = reviews_queue.get()
    while el:
        # TODO: call to reviews_collect

        el = reviews_queue.get()


# 0 - asin, 1 - product info, 2 - review(s)
def writer(writer_queue):
    while True:
        item, data = writer_queue.get()
        if item == -1:
            break
        writer_funcs[item](*data)


def asin_write(data, reviews_queue, products_queue):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    rows = []
    asins = []

    with open('products.list', 'a') as f:
        for item in raw_data:
            if len(item) > 1 and 'data-main-slot:search-result-' in item[1] and 'asin' in item[2]:
                rows.append(item[2]['asin'] + '\n')
                asins.append(item[2]['asin'])
                products_queue.put(item[2]['asin'])
        f.writelines(rows)
    # load reviews collecting for a page of products
    reviews_queue.put(asins)


def product_info_write(asin, title, cost, features, lighthums, categories):
    if not os.path.exists('products_list.csv'):
        f = open('products_list.csv', 'w', encoding='utf-8')
        f.write('asin,title,cost,features,lighthums,department,category,subcategory\n')
        f.close()
    df = DataFrame([[asin, title, cost, features, lighthums, *categories]], columns=[
        'asin',
        'title',
        'cost',
        'features',
        'lighthums',
        'department',
        'category',
        'subcategory',
    ])
    df.to_csv('products_list.csv', index=False, header=False, mode='a', encoding='utf-8')


def reviews_write(data):
    pass


writer_funcs = (asin_write, product_info_write, reviews_write)

if __name__ == '__main__':
    print(collect_asins('hair gummies', 'Beauty & Personal Care'))
