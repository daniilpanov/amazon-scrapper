from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from functions import chrome_init, wait_for_loading


def collect_asins(market_niche=None):
    webdriver = chrome_init()
    webdriver.get('https://amazon.com')
    wait_for_loading(webdriver)
    # переход к необходимой локации - US (UM)
    try:
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
    sleep(1)
    webdriver.refresh()
    wait_for_loading(webdriver)
    try:
        search_input = webdriver.find_element(By.CSS_SELECTOR, '#twotabsearchtextbox,#nav-bb-search')
    except NoSuchElementException:
        print('ERROR! Search box not found')
        return False


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
    pass
