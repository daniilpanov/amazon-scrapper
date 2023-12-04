import sys
from queue import Queue
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from functions import base_chrome_init, WebDriver
from main_collect_all import get_all_asins_from_text


def get_all_sales_links(wd):
    wd.get('https://amazon.com/')
    return wd.get_element('div.a-cardui-footer')


def get_all_asins_from_deal(wd: WebDriver, deal_link, q_asins=None):
    if q_asins is None:
        q_asins = Queue()
    wd.get(deal_link)
    try:
        wd.wait_for_loading('.octops-dlp-asin-stream-section')
        links = wd.find_elements(By.CSS_SELECTOR, '.octops-dlp-asin-stream-section a.a-size-base[href*="B0"]')
    except NoSuchElementException:
        return False
    for link in links:
        asins = get_all_asins_from_text(link.get_attribute('href') or '')
        if len(asins) > 0:
            q_asins.put(asins[0])
    return q_asins


def get_all_deals(wd, q_deals=None, q_asins=None):
    if q_deals is None:
        q_deals = Queue()
    if q_asins is None:
        q_asins = Queue()
    wd.change_loc()
    wd.change_loc()
    try:
        last_button = wd.get_element('li.a-last')
    except NoSuchElementException as e:
        print(e)
        return False
    try:
        while last_button and 'a-disabled' not in last_button.get_attribute('class'):
            # collect
            links = map(lambda el: el.get_attribute('href'), wd.find_elements(
                By.CSS_SELECTOR,
                'div[class^="DealGridItem-module__dealItemDisplayGrid"] a:first-child',
            ))
            for link in links:
                asins = get_all_asins_from_text(link)
                if len(asins) > 0:
                    q_asins.put(asins[0])
                else:
                    q_deals.put(link)
            last_page_source = wd.get_page_source()
            wd.click('li.a-last')
            while True:
                sleep(3)
                new_page_source = wd.get_page_source()
                if new_page_source != last_page_source:
                    break
                wd.click('li.a-last')
            break
    except (KeyboardInterrupt, Exception) as e:
        print(e)
    finally:
        return q_deals, q_asins


if __name__ == '__main__':
    wdr = base_chrome_init(
        False,
        goto='https://www.amazon.com/deals/ref=cg_BFLOHERO_1a1_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=slot-2&pf_rd_r'
             '=5QZFK381M65Q9B7H90E7&pf_rd_t=0&pf_rd_p=55c21ce1-047a-4190-bd23-78871098dae7&pf_rd_i=cybermonday'
    )
    qd, qa = get_all_deals(wdr)
    print(get_all_asins_from_deal(wdr, qd.get()).get())
    try:
        while True:
            wdr.driver.close()
    except Exception as e:
        raise e