import urllib
from json import JSONDecoder

from functions import chrome_init

# TODO: queues system (writer, products_info, reviews)


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
        q = '?' + '&'.join('='.join(map(str, keyval)) for keyval in args.items())
        result = webdriver.execute_script(f"$.post(\"https://www.amazon.com/s/query{q}\", "
                                          "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in args.items()]) + ""
                                          "\"}, null, 'text');")
        asin_write(result, args['pageNumber'])
        return True
    except:
        return False
    finally:
        webdriver.driver.close()


def collect_products_info():
    pass


def collect_reviews():
    pass


# 0 - asin, 1 - product info, 2 - review(s)
def writer(item, data):
    pass


def asin_write(data, page):
    decoder = JSONDecoder()
    raw_data = list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, data.strip().split('&&&'))))
    count_all_products = 0
    rows = []

    with open('products.list', 'a') as f:
        for item in raw_data:
            if count_all_products > 0 and count_all_products // 48 + 1 < page:
                return count_all_products
            if 'data-main-slot:search-result-' in item[1]:
                rows.append(item[2]['asin'] + '\n')
        f.writelines(rows)


def product_info_write(data):
    pass


def reviews_write(data):
    pass


writer_funcs = (asin_write, product_info_write, reviews_write)

if __name__ == '__main__':
    print(collect_asins('hair gummies', 'Amazon Devices'))
