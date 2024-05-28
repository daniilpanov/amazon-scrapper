import time

import requests


def get_html_by_request(asin, full_link=None, domain='amazon.com'):

    for i in range(5):
        r = requests.get(full_link or 'https://www.' + domain + '/dp/' + asin)

        time.sleep(5)
