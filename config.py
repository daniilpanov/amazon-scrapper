# -*- coding: utf-8 -*-
import datetime
import logging
import os

import dotenv

dotenv.load_dotenv()

WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH')
MAX_RETRIES = os.environ.get('MAX_RETRIES')
IGNORED_CHAR = os.environ.get('IGNORED_CHAR') or '[✎【】★❤️🎧💕♥🌈🎸🍀【✅✔\U0001f43b]'
FOLDER_NAME = os.environ.get('DIRECTORY_OUTPUT') or datetime.datetime.now().strftime('%Y-%m-%d')
HEADLESS = os.environ.get('HEADLESS') == 'true'

if not os.path.exists('./' + FOLDER_NAME):
    os.makedirs(FOLDER_NAME)

logging.basicConfig(filename=os.path.join(FOLDER_NAME, 'collect.log'),
                    format='%(levelname)s: %(asctime)s: %(message)s',
                    level=logging.INFO)


def get_file(filename):
    if os.path.exists(os.path.join(FOLDER_NAME, filename)):
        return 'a'
    return 'w'


def p(): return get_file('products.csv')
def r(): return get_file('reviews.csv')
def j(): return get_file('data.json')


def state(**kwargs) -> dict:
    """
    param str products_page: Link to the products' page of the current search.
    param str product_url: The link to current product
    param str reviews_page: The link to reviews page of current product
    param bool current_state: When it's True, after restart script click 'next' without collecting reviews
                              It helps eliminate duplicates.
    param int rate: This is the filter parameter. We have to use a filter because there is a visibility limit
                    500 review pages. When we use this filter, this limit only applies to the selected reviews rating.
                    So, for example, any product has 6_443 reviews. We can't get all reviews because of limit,
                    but we can get all 5-star reviews, then 4-star, then 3-, 2- and 1-star reviews. So in every case
                    we'll get less than 5k reviews, but the total number of reviews exceeds 5k.
    :rtype: dict All config
    """
    statefile = kwargs.get('filename', False)
    path = os.path.join(FOLDER_NAME, statefile or 'state.dat')
    new_data = dict()
    data = dict()

    if os.path.exists(path):
        f = open(path)
        for row in f.readlines():
            row = row.strip().split('=')
            data[row[0]] = new_data[row[0]] = '='.join(row[1:])
        f.close()
    else:
        open(path, 'w').close()
        if not statefile:
            return state(products_page='', product_url='', reviews_page='', current_state=0, rating=6, filtered=0)
        else:
            return dict()

    for key in kwargs:
        if key != 'filename':
            new_data[key] = kwargs.get(key)

    if new_data != data:
        f = open(path, 'w')
        f.writelines(map(lambda x: x + '=' + str(new_data[x]) + '\n', new_data))
        f.close()

    return data


state()
