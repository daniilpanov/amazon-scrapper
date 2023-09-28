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

from functions import chrome_init, user_emulate


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
    try:
        webdriver = chrome_init(modern=True, headless=False, goto='https://amazon.com')
        # переход к необходимой локации - US (UM)
        webdriver.sleep(.5)
        webdriver.activate_jquery()
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            'countryCode: "UM",'
            'deviceType: "web",'
            'distinct: "UM",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        webdriver.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        webdriver.refresh()
        webdriver.activate_jquery()
        # переход к необходимой локации - US (UM)
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            'countryCode: "UM",'
            'deviceType: "web",'
            'distinct: "UM",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        webdriver.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        webdriver.refresh()
    except:
        if webdriver:
            try:
                webdriver.driver.close()
            except:
                pass
        return False

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
                                                  "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in p]) + ""
                                                                                                                   "\"}, null, 'text');")
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
    # Initializing webdriver with extension
    webdriver = chrome_init(True, headless=False, extension=os.path.abspath('keepa-extension'))
    webdriver.get('chrome://extensions')
    # find ID of the extension
    webdriver.sleep(3)
    items = None
    try:
        # click to devmode
        webdriver.sleep(1)
        root_el = webdriver.get_element('extensions-manager', timeout=1).shadow_root
        items = root_el.find_element(By.CSS_SELECTOR, '#container extensions-item-list').shadow_root.find_elements(
            By.CSS_SELECTOR,
            '#container > #content-wrapper > .items-container:not(.review-panel-container) > extensions-item',
        )
    except:
        pass
    _id = None
    if items:
        for item in items:
            if 'Keepa - Amazon Price Tracker' \
                    in item.shadow_root.find_element(By.CSS_SELECTOR, '#card > #main #content > div:first-child').text:
                _id = item.get_property('id')
                break

    try:
        webdriver.get('https://amazon.com')
        webdriver.sleep(.5)
        webdriver.activate_jquery()
        # переход к необходимой локации - US (UM)
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            'countryCode: "UM",'
            'deviceType: "web",'
            'distinct: "UM",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        webdriver.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        webdriver.refresh()
        webdriver.activate_jquery()
        # переход к необходимой локации - US (UM)
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        webdriver.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            'countryCode: "UM",'
            'deviceType: "web",'
            'distinct: "UM",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        webdriver.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        webdriver.refresh()
    except:
        if webdriver:
            try:
                webdriver.driver.close()
            except:
                pass

    el = products_info_queue.get()
    while el:
        print(el)
        webdriver.get('https://amazon.com/dp/' + el)
        # Checking if not login
        try:
            webdriver.switch_to_frame('#keepa')
            webdriver.get_element('#keepaBoxLogin').click()
            webdriver.sleep(.1)
            webdriver.type('#username', 'keepa@brandlogic.ai')
            webdriver.sleep(.1)
            webdriver.type('#password', '5kJuNc6EU1itFh0Y')
            webdriver.sleep(.1)
            webdriver.submit('#password')
            webdriver.switch_to_default_content()
        except:
            pass
        # INFO
        title = webdriver.get_element('#titleSection, #title, #productTitle').text.strip()
        features = {}
        try:
            features_els = webdriver.get_element(
                '[data-hook="cr-widget-SummaryAttribute"] #cr-summarization-attributes-list > div'
            )
            for feat in features_els:
                features[feat.find_element(By.CSS_SELECTOR, 'div > div > div:first-child span').text.strip()] = \
                    feat.find_element(By.CSS_SELECTOR, 'div > div > div:last-child > span:last-child').text.strip()
        except:
            pass
        lighthums = []
        try:
            lighthums_els = webdriver.find_elements('[data-hook="lighthut-terms-list"] > div')
            for lighthum in lighthums_els:
                lighthums.append(lighthum.find_element(By.TAG_NAME, 'span').text.strip())
        except:
            pass
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
                els = row.find_elements('div[role="gridcell"]')
                if 'America' in els[0]:
                    cost = els[2].text.strip() or els[4].text.strip()
                    break
            webdriver.switch_to_default_content()
        webdriver.switch_to_frame('#keepa')
        categories = []
        try:
            webdriver.click('#tabMore')
            webdriver.wait_for_element_visible('#MoreTab1')
            for row in webdriver.find_elements('div[ref="eCenterViewport"] div[role="row"]'):
                items = row.find_elements('div[role="cell"]')
                if 'Categories - Tree' in items[0].text:
                    cat = items[1].find_elements('.cell-wrap div span a:first-child')
                    if len(categories) > 2:
                        categories = [cat[0], cat[1], cat[-1]]
                    elif len(categories) > 1:
                        categories = [cat[0], cat[1], None]
                    elif len(categories) > 2:
                        categories = [cat[-1], None, None]
                    else:
                        categories = [None, None, None]
                    break
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
