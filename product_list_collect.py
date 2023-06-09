import os.path
import random
import sys
import time
from time import sleep
import re
from typing import Union

from selenium.common import WebDriverException, InvalidSessionIdException
from selenium.webdriver import Keys

from initialization import initialize, CustomSelenium
from configuration import TIMEOUT, update_config, MAX_RETRIES, State
from uniqulizer import uniqulize_by_df

selenium: Union[CustomSelenium, None] = None

try:
    # SETTINGS UP
    categories = ['pc', 'computer', 'hair', 'gum', 'gummies', 'gym']
    category = categories[random.randint(0, len(categories) - 1)]

    st = State('last_product_list_collection__state.dat')
    if st['folder']:
        FOLDER_NAME = st['folder']
    else:
        FOLDER_NAME = input('Please, type the new directory name or exit to close the script: ')
        while not FOLDER_NAME:
            FOLDER_NAME = input('Please, type the new directory name: ')
        if FOLDER_NAME.strip().lower() == 'exit':
            sys.exit(0)

    if st['filepath']:
        products_list_filepath = st['filepath']
    else:
        products_list_filepath = input('Please, type the products list filepath or exit: ')
        while not products_list_filepath:
            products_list_filepath = input('Please, type the products list filepath: ')
        if products_list_filepath.strip().lower() == 'exit':
            sys.exit(0)

    # st.write()

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
    sleep(10)
    if '-C' in sys.argv:
        if not selenium.captcha_solve():
            print("CAPTCHA can't be solved!")
            selenium.close()
            sys.exit(0)
    else:
        if not selenium.captcha_check(not ('-c' in sys.argv)):
            print('CAPTCHA!')
            selenium.close()
            sys.exit(0)
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
    filepath = os.path.join(FOLDER_NAME, 'products_list.csv')
    if not os.path.exists(filepath):
        f = open(filepath, 'w')
        f.write('asin,link,title,rating,reviews_count,5star,4star,3star,2star,1star,price,brand,main_image\n')
        f.close()
    locations = 'NZ,AU,JP,IT,FI,SE,FR,CA,DE,ES,AT,KZ,MX,SG,GB,UM,BE,BO,BR,EG,GR,IE,IL,PT,TR,KR,CN'.split(',')

    # processing
    for asin in asins:
        if asin in ready:
            continue
        selenium.get(f'https://www.amazon.com/dp/{asin}')
        selenium.insert_jquery()
        selenium.wait('#twotabsearchtextbox, #sectionTitle,'
                      ' div.a-box.a-alert.a-alert-info.a-spacing-base > div.a-box-inner > h4')
        if '-C' in sys.argv:
            if not selenium.captcha_solve():
                print("CAPTCHA can't be solved!")
                selenium.close()
                sys.exit(0)
        else:
            if not selenium.captcha_check(not ('-c' in sys.argv)):
                print('CAPTCHA!')
                selenium.close()
                sys.exit(0)

        selenium.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        selenium.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            f'countryCode: "CN",'
            'deviceType: "web",'
            f'distinct: "CN",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        selenium.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        f = open(os.path.join(FOLDER_NAME, 'products_list.csv'), 'a', encoding='utf-8')
        # The row of CSV file
        row = f'{asin},https://www.amazon.com/dp/{asin}'

        # First data
        row += ','
        title_el = selenium.get_items('#titleSection', wait=False, single=True)
        if title_el:
            row += title_el.text.strip()

        # Rating
        rating_el = selenium.get_items('#acrPopover a span.a-size-base.a-color-base', wait=False, single=True)
        if rating_el:
            data = [rating_el.text.strip()]
            count_el = selenium.get_items('#acrCustomerReviewText', wait=False, single=True)
            data.append(count_el.text.split(' ')[0].replace(',', '').strip() if count_el else '0')
            ratings = selenium.get_items(
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
        price_whole_el = selenium.get_items(
            '.a-price.aok-align-center .a-price-whole', wait=False, single=True)
        price_fraction_el = selenium.get_items(
            '.a-price.aok-align-center .a-price-fraction', wait=False, single=True)
        if not price_whole_el or not price_fraction_el:
            for loc in locations:
                selenium.insert_jquery()
                selenium.execute_script(
                    '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
                    '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
                )
                selenium.execute_script(
                    '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
                    '{actionSource: "glow",'
                    f'countryCode: "{loc}",'
                    'deviceType: "web",'
                    f'distinct: "{loc}",'
                    'locationType: "COUNTRY",'
                    'pageType: "Detail",'
                    'storeContext: "hpc"}'
                    ')'
                )
                selenium.execute_script(
                    '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
                    '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
                )
                sleep(1)
                selenium.refresh()
                sleep(1)
                selenium.insert_jquery(True)
                selenium.wait('#twotabsearchtextbox, #sectionTitle,'
                              ' div.a-box.a-alert.a-alert-info.a-spacing-base > div.a-box-inner > h4')
                if '-C' in sys.argv:
                    if not selenium.captcha_solve():
                        print("CAPTCHA can't be solved!")
                        selenium.close()
                        sys.exit(0)
                else:
                    if not selenium.captcha_check(not ('-c' in sys.argv)):
                        print('CAPTCHA!')
                        selenium.close()
                        sys.exit(0)
                price_whole_el = selenium.get_items(
                    '.a-price.aok-align-center .a-price-whole', wait=False, single=True)
                price_fraction_el = selenium.get_items(
                    '.a-price.aok-align-center .a-price-fraction', wait=False, single=True)
                if price_whole_el and price_fraction_el:
                    break
        if price_whole_el and price_fraction_el:
            row += price_whole_el.text.strip() + '.' + price_fraction_el.text.strip()
        # Brand
        row += ','
        brand_el = selenium.get_items(
            '#productOverview_feature_div table .po-brand td.a-span9 span', wait=False, single=True
        )
        if brand_el:
            row += brand_el.text.strip()

        # Main image
        row += ','
        image_el = selenium.get_items('#imgTagWrapperId > img', wait=False, single=True)
        if image_el and (image_el.get_attribute('src') or image_el.get_property('src')):
            row += image_el.get_attribute('src') or image_el.get_property('src')

        f.write(f'{row}\n')
        print(row)
        f.flush()
        f.close()
        st['ready'] = ','.join(filter(lambda x: bool(x), st['ready'].split(',') + [asin]))
        st.write()

    try:
        selenium.close()
    except InvalidSessionIdException:
        pass

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
