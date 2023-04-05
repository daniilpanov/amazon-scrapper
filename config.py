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
                    level=logging.WARNING)


def get_file(filename):
    if os.path.exists(os.path.join(FOLDER_NAME, filename)):
        return 'a'
    return 'w'


def p(): return get_file('products.csv')
def r(): return get_file('reviews.csv')
def j(): return get_file('data.json')


defaultstate = None


def state(products_page=None, product_url=None, reviews_page=None, current_state=None):
    """
    :param str products_page: The link to products page of current search request
    :param str product_url: The link to current product
    :param str reviews_page: The link to reviews page of current product
    :param bool current_state: When it's True, after restart script press 'next' button without collecting reviews
                               It helps exclude duplicates
    :return dict: All config
    """
    global defaultstate
    path = os.path.join(FOLDER_NAME, 'state.dat')
    data = dict()

    if os.path.exists(path):
        f = open(path)
        for row in f.readlines():
            row = row.strip().split('=')
            data[row[0]] = '='.join(row[1:])
        f.close()

        if products_page is not None:
            data['products_page'] = products_page
        if product_url is not None:
            data['product_url'] = product_url
        if reviews_page is not None:
            data['reviews_page'] = reviews_page
        if current_state is not None:
            data['current_state'] = int(current_state)
    else:
        open(path, 'w').close()
        return state('', '', '', False)

    if products_page is not None or product_url is not None or reviews_page is not None or current_state is not None:
        f = open(path, 'w')
        f.writelines(map(lambda x: x + '=' + str(data[x]) + '\n', data))
        f.close()

    defaultstate = data
    return data


state()
