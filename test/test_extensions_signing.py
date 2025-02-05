import os
import unittest
from urllib.parse import quote

import requests

from . import config

unittest.TestLoader.sortTestMethodsUsing = None


class TestExtSign(unittest.TestCase):
    def test_chrome_resigning(self):
        print(requests.post('http://0.0.0.0:8091/ext/resign/chrome'))

    def test_chrome_getting_updates(self):
        print(requests.get('http://0.0.0.0:8091/ext/update/d798b6a94abcd3bdcc5705eda2fbc711.xml').text)

    def test_chrome_getting_crx(self):
        print(len(requests.get('http://0.0.0.0:8091/ext/update/100asins-scrap-extension.crx').content))
