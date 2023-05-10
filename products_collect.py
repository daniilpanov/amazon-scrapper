import os.path
import sys
from time import sleep

from selenium.webdriver import Keys

from Requests import ProductsRequest
from get_args import get_args
from initialization import initialize
from configuration import FOLDER_NAME

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
    selenium = initialize()
    selenium.get('https://www.amazon.com/')
    # type the request
    search_input = selenium.get_items('#twotabsearchtextbox,#nav-bb-search', single=True)
    search_input.send_keys(category)
    sleep(5)
    search_input.send_keys(Keys.ENTER)
    sleep(5)
    if '-v' in sys.argv:
        print('Web driver loaded successfully')

    max_page = 7
    page = 1

    args = get_args(selenium, True, True)

    # processing
    with open(os.path.join(FOLDER_NAME, 'products_list.csv'), 'w') as f:
        while page <= max_page:
            args.update(page=page)
            req = ProductsRequest(FOLDER_NAME, f, **args)
            if not req.send(selenium):
                print('ERROR!')
                break

            count_all_results = req.processing()
            if count_all_results > 0:
                max_page = count_all_results // 48 + 1 if count_all_results // 48 + 1 <= 7 else 7
            page += 1

    selenium.close()
    if '-v' in sys.argv:
        print('Products loading done. Now you need to start another script: `reviews_collect.py`')
except Exception as e:
    print('An error was occurred.')
    if '-v' in sys.argv:
        raise e
