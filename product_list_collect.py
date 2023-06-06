import os.path
import random
import sys
import time
from time import sleep
import re
from typing import Union

from selenium.common import WebDriverException
from selenium.webdriver import Keys

from initialization import initialize, CustomSelenium
from configuration import TIMEOUT, update_config, MAX_RETRIES, State
from uniqulizer import uniqulize_by_df

selenium: Union[CustomSelenium, None] = None

try:
    # SETTINGS UP
    categories = ['pc', 'computer', 'hair', 'gum', 'gummies', 'gym']
    category = categories[random.randint(0, len(categories) - 1)]
    FOLDER_NAME = input('Please, type the new directory name or exit to close the script: ')
    while not FOLDER_NAME:
        FOLDER_NAME = input('Please, type the new directory name: ')
    if FOLDER_NAME.strip().lower() == 'exit':
        sys.exit(0)

    products_list_filepath = input('Please, type the products list filepath or exit: ')
    while not products_list_filepath:
        products_list_filepath = input('Please, type the products list filepath: ')
    if products_list_filepath.strip().lower() == 'exit':
        sys.exit(0)

    with open(products_list_filepath) as products_list_file:
        products_list_raw = list(products_list_file)

    asins = []
    pattern = re.compile('[A-Z0-9]{10}')
    for row in products_list_raw:
        if not row.strip():
            continue
        m = pattern.search(row)
        if m:
            asins.append(m.group())

    if not os.path.exists('./' + FOLDER_NAME):
        os.makedirs(FOLDER_NAME)

    if '-v' in sys.argv:
        print('Products loading started...')
    # PREPARE
    selenium: CustomSelenium = initialize()
    selenium.get('https://www.amazon.com/')
    # type the request
    search_input = selenium.get_items('#twotabsearchtextbox,#nav-bb-search', single=True)
    search_input.send_keys(category)
    sleep(5)
    search_input.send_keys(Keys.ENTER)
    sleep(5)
    selenium.insert_jquery()
    if '-v' in sys.argv:
        print('Web driver loaded successfully')

    st = State('products_list_collect__state.dat', directory=FOLDER_NAME)
    ready = []
    if st['ready']:
        ready = st['ready'].split(',')
    else:
        st['ready'] = ''

    error = False
    f = open(os.path.join(FOLDER_NAME, 'products_list.csv'), 'w')
    f.write('asin,rating,reviews_count,5star,4star,3star,2star,1star\n')
    f.close()

    # processing
    for asin in asins:
        if asin in ready:
            continue
        selenium.get(f'https://www.amazon.com/dp/{asin}')
        f = open(os.path.join(FOLDER_NAME, 'products_list.csv'), 'a')
        selenium.wait('#titleSection')

        rating_el = selenium.get_items('#acrPopover a span.a-size-base.a-color-base', wait=False, single=True)
        if rating_el:
            data = [asin, rating_el.text.strip()]
            count_el = selenium.get_items('#acrCustomerReviewText', wait=False, single=True)
            data.append(count_el.text.split(' ')[0].replace(',', '').strip() if count_el else '0')
            ratings = selenium.get_items(
                '''#reviewsMedley [data-action="reviews:filter-action:push-state"]
                #histogramTable.a-normal.a-align-center.a-spacing-base tr td.a-text-right.a-nowrap span'''
            )
            if ratings:
                for item in ratings:
                    data.append(item.text.strip())
            else:
                for i in range(5):
                    data.append('0')
            f.write(','.join(data))
            f.write('\n')
        else:
            f.write(f'{asin},0.0,0,0,0,0,0,0\n')

        f.close()
        st['ready'] = ','.join(filter(lambda x: bool(x), st['ready'].split(',') + [asin]))
        st.write()

    selenium.close()
    if '-v' in sys.argv:
        print('Make the data unique...')
    uniqulize_by_df(
        os.path.join(FOLDER_NAME, 'products_list.csv'),
        os.path.join(FOLDER_NAME, 'uniqulized_products_list.csv'),
        0
    )
    if '-v' in sys.argv:
        if error:
            print('Products collecting ends with some errors')
        else:
            print('Products collecting done. Now you need to start another script: `reviews_collect.py`')
except WebDriverException as e:
    print('An error was occurred.')

    if selenium:
        interval = time.time() - selenium.start_timestamp
        if interval < TIMEOUT:
            TIMEOUT = interval
            update_config()
        selenium.close()

    if '-v' in sys.argv:
        if '-s' in sys.argv:
            raise e
        else:
            print(e)

    n = MAX_RETRIES
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '-n' and sys.argv[i + 1].isdigit():
            n -= int(sys.argv[i + 1])
            break
    if n > 0:
        args = [sys.executable, sys.argv[0], '-v'] if '-v' in sys.argv else [sys.executable, sys.argv[0]]
        args.append('-n')
        args.append(str(n - 1))
        os.execv(sys.executable, args)
except Exception as e:
    print('An error was occurred.')
    if selenium:
        selenium.close()
    if '-v' in sys.argv:
        raise e
