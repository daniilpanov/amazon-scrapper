import os.path
import sys
import time
from time import sleep

from selenium.common import WebDriverException, InvalidSessionIdException
from selenium.webdriver import Keys

from Requests import ProductsRequest
from get_args import get_args
from initialization import initialize
from configuration import FOLDER_NAME, TIMEOUT, update_config, MAX_RETRIES, State
from uniqulizer import uniqulize_by_df

selenium = None

try:
    # SETTINGS UP
    category = input('Please, type the name of the products category to collect or exit to stop: ')
    while not category:
        category = input('Please, type the name of the products category to collect or exit to stop: ')
    if category.strip().lower() == 'exit':
        sys.exit(0)

    if '-v' in sys.argv:
        print('Products loading started...')
    # PREPARE
    selenium, thread = initialize(True)
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

    st = State('products_collect__state.dat')

    max_page = 7
    page = int(st['page'] or 1)

    args = get_args(selenium, True, True)
    if '-v' in sys.argv:
        print('arguments loaded successfully')
        print('-----------')
        print(args)
        print('-----------')

    sleep(10)
    thread.start()
    error = False

    # processing
    while page <= max_page:
        f = open(os.path.join(FOLDER_NAME, 'products_list.csv'), 'a' if page > 1 else 'w')
        args.update(page=page)
        req = ProductsRequest(FOLDER_NAME, f, **args)
        if not req.send(selenium, False):
            print('ERROR!')
            error = True
            break

        count_all_results = req.processing()
        if count_all_results > 0:
            max_page = count_all_results // 48 + 1 if count_all_results // 48 + 1 <= 7 else 7

        page += 1
        st['page'] = str(page)
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
