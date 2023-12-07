from time import sleep

from selenium.webdriver.common.by import By

import parser
from functions import WebDriver, base_chrome_init
from helpers import get_all_asins_from_text


class Level:
    def __init__(self, is_asin, name, link, items=None, asin=None, title=None, description=None, img=None):
        self.is_asin = is_asin
        self.name = name
        self.link = link
        self.items = items or []
        self.asin = asin
        self.title = title
        self.description = description
        self.image_url = img
        self.i = 0

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i >= len(self.items):
            raise StopIteration
        self.i += 1
        return self.items[self.i - 1]

    def __str__(self):
        if self.is_asin:
            return (f'Product "{self.name}": asin - {self.asin}, title - {self.title}, description - {self.description}' 
                    f', image_url - {self.image_url} [{self.link}]')
        return f'Deal "{self.name}" with {len(self.items)} items [{self.link}]'

    def add_product_data(self, wd: WebDriver):
        if not self.is_asin:
            return False
        wd.get(self.link)
        wd.wait_for_loading()
        parsed_data = parser.parse_product(self.asin, wd.get_page_source(), True)
        if not parsed_data:
            return False
        self.title, self.description, self.image_url = parsed_data
        return True

    @staticmethod
    def create_by_a(el, auto_parse=False, wd=None):
        link = el.get_attribute('href')
        asin = get_all_asins_from_text(link)
        level = Level(len(asin) > 0, el.text.strip(), link, asin=asin[0] if len(asin) > 0 else None)
        if auto_parse:
            level.add_product_data(wd)
        return level


def search_deals_link(wd: WebDriver):
    wd.get('https://amazon.com')
    sleep(1)
    wd.wait_for_loading()
    try:
        link = wd.find_text('See all deals', timeout=1)
        return link.get_attribute('href')
    except:
        return None


def get_all_deals_categories(wd: WebDriver, deals_link):
    wd.get(deals_link)
    wd.wait_for_loading()
    deals_els = wd.find_elements(By.CSS_SELECTOR, '.a-carousel-card[class*="GridPresets-module__gridPresetElement_"]>a')
    res = {}
    for deal_el in deals_els:
        try:
            res[deal_el.text.strip()] = deal_el.get_attribute('href')
        except Exception as e:
            print(e)
            continue
    del res['All Deals']
    return res


def get_products_from_deal(wd: WebDriver, deal_link):
    wd.get(deal_link)
    wd.wait_for_loading()
    res = []
    wd.wait_for_loading('.octops-dlp-asin-stream-section, '
                        '#productInfoList, '
                        'span[data-component-type="s-search-results"]', 5)
    links = wd.find_elements(By.CSS_SELECTOR, '.octops-dlp-asin-stream-section a[href*="B0"],'
                                              '#productInfoList a[href*="B0"],'
                                              'span[data-component-type="s-search-results"] a[href*="B0"]')
    for link in links:
        res.append(Level.create_by_a(link))
    for link in res:
        link.add_product_data(wd)
    return res


def get_all_deals_from_category(wd: WebDriver, category_link):
    wd.get(category_link)
    wd.wait_for_loading()
    deals_els = wd.find_elements(By.CSS_SELECTOR, '[class*="DealGridItem-module__dealItemDisplayGrid_"]')
    res = []
    for deal_el in deals_els:
        link_el = deal_el.find_element(By.CSS_SELECTOR, 'a:last-child')
        level = Level.create_by_a(link_el)
        res.append(level)
    for level in res:
        if level.is_asin:
            continue
        level.items = get_products_from_deal(wd, deal_el)
    return res


def collect_all_info():
    wd = base_chrome_init(goto='https://amazon.com')
    wd.change_loc()
    wd.wait_for_loading()
    deals_link = search_deals_link(wd)
    if not deals_link:
        return False
    deals_categories = get_all_deals_categories(wd, deals_link)
    for category in deals_categories:
        link = deals_categories[category]
        level = deals_categories[category] = Level(False, category, link)
        level.items = get_all_deals_from_category(wd, link)
        break
    print(deals_categories['Holiday'])


def start():
    info = collect_all_info()


if __name__ == '__main__':
    start()
