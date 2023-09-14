import urllib
from json import JSONDecoder
from queue import Queue
from threading import Thread
from typing import Union

from seleniumbase import BaseCase

from functions import chrome_init


def collect_asins(query, market_niche=None):
    webdriver: Union[BaseCase, None] = None
    # Queues
    writer_queue = Queue()
    products_info_queue = Queue()
    reviews_queue = Queue()
    # Threads
    writer_thr = Thread(target=writer, args=(writer_queue, ))
    products_info_thr = Thread(target=collect_products_info, args=(products_info_queue, ))
    reviews_thr = Thread(target=collect_reviews, args=(reviews_queue, ))
    try:
        webdriver = chrome_init(modern=True, headless=False, goto='https://amazon.com')
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
    except:
        if webdriver:
            try:
                webdriver.driver.close()
            except:
                pass
        return False

    webdriver.sleep(1)
    webdriver.refresh()
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
        page = 1
        # get the last page (and later we need to update it)
        # TODO: update it!
        max_page_el = None
        if 'Next' in max_page_el.text:
            max_page = 1
        else:
            max_page = 10
        while True:
            p = args
            p['page'] = str(page)
            p = p.items()
            result = webdriver.execute_script(f"$.post(\"https://www.amazon.com/s/query?{q}\", "
                                              "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in p]) + ""
                                              "\"}, null, 'text');")
            writer_queue.put((0, (result, )))
            page += 1
            if page >= max_page:
                # TODO: update the last page!
                max_page_el = None
                if 'Next' in max_page_el.text:
                    break
                max_page = 10
        return True
    except:
        return False
    finally:
        writer_queue.put((-1, None))
        products_info_queue.put(None)
        reviews_queue.put(None)
        webdriver.driver.close()


def collect_products_info():
    pass


def collect_reviews():
    pass


# 0 - asin, 1 - product info, 2 - review(s)
def writer(writer_queue):
    while True:
        item, data = writer_queue.get()
        if item == -1:
            break
        writer_funcs[item](*data)


def asin_write(data):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    rows = []

    with open('products.list', 'a') as f:
        for item in raw_data:
            if len(item) > 1 and 'data-main-slot:search-result-' in item[1] and 'asin' in item[2]:
                rows.append(item[2]['asin'] + '\n')
        f.writelines(rows)


def product_info_write(data):
    pass


def reviews_write(data):
    pass


writer_funcs = (asin_write, product_info_write, reviews_write)

if __name__ == '__main__':
    print(collect_asins('hair gummies', 'Amazon Devices'))
