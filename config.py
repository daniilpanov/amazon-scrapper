import datetime
import logging
import os

WEBDRIVER_PATH = '../chromedriver/chromedriver.exe'
MAX_RETRIES = 10
IGNORED_CHAR = '[✎【】★❤️🎧💕♥🌈🎸🍀【✅✔]'

FOLDER_NAME = datetime.datetime.now().strftime('%Y-%m-%d')
if not os.path.exists('./' + FOLDER_NAME):
    os.makedirs(FOLDER_NAME)

logging.basicConfig(filename=os.path.join(FOLDER_NAME, 'log.txt'),
                    format='%(levelname)s: %(asctime)s: %(message)s',
                    level=logging.DEBUG)


def get_file(filename):
    if os.path.exists(os.path.join(FOLDER_NAME, filename)):
        return 'a'
    return 'w'


p = get_file('products.csv')
r = get_file('reviews.csv')
j = get_file('data.json')
