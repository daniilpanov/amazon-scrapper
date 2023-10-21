import os.path
import urllib
from json import JSONDecoder
from queue import Queue
from threading import Thread, Event
from time import sleep

from pandas import DataFrame
from selenium.common import JavascriptException

from functions import chrome_init, user_emulate, captcha_solve, WebDriver
import keepa_functions as kf
import collect_reviews as cr


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


def collect_products_info(products_info_queue, writer_queue):
    # Initializing webdriver with extension 'Keepa - Amazon Price Tracker'
    webdriver = chrome_init(False, goto='https://amazon.com', extension='./keepa-extension')
    webdriver.change_loc()

    el = products_info_queue.get()
    while el:
        print(el)
        webdriver.get('https://amazon.com/dp/' + el)
        captcha_solve(webdriver)
        webdriver.activate_jquery()
        # Checking if not login
        kf.keepa_login(webdriver)
        # saving html + keepa data
        writer_queue.put((1, [
            el, webdriver.get_page_source(),
            kf.keepa__price_history(webdriver),
            kf.keepa__statistics(webdriver),
            kf.keepa__comparing(webdriver),
            kf.keepa__data(webdriver),
        ]))

        products_info_queue.task_done()
        el = products_info_queue.get()

    webdriver.driver.quit()


def collect_reviews(reviews_queue):
    el = reviews_queue.get()
    while el:
        # cr.main(el)
        reviews_queue.task_done()
        el = reviews_queue.get()


# 0 - asin, 1 - product info, 2 - review(s)
def writer(writer_queue):
    while True:
        item, data = writer_queue.get()
        if item == -1:
            break
        writer_funcs[item](*data)
        writer_queue.task_done()


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


def product_info_write(asin, html, keepa_ph, keepa_stats, keepa_comparing, keepa_data):
    if not os.path.exists('products_list.csv'):
        f = open('products_list.csv', 'w', encoding='utf-8')
        f.write('asin,html,keepa price history,keepa statistics,keepa comparing,keepa data\n')
        f.close()
    df = DataFrame([[asin, html, keepa_ph, keepa_stats, keepa_comparing, keepa_data]],
                   columns=[
                       'asin',
                       'html',
                       'keepa price history',
                       'keepa statistics',
                       'keepa comparing',
                       'keepa data',
                   ])
    df.to_csv('products_list.csv', index=False, header=False, mode='a', encoding='utf-8')


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
