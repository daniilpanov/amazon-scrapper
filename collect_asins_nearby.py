import requests
from bs4 import BeautifulSoup

from functions import base_chrome_init
from helpers import get_all_asins_from_text, parse_args


def get_asins(url, wd):
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
        if reviews_count < 700:
            continue
        i += 1
        yield 'https://amazon.com/dp/' + get_all_asins_from_text(link.find('a')['href'])


def get_bsr(asin, wd):
    asins = get_all_asins_from_text(asin)
    if not asins:
        return asin
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
    print(sys.argv)
    params_dict = parse_args(sys.argv)
    print(params_dict)
    try:
        wd = base_chrome_init('https://amazon.com')
        wd.change_loc()
        # get department url
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
            'msg': f'Error on collecting nearby asins: {params_dict["asin"]}\n' + str(e) + '\n',
            'uid': params_dict['user'],
        })
    finally:
        requests.post('http://localhost:8080/end_task', {'_id': params_dict['_id']})
