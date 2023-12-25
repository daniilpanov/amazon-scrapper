from time import sleep

import requests
from bs4 import BeautifulSoup

from functions import base_chrome_init
from helpers import get_all_asins_from_text, parse_args


def get_asins(url, wd):
    wd.get(url)
    soup = BeautifulSoup(wd.get_page_source(), features='html.parser')
    links_a = soup.select('div.a-cardui[id*="asin-index"]')
    for link in links_a:
        reviews_lnk = link.select_one('a[href*="product-reviews"]')
        print(reviews_lnk.text)
        reviews_info = reviews_lnk.text.replace('\u2009', '\n').split('\n')
        print(reviews_info)
        reviews_count = int(reviews_info[1].strip().replace(',', '').replace(' ', ''))
        if reviews_count < 700:
            continue
        url = link.find('a')['href']
        if not url.startswith('https://'):
            url = 'https://amazon.com' + url
        yield url


def get_bsr(asin, wd):
    asins = get_all_asins_from_text(asin)
    if not asins:
        return False
    asin = asins[0]

    wd.get(f'https://amazon.com/dp/{asin}')
    el = wd.get_element('[data-feature-name="detailBullets"]')
    soup = BeautifulSoup(el.get_attribute('innerHTML'), features='html.parser')
    details = soup.find_all(attrs={'class': 'detail-bullet-list'})
    for det in details:
        if 'Best Sellers Rank' in det.text:
            bsrs = det.find_all('ul')
            min_place = None
            lnk = None

            for bsr in bsrs:
                a_bsr = bsr.text
                parts = a_bsr.strip()[1:].split(' in ')
                if len(parts) != 2:
                    continue
                num, bsr_cat = parts
                num = int(num.replace(',', ''))
                if min_place is None or num < min_place:
                    min_place = num
                    lnk = bsr.find('a')
            url = lnk['href']
            if not url.startswith('https://'):
                url = 'https://amazon.com' + url
            return url


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)
    try:
        wd = base_chrome_init(False, 'https://amazon.com')
        wd.change_loc()
        # get department url
        params_dict.setdefault('asin', 'B0725YPBPR')
        url = get_bsr(params_dict['asin'], wd)
        requests.post('http://localhost:8080/send_msg', {
            'msg': f'BSR URL: {url}\n(for [{params_dict["asin"]}])',
            'uid': params_dict.get('user', '1456674317,1428909514'),
        })
        # search asins
        result = list(get_asins(url, wd))
        requests.post('http://localhost:8080/send_msg', {
            'msg': f'BSR products (for [{params_dict["asin"]}]):\n' + '\n'.join(result),
            'uid': params_dict.get('user', '1456674317,1428909514'),
        })
    except Exception as e:
        requests.post('http://localhost:8080/send_msg', {
            'msg': f'Error on collecting nearby asins: {params_dict.get("sheet_name")}\n' + str(e) + '\n',
            'uid': params_dict['user'],
        })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
