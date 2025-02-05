import requests
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException

from functions import base_chrome_init
from helpers import get_all_asins_from_text
from args_parser import parse_args


def get_asins(url, wd, excluded=None, limit=True, domain='amazon.com', unique_brands=False, to_links=True):
    wd.get(url)
    soup = BeautifulSoup(wd.get_page_source(), features='html.parser')
    links_a = soup.select('div.a-cardui[id*="asin-index"]')
    i = 0
    for link in links_a:
        if i >= 5:
            break
        reviews_lnk = link.select_one('a[href*="product-reviews"]')
        reviews_info = reviews_lnk.text.replace('\u2009', '\n').split('\n')
        reviews_count = int(reviews_info[1].strip().replace(',', '').replace(' ', ''))
        if limit and reviews_count < 700 or excluded and excluded in link.find('a')['href']:
            continue
        i += 1
        yield (f'https://{domain}/dp/' if to_links else '') + get_all_asins_from_text(link.find('a')['href'])[0]


def get_bsr(asin, wd, domain):
    asins = get_all_asins_from_text(asin)
    if not asins:
        return asin
    asin = asins[0]

    wd.get(f'https://{domain}/dp/{asin}')
    try:
        el = wd.get_element('[data-feature-name="detailBullets"]')
        soup = BeautifulSoup(el.get_attribute('innerHTML'), features='html.parser')
        details = soup.find_all(attrs={'class': 'detail-bullet-list'})
        get_bsrs = lambda detail: detail.find_all('ul')
    except NoSuchElementException:
        el = wd.get_element('#prodDetails')
        soup = BeautifulSoup(el.get_attribute('innerHTML'), features='html.parser')
        details = soup.select('[id*="productDetails_detailBullets"] tr')
        get_bsrs = lambda detail: detail.select('td > span > span')

    for det in details:
        if 'Best Sellers Rank' in det.text:
            bsrs = get_bsrs(det)
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
            if not lnk:
                continue
            url = lnk['href']
            if not url.startswith('https://'):
                url = f'https://{domain}' + url
            return url


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)
    params_dict.setdefault('domain', 'amazon.com')
    try:
        wd = base_chrome_init(f'https://{params_dict["domain"]}')
        wd.change_loc(domain=params_dict['domain'])
        # get department url
        url = get_bsr(params_dict['asin'], wd, params_dict['domain'])
        # search asins
        result = list(get_asins(url, wd, params_dict['asin'], params_dict.get('limit', True), params_dict['domain']))
        if 'user' in params_dict:
            requests.post('http://localhost:8080/send_msg', {
                'msg': f'BSR URL: {url}\n(for [{params_dict["asin"]}])',
                'uid': params_dict['user'],
            })
            requests.post('http://localhost:8080/send_msg', {
                'msg': f'BSR products (for [{params_dict["asin"]}]):\n' + '\n'.join(result),
                'uid': params_dict['user'],
            })
    except Exception as e:
        if 'user' in params_dict:
            requests.post('http://localhost:8080/send_msg', {
                'msg': f'Error on collecting nearby asins: {params_dict["asin"]}\n' + str(e) + '\n',
                'uid': params_dict['user'],
            })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
