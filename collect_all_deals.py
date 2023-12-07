import sys
from queue import Queue
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from functions import base_chrome_init, WebDriver
from main_collect_all import get_all_asins_from_text


def asin_level(wd: WebDriver, asin, name=None, link=None):
    return {'name': name, 'link': link, 'is_asin': True}


def deal_level(wd: WebDriver, deal_link, deal_name):
    asins = []
    wd.get(deal_link)
    try:
        wd.wait_for_loading('.octops-dlp-asin-stream-section, '
                            '#productInfoList, '
                            'span[data-component-type="s-search-results"]', 5)
        links = wd.find_elements(By.CSS_SELECTOR, '.octops-dlp-asin-stream-section a[href*="B0"],'
                                                  '#productInfoList a[href*="B0"],'
                                                  'span[data-component-type="s-search-results"] a[href*="B0"]')
    except (NoSuchElementException, TimeoutException):
        return False
    links = set([link.get_attribute('href') for link in links])
    i = 0
    for link in links:
        t_asins = get_all_asins_from_text(link or '')
        if len(t_asins) > 0:
            asins.append((i, link, t_asins[0]))
    return {'name': deal_name, 'link': deal_link, 'is_asin': False, 'items': asins}


def deals_group_level(wd, link):
    wd.get(link)
    wd.wait_for_loading()
    deals = []
    try:
        last_button = wd.get_element('li.a-last')
    except NoSuchElementException as e:
        print(e)
        return False
    try:
        i = 0
        while last_button and 'a-disabled' not in last_button.get_attribute('class'):
            # collect
            links = wd.find_elements(
                By.CSS_SELECTOR,
                'div[class^="DealGridItem-module__dealItemDisplayGrid"] a:last-child',
            )
            for link in links:
                t_asins = get_all_asins_from_text(link.get_attribute('href'))
                if len(t_asins) > 0:
                    deals.append((i, True, link.get_attribute('href'), link.text.strip(), t_asins[0]))
                else:
                    deals.append((i, False, link.get_attribute('href'), link.text.strip()))
            last_page_source = wd.get_page_source()
            wd.click('li.a-last')
            while True:
                sleep(3)
                new_page_source = wd.get_page_source()
                if new_page_source != last_page_source:
                    break
                wd.click('li.a-last')
            break  # temp
    except (KeyboardInterrupt, Exception) as e:
        print(e)
    finally:
        return deals


def landing_level():
    return []


def scrap_main_page():
    wd = base_chrome_init(False, goto='https://amazon.com')
    wd.change_loc()

    # SCRAP MAIN; CREATES SHEETS
    landing_scrap = (landing_level()
                     or [
                         'https://www.amazon.com/deals/ref=cg_BFLOHERO_1a1_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=slot-2'
                         '&pf_rd_r=5QZFK381M65Q9B7H90E7&pf_rd_t=0&pf_rd_p=55c21ce1-047a-4190-bd23-78871098dae7'
                         '&pf_rd_i=cybermonday'
                     ])
    data = {}
    for deals_group in landing_scrap:
        # SCRAP DEAL GROUPS; INSERTING INTO SHEETS; CREATES TITLES
        data[deals_group] = deals_group_level(wd, deals_group)
    # SCRAP ITEMS
    for deals_group in data:
        # SCRAP DEAL GROUPS; INSERTING INTO SHEETS; CREATES TITLES
        for deal_idx in range(len(data[deals_group])):
            if data[deals_group][deal_idx].pop(1):
                data[deals_group][deal_idx] = asin_level(
                    wd, data[deals_group][deal_idx][-1],
                    data[deals_group][deal_idx][1],
                    data[deals_group][deal_idx][2],
                )
            else:
                data[deals_group][deal_idx] = deal_level(
                    wd, data[deals_group][deal_idx][1],
                    data[deals_group][deal_idx][2],
                )
    # SCRAP LAST ITEMS
    for deals_group in data:
        # SCRAP DEAL GROUPS; INSERTING INTO SHEETS; CREATES TITLES
        for deal_idx in range(len(data[deals_group])):
            deal = data[deals_group][deal_idx]
            if deal.get('is_asin'):
                continue

            for asin_id in range(len(deal['items'])):
                data[deals_group][deal_idx]['items'][asin_id] = asin_level(wd, deal[-1], deal[1], deal[2])

    try:
        while True:
            wd.driver.close()
    except Exception as e:
        raise e


if __name__ == '__main__':
    scrap_main_page()
