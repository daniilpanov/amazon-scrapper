import re

from bs4 import BeautifulSoup
from orjson import orjson, JSONDecodeError

import parser


def process_req1(asin, response, domain, q):
    try:
        process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', response.strip())
        try:
            raw = []
            for s in [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()]:
                try:
                    raw.append(orjson.loads(s.strip()))
                except JSONDecodeError:
                    pass
        except Exception as e:
            print(e)
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
        if not res:
            print(process_data_res)
        q.put(res)
        return bool(res) - (not bool(res))
    except Exception as ex:
        print(ex)
        return False


def process_req2(asin, response, domain, q):
    soup = BeautifulSoup(response, features='lxml')
    if soup.find(attrs={'id': 'authportal-center-section'}) or soup.select('body > div > div[style*="width: 350px"]'):
        return None
    reviews = soup.find_all('div', {'data-hook': 'review'})
    res = []
    for review in reviews:
        res.append(parser.parse_reviews(asin, review, domain))
    if res:
        q.put(res)
    return bool(res) - (not bool(res))
