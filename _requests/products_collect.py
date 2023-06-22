import os
import urllib
from time import sleep
from typing import Union
from urllib.parse import quote_plus

from selenium.common import InvalidSessionIdException
from selenium.webdriver import Keys

from config import State
from _requests.BaseRequest import BaseRequest, initialize, STATUS


class ProductCollect(BaseRequest):
    method = 'post'

    @property
    def url(self):
        return 'https://www.amazon.com/s/query' + self.params_to_str() if self.params else 'https://www.amazon.com'

    def __init__(self, webdriver, category, folder, state):
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

        pagination_button = self.get_items('a.s-pagination-item.s-pagination-button', wait=False, single=True)
        if pagination_button:
            self.execute_script('arguments[0].scrollIntoView();', pagination_button)
            sleep(2)
            pagination_button.click()
            sleep(5)
        base_url = self.webdriver.current_url
        params_str = base_url.split('?')[1]
        args = dict(list(tuple(map(lambda x: urllib.parse.quote(urllib.parse.unquote(x)),
                                   map(lambda x: x.replace('+', ' '), item.split('='))))
                         for item in params_str.split('&')))
        self.set_params(**args)
        self.wait_for_loading()
        self.insert_jquery(True)

        self.folder = folder
        self.state = state
        self.args = args

    def send(self, page):
        self.params.update(page=str(page))
        return super().send(True)

    def processing(self, f):
        raw_data = super().processing()
        count_all_products = 0
        rows = []

        for item in raw_data:
            if count_all_products > 0 and count_all_products // 48 + 1 < self.params['pageNumber']:
                return count_all_products
            if 'data-main-slot:search-result-' in item[1]:
                rows.append(item[2]['asin'] + '\n')

        f.writelines(rows)
        f.close()

        return count_all_products


wd = ev = None


def products_collect(folder, category):
    global ev, wd

    def close(status: Union[None, str] = 'error'):
        global wd, ev
        try:
            if ev:
                ev.set()
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
        if not os.path.exists(folder):
            os.mkdir(folder)

        st = State('products_collect.state', folder, {'page': '1'})

        max_page = 7
        page = int(st['page'])

        # wd, thread, ev = initialize(True)
        wd = initialize()

        sleep(10)

        if not wd:
            return close()

        collecting = ProductCollect(wd, category, folder, st)

        while page <= max_page:
            if not collecting.success:
                return close()

            if not collecting.send(page):
                return close()

            count_all_results\
                = collecting.processing(open(os.path.join(folder, 'products.list'), 'a' if page > 1 else 'w'))

            if count_all_results > 0:
                max_page = min(7, count_all_results // 48 + 1)

            page += 1
            st['page'] = str(page)
            st.write()

        wd.close()

        from uniqulizer import uniqulize_by_df

        uniqulize_by_df(
            os.path.join(folder, 'products.list'),
            os.path.join(folder, 'uniqulized_products.list'),
            0
        )
        os.unlink(os.path.join(folder, 'products.list'))
        os.rename(
            os.path.join(folder, 'uniqulized_products.list'),
            os.path.join(folder, 'products.list'),
        )
        return close('success')
    except KeyboardInterrupt:
        return close('closed')
    except Exception as e:
        print(e)
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
        category = set(sys.argv[args_start_index + 1].strip().split(','))
    else:
        sys.exit(1)

    res = products_collect(folder, category)
    if res == STATUS['success']:
        print('success')
    elif res == STATUS['error']:
        print('error')
    elif res == STATUS['closed']:
        print('closed')

