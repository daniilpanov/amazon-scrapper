import os
from json import JSONDecoder, JSONEncoder, JSONDecodeError
from time import sleep
from typing import List

import openpyxl
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Keys

import parser
from collect_all_deals import prepare_link
from functions import WebDriver, base_chrome_init
from helpers import get_all_asins_from_text, log, parse_args


class Level:
    name: str | None
    link: str | None
    items: List['Level']
    asin: str | None
    brand: str | None
    score: int | None
    is_last_group: bool
    ready: bool
    all_items_preloaded: bool
    i: int = 0

    def __init__(self, name, link: str, items=None, is_last_group=None, asin=None, score=None, brand=None, ready=False, all_items_preloaded=False):
        self.name = name
        if link and not link.strip().startswith('https://amazon.com') and not link.strip().startswith('https://www.amazon.com'):
            link = 'https://amazon.com' + link
        self.link = link
        self.is_last_group = is_last_group
        self.asin = asin
        self.score = score
        self.brand = brand
        self.ready = ready
        self.all_items_preloaded = all_items_preloaded
        self.items = []
        if items:
            self.set_items(items)

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
        if self.asin:
            return (f'Product "{self.name}": asin - {self.asin}, brand - {self.brand}, score - {self.score}' 
                    f' [{self.link}] {self.ready}')
        return f'Department "{self.name}" with {len(self.items or [])} items [{self.link}] {self.ready}'

    def __hash__(self):
        return hash(str(self))

    def __len__(self):
        return len(self.items or [])

    def set_items(self, items: List['Level']):
        self.items.extend(items)

    def check_exists(self, name):
        for item in self.items:
            if name == item.name:
                return True
        return False

    def add_item(self, item: 'Level', unique=False):
        if not unique or not self.check_exists(item.name):
            self.items.append(item)

    def to_list(self):
        res = []
        for item in [self.name, self.link, self.asin, self.description, self.image_url]:
            if item:
                res.append(item)

        return res

    def to_dict(self):
        items = []
        if self.items:
            for item in self.items:
                items.append(item.to_dict())

        return {'name': self.name, 'link': self.link, 'is_last_group': self.is_last_group} | ({
            'asin': self.asin,
            'score': self.score,
            'brand': self.brand,
        } if self.asin else {'items': items}) | {'ready': self.ready, 'all_items_preloaded': self.all_items_preloaded}

    @staticmethod
    def from_dict(d):
        level = Level(d.get('name'), d.get('link'), None, d.get('is_last_group', False),
                      d.get('asin'), d.get('score'), d.get('brand'), d.get('ready', False),
                      d.get('all_items_preloaded', False))
        items = []
        for item in d.get('items', []):
            items.append(Level.from_dict(item))
        level.set_items(items)
        return level

    def add_product_data(self, wd: WebDriver):
        # расширяем данные - добавляем информацию о товаре
        if not self.asin or self.ready:  # проверка: является ли объект товаром и готов ли товар
            return False
        # переходим по ссылке
        wd.get(self.link)
        sleep(.1)
        wd.wait_for_loading()
        # парсим tiny набор данных - title, description, image_url
        parsed_data = parser.parse_product(self.asin, wd.get_page_source(), -1)
        if not parsed_data:  # если возникла ошибка - возвращаем False
            return False
        self.name, self.brand = parsed_data
        self.ready = True
        return True

    # Фабричный метод
    @staticmethod
    def create_by_a(el, auto_parse=False, wd=None):
        if type(el) not in (tuple, list):
            link = prepare_link(el)
            name = el.text.strip()
        else:
            name, link = el
        asin = get_all_asins_from_text(link)
        level = Level(name, link, asin=asin[0] if len(asin) > 0 else None)
        if auto_parse and wd:
            level.add_product_data(wd)
        return level


class XSheet:
    wb: openpyxl.Workbook
    current_sheet_name: str = None
    current_row: int = 1
    current_subcategory_row: int = 1
    departments_tree: Level
    jsd: JSONDecoder
    jse: JSONEncoder

    def __init__(self, name):
        self.jsd = JSONDecoder()
        self.jse = JSONEncoder()
        self.departments_tree = self.load(name) or Level(name, None)
        path = os.path.join('tmp__', f'{name}.xlsx')
        if os.path.exists(path):
            self.wb = openpyxl.load_workbook(path)
        else:
            self.wb = openpyxl.Workbook()

    def set_link(self, link):
        self.departments_tree.link = link
        return link

    @property
    def name(self):
        return self.departments_tree.name

    def save(self):
        if not os.path.isdir('tmp__'):
            os.mkdir('tmp__')
        with open(f'tmp__/{self.name}.json', 'w', encoding='utf-8') as f:
            f.write(self.jse.encode(self.departments_tree.to_dict()))

    def load(self, name):
        if not os.path.exists(f'tmp__/{name}.json'):
            return None
        with open(f'tmp__/{name}.json', encoding='utf-8') as f:
            try:
                d = self.jsd.decode(f.read())
            except JSONDecodeError as e:
                print(e)
                return None
        return Level.from_dict(d)

    def add_sheet(self, name, link):
        self.wb.create_sheet(name)
        self.current_sheet_name = name
        self.current_row = 1
        self.set_cells([link])
        self.current_subcategory_row = 1

    def set_cells(self, cols_vals: list[str | int], marked=False, row=None):
        cols = 'ABCDEFGHJKLMNOPQR'
        if row is None:
            row = self.current_row
        for col_num in range(len(cols_vals)):
            col = cols[col_num]
            self.wb[self.current_sheet_name][col + str(row)] = cols_vals[col_num]
        if marked:
            for i in range(1, len(cols) + 1):
                self.wb[self.current_sheet_name].cell(column=i, row=row).fill = openpyxl.styles.PatternFill(
                    start_color='ffff00',
                    end_color='ffff00',
                    fill_type='solid',
                )
        self.current_row += 1

    def to_xlsx(self):
        self.wb.save(os.path.abspath(os.path.join('tmp__', f'{self.name}.xlsx')))


def recursive_tree(tree: Level, wd: WebDriver, xsh: XSheet, name_only=None):
    if tree.ready:
        return
    # if links are not collected
    if not tree.all_items_preloaded:
        wd.get(tree.link)
        soup = BeautifulSoup(wd.get_page_source(), features='html.parser')
        view_tree = soup.find(role='tree')
        group = view_tree.find(role='group')
        if group is None or tree.name in group.text:
            tree.is_last_group = True
            for pg in range(1, 3):
                wd.get(tree.link + ('&pg=' + str(pg) if '?' in tree.link else '?pg=' + str(pg)))
                for _ in range(12):
                    body = wd.get_element('body')
                    body.send_keys(Keys.PAGE_DOWN)
                    sleep(.9)
                soup = BeautifulSoup(wd.get_page_source(), features='html.parser')
                links_a = soup.select('div.a-cardui[id*="asin-index"]')
                for div in links_a or []:
                    asin_div = div.select_one('div[data-asin]')
                    if not asin_div:
                        continue
                    asin = asin_div['data-asin']
                    a_tags = div.find_all('a')
                    a_tag = None
                    for a_tag_item in a_tags:
                        if a_tag_item.text:
                            a_tag = a_tag_item
                            break
                    if not a_tag:
                        continue
                    name = a_tag.text
                    if not name_only or name_only == name:
                        prod = Level(name, a_tag['href'], asin=asin)
                        score_item = asin_div.find(attrs={'class': 'zg-bdg-text'})
                        if score_item:
                            prod.score = score_item.text
                            if prod.score:
                                prod.score = int(prod.score.replace('#', '').strip())
                        tree.add_item(prod, True)
        else:
            tree.is_last_group = False
            links_a = group.find_all('a')
            for a_tag in links_a or []:
                name = a_tag.text
                if not name_only or name_only == name:
                    tree.add_item(Level(name, a_tag['href']), True)
        tree.all_items_preloaded = True
        xsh.save()
    # if links are already collected, or we have a links group
    if tree.is_last_group is False:
        # RECURSIVE_CALL: load tree
        # full loading
        for link in tree:
            if not name_only or name_only == link.name:
                recursive_tree(link, wd, xsh)
        xsh.save()
    # it is last-point group
    else:
        # ENDPOINT: load asins
        # full loading
        for link in tree:
            if not name_only or name_only == link.name:
                link.add_product_data(wd)
                xsh.save()


def recursive_find(tree: Level, name_only=None):
    asins = []
    for dep in tree:
        if dep.asin:
            asins.append(dep)
        elif name_only is None or dep.name == name_only:
            asins.extend(recursive_find(dep))
    return asins


def collect_all_info(xsheet: XSheet, dep_name=None):
    log('[1] Init chrome')
    wd = base_chrome_init(goto='https://amazon.com')
    log('[1] Change loc')
    wd.change_loc()
    wd.wait_for_loading()
    wd.get(xsheet.set_link('https://amazon.com/gp/bestsellers'))
    recursive_tree(xsheet.departments_tree, wd, xsheet, dep_name)
    xsheet.save()
    # asins = recursive_find(xsheet.departments_tree)
    log('[1] Tree collected:', xsheet.departments_tree)
    xsheet.departments_tree.ready = True
    xsheet.save()


def write_info(xsh: XSheet):
    pass


def start(sheet_name=None, dep_name=None, tg_note_users_ids: list[str] | None = None):
    if not tg_note_users_ids:
        tg_note_users_ids = []
    if not sheet_name:
        sheet_name = str(hash(tg_note_users_ids))
    xsh = XSheet(sheet_name)
    if not xsh.departments_tree.ready:
        log('[0] Start. Collect all info')
        collect_all_info(xsh, dep_name)
    log('[0] Write all info')
    write_info(xsh)
    log('[0] Open file to send it')
    with open(os.path.join('tmp__', sheet_name + '.xlsx'), 'rb') as f:
        requests.post(
            'localhost:8080',
            {'msg': 'Data collected! Your XLSX file with the Departments:', 'uid': ','.join(tg_note_users_ids)},
            files=[(sheet_name + '.xlsx', f)],
        )
        log('[0] Sent!')
    log('[0] Program finished')


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)
    try:
        start(
            params_dict.get('dep_name', 'ALL'),
            params_dict.get('dep_name'),
            params_dict.get('user', '1456674317,1428909514').split(',')
        )
        requests.post('http://localhost:8080/send_msg', {
            'msg': f'Departments collected: {params_dict.get("dep_name")}',
            'uid': params_dict.get('user', '1456674317,1428909514'),
        })
    except Exception as e:
        requests.post('http://localhost:8080/send_msg', {
            'msg': f'Error on collecting departments: {params_dict.get("dep_name")}\n' + str(e) + '\n',
            'uid': params_dict.get('user', '1456674317,1428909514'),
        })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
