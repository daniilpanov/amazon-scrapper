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


def get_file_write_mode(filename):
    if os.path.exists(os.path.join(FOLDER_NAME, filename)):
        return 'a'
    return 'w'


class State:
    def __init__(self, filename, default_data=None):
        self.filename = filename
        self.data = default_data
        if not os.path.exists(filename):
            self.write()
        else:
            self.update()

    def update(self):
        with open(self.filename, 'r', encoding='utf-8') as state_file:
            for row in state_file.readlines():
                row = row.strip()
                if not row:
                    continue
                row = row.split('=')
                self.data[row[0]] = '='.join(row[1:]) if len(row) > 1 else ''
        self.write()

    def write(self):
        with open(self.filename, 'w') as state_file:
            if self.data:
                for keyval in self.data.items():
                    state_file.write('='.join(keyval))

    def has_data(self):
        return bool(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item] if item in self.data else None

