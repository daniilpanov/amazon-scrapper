import urllib
from json import JSONDecoder
from queue import Queue

from functions import chrome_init

writer_queue = Queue()
products_info_queue = Queue()
reviews_queue = Queue()
collected_asins = []


def collect_asins(query, market_niche=None):
    webdriver = None
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
        # Set needle niche and search query
        webdriver.select_option_by_text('#searchDropdownBox', market_niche)
        webdriver.type('#twotabsearchtextbox,#nav-bb-search', query)
        webdriver.submit('#twotabsearchtextbox,#nav-bb-search')

        # Get all query arguments (crid, qid, etc.)
        webdriver.click('a.s-pagination-item.s-pagination-button')
        webdriver.sleep(1)
        params_str = webdriver.get_current_url().split('?')[1]
        args = dict(list(tuple(map(lambda x: urllib.parse.quote(urllib.parse.unquote(x)),
                                   map(lambda x: x.replace('+', ' '), item.split('='))))
                         for item in params_str.split('&')))
        webdriver.activate_jquery()
        q = '?' + '&'.join('='.join(map(str, keyval)) for keyval in args.items())

        # we're ready to collect!
        # ALGORITHM: find the last page, then iterate each page before last page,
        # then goto the last page in browser and check again. If the last page will be the same - break cycle
        while True:
            last_page_el = webdriver.get_element('.s-pagination-item.s-pagination-disabled:last-of-type')
            if not last_page_el:
                last_page_el = webdriver.find_elements('.s-pagination-item.s-pagination-button')
                if last_page_el and len(last_page_el) > 2:
                    last_page_el = last_page_el[-2]
                else:
                    break
            elif 'Next' in last_page_el.text:
                break
            last_page = int(last_page_el.text.strip())
            for i in range(1, last_page + 1):
                strargs = '",'.join([':"'.join(map(str, keyval)) for keyval in (args | {'page': i}).items()]) + '"'
                result = webdriver.execute_script(f"$.post(\"https://www.amazon.com/s/query{q}\", "
                                                  "{" + strargs + "}, null, 'text');")
                writer_queue.put([0, result])
        return True
    except:
        return False
    finally:
        webdriver.driver.close()


def collect_products_info():
    pass


def collect_reviews():
    pass


def writer():
    # 0 - asin, 1 - product info, 2 - review(s)
    list_of_functions = [asin_write, product_info_write, reviews_write]
    not_broken = len(list_of_functions)

    while True:
        if not_broken:
            # [0 - item, 1 - data]
            el = writer_queue.get()
            if el[1] is None:
                not_broken -= 1
                continue
            list_of_functions[el[0]](el[1])
        else:
            return


def asin_write(data):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    rows = []

    with open('products.list', 'a') as f:
        for item in raw_data:
            if 'data-main-slot:search-result-' in item[1]:
                if item[2]['asin'] in collected_asins:
                    continue
                else:
                    rows.append(item[2]['asin'] + '\n')
                    collected_asins.append(item[2]['asin'])
                    # collect product info and reviews
                    products_info_queue.put(item[2]['asin'])
                    reviews_queue.put(item[2]['asin'])
        f.writelines(rows)


def product_info_write(data):
    pass


def reviews_write(data):
    pass


writer_funcs = (asin_write, product_info_write, reviews_write)

if __name__ == '__main__':
    print(collect_asins('hair gummies', 'Amazon Devices'))
