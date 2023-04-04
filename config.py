# -*- coding: utf-8 -*-
import datetime
import logging
import os

import dotenv

dotenv.load_dotenv()

WEBDRIVER_PATH = os.environ.get('WEBDRIVER_PATH')
MAX_RETRIES = os.environ.get('MAX_RETRIES')
IGNORED_CHAR = os.environ.get('IGNORED_CHAR') or '[✎【】★❤️🎧💕♥🌈🎸🍀【✅✔\U0001f43b]'
FOLDER_NAME = input('Please, input the folder name: ') or datetime.datetime.now().strftime('%Y-%m-%d')

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


def state(products_page=None, product_url=None, reviews_page=None):
    global defaultstate
    path = os.path.join(FOLDER_NAME, 'state.dat')
    data = dict()
    if os.path.exists(path):
        f = open(path)
        for row in f.readlines():
            row = row.strip().split('=')
            data[row[0]] = row[1]
        f.close()

        if products_page is not None:
            data['products_page'] = products_page
        if product_url is not None:
            data['product_url'] = product_url
        if reviews_page is not None:
            data['reviews_page'] = reviews_page
    else:
        open(path, 'w').close()
        return state(1, '', 1)

    if products_page is not None or product_url is not None or reviews_page is not None:
        f = open(path, 'w')
        f.writelines(map(lambda x: x + '=' + str(data[x]) + '\n', data))
        f.close()

    defaultstate = data
    return data


state()
