import os
import re
from time import sleep
from typing import Union
from urllib.parse import quote_plus

from selenium.common import InvalidSessionIdException
from selenium.webdriver import Keys

from config import State
from _requests.BaseRequest import BaseRequest, initialize, STATUS


class ProductDetailsCollect(BaseRequest):
    def __init__(self, webdriver, category, asins, folder, state):
        super().__init__(webdriver)
        if not self.success:
            return

        search_input = self.get_items('#twotabsearchtextbox,#nav-bb-search', wait=False, single=True)

        if not search_input:
            self.success = False
            return

        search_input.send_keys(category)
        sleep(3)
        search_input.send_keys(Keys.ENTER)
        self.wait_for_loading()
        self.insert_jquery()
        self.asins = asins
        self.folder = folder
        self.state = state

    def start(self):
        for asin in self.asins:
            # goto product
            link = f'https://www.amazon.com/dp/{asin}'
            self.webdriver.get(link)
            if not self.captcha_solve():
                print('captcha')
                self.webdriver.close()
                sys.exit(1)
            self.wait_for_loading()
            # open data file
            f = open(os.path.join(self.folder, 'products_list.csv'), 'a', encoding='utf-8')
            # The row of CSV file
            row = f'{asin},{link}'

            # First data
            row += ','
            title_el = self.get_items('#titleSection', wait=False, single=True)
            if title_el:
                row += title_el.text.strip().replace(',', ';')

            # Rating
            rating_el = self.get_items('#acrPopover a span.a-size-base.a-color-base', wait=False, single=True)
            if rating_el:
                data = [rating_el.text.strip()]
                count_el = self.get_items('#acrCustomerReviewText', wait=False, single=True)
                data.append(count_el.text.split(' ')[0].replace(',', '').strip() if count_el else '0')
                ratings = self.get_items(
                    '''#reviewsMedley [data-action="reviews:filter-action:push-state"]
                    #histogramTable.a-normal.a-align-center.a-spacing-base tr td.a-text-right.a-nowrap span'''
                )
                if ratings:
                    for item in ratings:
                        item = item.text.strip()
                        if item:
                            data.append(item)
                else:
                    for i in range(5):
                        data.append('0')
                row += ',' + (','.join(data))
            else:
                row += ',0.0,0,0,0,0,0,0'

            # Price
            row += ','
            price_whole_el = self.get_items(
                '.a-price.aok-align-center .a-price-whole', wait=False, single=True)
            price_fraction_el = self.get_items(
                '.a-price.aok-align-center .a-price-fraction', wait=False, single=True)
            if price_whole_el and price_fraction_el:
                row += price_whole_el.text.strip() + '.' + price_fraction_el.text.strip()
            # Brand
            row += ','
            brand_el = self.get_items(
                '#productOverview_feature_div table .po-brand td.a-span9 span', wait=False, single=True
            )
            if brand_el:
                row += brand_el.text.strip().replace(',', ';')

            # Main image
            row += ','
            image_el = self.get_items('#imgTagWrapperId > img', wait=False, single=True)
            if image_el and (image_el.get_attribute('src') or image_el.get_property('src')):
                row += quote_plus(image_el.get_attribute('src') or image_el.get_property('src'))\
                    .replace('https%3A%2F%2F', 'https://').replace('%2F', '/')

            f.write(f'{row}\n')
            f.flush()
            f.close()
            self.state['ready'] = ','.join(filter(lambda x: bool(x), self.state['ready'].split(',') + [asin]))
            self.state.write()


def get_asins(folder):
    products_list_filepath = os.path.join(folder, 'products.list')
    with open(products_list_filepath) as products_list_file:
        products_list_raw = list(products_list_file)
    asins = set()
    pattern = re.compile('[A-Z0-9]{10}')
    for row in products_list_raw:
        if not row.strip():
            continue
        m = pattern.search(row)
        if m:
            asins.add(m.group())
    return asins


wd = None


def products_details_collect(folder, asins):

    def close(status: Union[None, str] = 'error'):
        global wd
        try:
            if wd:
                wd.close()
                wd = None
        except InvalidSessionIdException:
            pass
        finally:
            if status:
                return STATUS[status]

    try:
        import sys
        import os
        import re
        import random

        # SETTINGS UP
        categories = ['pc', 'computer', 'hair', 'gum', 'gummies', 'gym']
        category = categories[random.randint(0, len(categories) - 1)]

        if not os.path.exists(folder):
            os.mkdir(folder)

        st = State('products_details_collect.state', folder, {'ready': ''})

        ready = st['ready']
        if ready:
            ready = ready.split(',')
            asins_copy = []

            for item in asins:
                if item not in ready:
                    asins_copy.append(item)

            asins = asins_copy

        if len(asins) > 0:
            wd = initialize()

            if not wd:
                return close()

            collecting = ProductDetailsCollect(wd, category, asins, folder, st)
            if not collecting.success:
                return close()

            filepath = os.path.join(folder, 'products_list.csv')
            if not os.path.exists(filepath):
                f = open(filepath, 'w')
                f.write('asin,link,title,rating,reviews_count,5star,4star,3star,2star,1star,price,brand,main_image\n')
                f.close()

            collecting.start()

            wd.close()

        from uniqulizer import uniqulize_by_df

        if os.path.exists(os.path.join(folder, 'products_list.csv')):
            uniqulize_by_df(
                os.path.join(folder, 'products_list.csv'),
                os.path.join(folder, 'uniqulized_products_list.csv'),
                0
            )
        if os.path.exists(os.path.join(folder, 'uniqulized_products_list.csv')):
            os.unlink(os.path.join(folder, 'products_list.csv'))
            os.rename(
                os.path.join(folder, 'uniqulized_products_list.csv'),
                os.path.join(folder, 'products_list.csv')
            )
        return close('success')
    except KeyboardInterrupt:
        return close('closed')
    except Exception as e:
        return close()


if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    args_start_index = 1
    for i in sys.argv:
        if i == '--start':
            break
        args_start_index += 1

    # SETTINGS UP
    folder = sys.argv[args_start_index]

    if len(sys.argv) > args_start_index + 1 and sys.argv[args_start_index + 1]:
        asins = set(sys.argv[args_start_index + 1].strip().split(','))
    else:
        asins = get_asins(folder)

    res = products_details_collect(folder, asins)
    if res == STATUS['success']:
        print('success')
    elif res == STATUS['error']:
        print('error')
    elif res == STATUS['closed']:
        print('closed')
    
