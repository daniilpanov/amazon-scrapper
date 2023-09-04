from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from functions import chrome_init, wait_for_loading


def collect_asins(query, market_niche=None):
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
        return False
    finally:
        webdriver._BaseCase__close_all_drivers()

    webdriver.sleep(1)
    webdriver.refresh()
    try:
        print(webdriver.get_element('#searchDropdownBox'))
        webdriver.select_option_by_text('#searchDropdownBox', 'Arts & Crafts')
        webdriver.sleep(10)
        webdriver.type('#twotabsearchtextbox,#nav-bb-search', query)
    finally:
        try:
            webdriver._BaseCase__close_all_drivers()
        except:
            pass


def collect_products_info():
    pass


def collect_reviews():
    pass


# 0 - asin, 1 - product info, 2 - review(s)
def writer(item, data):
    pass


def asin_write(data):
    pass


def product_info_write(data):
    pass


def reviews_write(data):
    pass


writer_funcs = (asin_write, product_info_write, reviews_write)

if __name__ == '__main__':
    collect_asins('hair gummies', 'fsdfd')
