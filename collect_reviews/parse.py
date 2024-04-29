import json
import re

from bs4 import BeautifulSoup

import parser
from .logger import logger
from .write import write


def count_reviews(html):
    soup = BeautifulSoup(html, features='lxml')
    reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
    reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
    if len(reviews_count_part) == 2:
        return int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
    return 0


def process_data(asin, seed, process_data_res, domain):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', process_data_res.strip())
        try:
            raw = []
            for s in [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()]:
                try:
                    raw.append(json.loads(s.strip()))
                except json.JSONDecodeError:
                    pass
        except Exception:
            logger('parse.process_data').exception()
            return False
        data_with_quantity = None
        for item in raw:
            if len(item) >= 3 and item[1] == '#filter-info-section':
                data_with_quantity = item[2]
                break
        if not data_with_quantity:
            return False

        res = []

        for item in raw:
            if len(item) < 3 or item[1] != "#cm_cr-review_list" or not item[2].strip():
                continue
            item_parser = BeautifulSoup(item[2].strip(), features='lxml')
            if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
                    or item_parser.find('div', class_='a-divider-section') \
                    or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                continue
            res.append(parser.parse_reviews(asin, item[2].strip(), domain))
        if res:
            write(res)
        return bool(res) - (not bool(res))
    except Exception:
        logger('parse.process_data').exception()
        return False


def process_data_from_page(asin, seed, process_data_res, domain):
    soup = BeautifulSoup(process_data_res, features='lxml')
    reviews = soup.find_all('div', {'data-hook': 'review'})
    res = []
    for review in reviews:
        res.append(parser.parse_reviews(asin, review, domain))
    write(res)
    return bool(res) - (not bool(res))
