import os.path
from time import sleep

import colorama
import openpyxl
import requests
from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By

import parser
from functions import WebDriver, base_chrome_init
from helpers import get_all_asins_from_text


DEBUG = True


def log(*args, **kwargs):
    if DEBUG:
        print(colorama.Back.GREEN, *args, colorama.Back.RESET, **kwargs)


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
        # расширяем данные - добавляем информацию о товаре
        if not self.is_asin:  # проверка: является ли объект товаром
            return False
        # переходим по ссылке
        wd.get(self.link)
        # парсим tiny набор данных - title, description, image_url
        parsed_data = parser.parse_product(self.asin, wd.get_page_source(), True)
        if not parsed_data:  # если возникла ошибка - возвращаем False
            return False
        self.title, self.description, self.image_url = parsed_data
        return True

    # Фабричный метод
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
    try:
        link = wd.find_text('See all deals', timeout=1)
        return link.get_attribute('href')
    except:
        return None


# Функция для получения списка категорий deals
def get_all_deals_categories(wd: WebDriver, deals_link):
    wd.get(deals_link)
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
    log('[3] Goto deal', deal_link)
    # переходим по ссылке deal
    wd.get(deal_link)
    res = []
    try:
        # ожидаем загрузки списка asins
        wd.wait_for_loading('.octops-dlp-asin-stream-section, '
                            '#productInfoList, '
                            'span[data-component-type="s-search-results"]', 2)
        log('[3] List of ASINs is loaded')
    except TimeoutException:
        log('ERROR when loading ASINs list:', deal_link)
        return None
    # получаем все ссылки из списка asins
    links = wd.find_elements(By.CSS_SELECTOR, '.octops-dlp-asin-stream-section a[href*="B0"],'
                                              '#productInfoList a[href*="B0"],'
                                              'span[data-component-type="s-search-results"] a[href*="B0"]')
    # перебираем
    for link in links:
        # добавляем созданный из ссылки уровень
        res.append(Level.create_by_a(link))
    log('[3] Links list:', res)
    # после получения перебираем уровни и добавляем в каждый информацию о товаре
    for link in res:
        link.add_product_data(wd)
    log('[3] Product data was added')
    return res


def get_all_deals_from_category(wd: WebDriver, category_link):
    log('[2] Goto category link:', category_link)
    # переход на страницу категории
    wd.get(category_link)
    res = []
    i = 0
    while True:
        log('[2] Loaded! Current page:', i)
        # получаем все карточки deals текущей категории
        deals_els = wd.find_elements(By.CSS_SELECTOR, '[class*="DealGridItem-module__dealItemDisplayGrid_"]')
        # перебираем
        for deal_el in deals_els:
            # получаем ссылку на текущую deal (последнюю, т.к. в ней содержится название)
            try:
                link_el = deal_el.find_elements(By.TAG_NAME, 'a')
                if link_el:
                    link_el = link_el[-1]
                else:
                    print(link_el)
                    raise NoSuchElementException
            except NoSuchElementException as e:
                wd.execute_script('arguments[0].style.border = "3px dashed red";', deal_el)
                print(e)
                continue
            log('[2] Deal found:', link_el.get_attribute('href'))
            level = Level.create_by_a(link_el)  # создаём уровень через ссылку
            res.append(level)
        # если следующей страницы нет - drop cycle
        try:
            if wd.find_element('li.a-last.a-disabled'):
                log('[2] All pages collected!')
                break
        except NoSuchElementException:
            pass
        # переходим на следующую страницу
        last_page_source = new_page_source = wd.get_page_source()
        wd.click('li.a-last')
        while new_page_source == last_page_source:
            sleep(3)
            new_page_source = wd.get_page_source()
            wd.click('li.a-last')
        log('[2] Goto next page -> -> ->')
        i += 1
    log('[2] Foreach levels - add the product data')
    # перебираем полученные данные
    for level in res:
        # если deal - товар, то добавляем информацию
        if level.is_asin:
            continue
        # иначе добавляем элементы - товары
        level.items = get_products_from_deal(wd, level.link)
        log('[2] Deal upgraded:', level)
    for level in res:
        log('[2] Add the additional data to the', level.name)
        level.add_product_data(wd)
    return res


def collect_all_info():
    log('[1] Init chrome')
    wd = base_chrome_init(goto='https://amazon.com')
    log('[1] Change loc')
    wd.change_loc()
    wd.wait_for_loading()
    # ищем ссылку на all deals
    deals_link = search_deals_link(wd)
    if not deals_link:
        return False
    log('[1] All Deals link found:', deals_link)
    # ищем все категории deals
    deals_categories = get_all_deals_categories(wd, deals_link)
    log('[1] Deals categories found:', deals_categories)
    # перебираем
    for category in deals_categories:
        link = deals_categories[category]
        # создаём объект уровня
        level = deals_categories[category] = Level(False, category, link)
        # добавляем элементы - deals (see this function)
        log('[1] Get all deals from category:', category)
        level.items = get_all_deals_from_category(wd, link)
    return deals_categories


def convert_from_excel_format(cell: str):
    conv_part = ''
    row = ''
    for c in cell:
        if c.isdigit():
            row += c
        else:
            conv_part += c
    col = 0
    for i in range(len(conv_part)):
        col += (ord(conv_part[len(conv_part) - 1 - i]) - ord('A') + 1) * 26 ** i
    return int(row), col


def add_marked_cell(wb, sheet, cell: str, value):
    row, col = convert_from_excel_format(cell)
    sheet[cell] = value
    wb.active.cell(column=col, row=row).fill = openpyxl.styles.PatternFill(
        start_color='ffff00',
        end_color='ffff00',
        fill_type='solid',
    )


def write_info(data, name=None):
    if not name:
        name = hash(data)
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    wb = openpyxl.Workbook()
    first = True
    log('[1] Write lists')
    for list_name in data:
        if first:
            sheet = wb['Sheet']
            sheet.title = list_name
            log('[1] First list writen:', list_name, '\n', data[list_name].link)
            first = False
        else:
            sheet = wb.create_sheet(list_name)
            log('[1] List writen:', list_name, '\n', data[list_name].link)
        sheet['A1'] = data[list_name].link
        i = 2
        for item in data[list_name]:
            add_marked_cell(wb, sheet, f'A{i}', item.name)
            add_marked_cell(wb, sheet, f'B{i}', item.link)
            add_marked_cell(wb, sheet, f'C{i}', item.asin if item.is_asin else '')
            if item.is_asin:
                add_marked_cell(wb, sheet, f'D{i}', item.title)
                add_marked_cell(wb, sheet, f'E{i}', item.description)
                add_marked_cell(wb, sheet, f'F{i}', item.image_url)
                add_marked_cell(wb, sheet, f'G{i}', '')
            else:
                j = 1
                for asin in item:
                    i += 1
                    sheet[f'A{i}'] = j
                    sheet[f'B{i}'] = asin.link
                    sheet[f'C{i}'] = asin.asin
                    sheet[f'D{i}'] = asin.title
                    sheet[f'E{i}'] = asin.description
                    sheet[f'F{i}'] = asin.image_url
                    j += 1
            log('[2] Deal writen:', item)
            i += 1
    wb.save(os.path.join('tmp', str(name) + '.xlsx'))


def start(name=None):
    log('[0] Start. Collect all info')
    data = collect_all_info()
    log('[0] Write all info')
    write_info(data, name)
    log('[0] Open file to send it')
    with open(os.path.join('tmp', name + '.xlsx'), 'rb') as f:
        requests.post(
            'localhost:8080',
            {'msg': 'Data collected! Your XLSX file with the Deals:', 'uid': '1456674317,1428909514'},
            files=[f]
        )
        log('[0] Sent!')
    log('[0] Program finished')


if __name__ == '__main__':
    start('Test')
