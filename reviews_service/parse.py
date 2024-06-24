import re
from queue import Queue

import requests
from bs4 import BeautifulSoup
from orjson import orjson, JSONDecodeError

import parser


class UnknownParseError(Exception):
    pass


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
            raise UnknownParseError
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

            json_data = parser.parse_reviews(asin, item[2].strip(), domain)
            json_data['date'] = json_data['date'].isoformat()
            json_data['scrap_datetime'] = json_data['scrap_datetime'].isoformat()
            res.append(json_data)
        if not res:
            print(process_data_res)
        q.put(res)
        return bool(res)
    except Exception as ex:
        print(ex)
        raise UnknownParseError


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


def write_data(q: Queue):
    data = -1
    try:
        while data is not None:
            data = q.get()
            requests.post('http://localhost:8832/products/set_result/reviews', json=data)
    except KeyboardInterrupt:
        while not q.empty() and data is not None:
            data = q.get()
            requests.post('http://localhost:8832/products/set_result/reviews', json=data)
        raise
