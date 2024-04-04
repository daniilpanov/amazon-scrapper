import asyncio

from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException

import amazon_requests
import tasks
from helpers import get_all_asins_from_text


async def get_asins(url, sess, excluded=None, limit=True, domain='amazon.com', unique_brands=False, count=5):
    await sess.init()

    html = await sess.get_html(url, abs_path=True)
    while not html:
        await asyncio.sleep(0)
        await sess.init()
        html = await sess.get_html(url, abs_path=True)
    soup = BeautifulSoup(html, features='lxml')
    links_a = soup.select('div.a-cardui[id*="asin-index"]')
    brands = set()
    i = 0
    for link in links_a:
        if i >= count:
            break
        reviews_lnk = link.select_one('a[href*="product-reviews"]')
        reviews_info = reviews_lnk.text.replace('\u2009', '\n').split('\n')
        reviews_count = int(reviews_info[1].strip().replace(',', '').replace(' ', ''))
        if limit and reviews_count < 700 or excluded and excluded in link.find('a')['href']:
            continue
        asin = get_all_asins_from_text(link.find('a')['href'])[0]
        if unique_brands:
            soup = BeautifulSoup(await sess.get_html('dp/' + asin), features='lxml')
            try:
                brand = soup.select_one('tr.po-brand').find_all('td')[-1].text
                if brand in brands:
                    continue
                brands.add(brand)
            except Exception as e:
                print(e)
        i += 1
        yield f'https://{domain}/dp/' + asin, asin


async def get_bsr(asin, sess, domain):
    asins = get_all_asins_from_text(asin)
    if not asins:
        return asin
    asin = asins[0]

    await sess.init()
    soup = BeautifulSoup(await sess.get_html(f'dp/{asin}'), features='lxml')
    try:
        el = soup.select_one('[data-feature-name="detailBullets"]')
        details = el.find_all(attrs={'class': 'detail-bullet-list'})
        get_bsrs = lambda detail: detail.find_all('ul')
    except NoSuchElementException:
        el = soup.get_element('#prodDetails')
        details = el.select('[id*="productDetails_detailBullets"] tr')
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


async def collect_nearby(_id, asin_bsr, limit=True, unique_brands=False, count=5, domain='amazon.com'):
    sess = amazon_requests.Requests(domain)
    # get department url
    url = await get_bsr(asin_bsr, sess, domain)
    # search asins
    asins_generator = get_asins(url, sess, asin_bsr, limit, domain, unique_brands, count)
    result = []
    async for item in asins_generator:
        result.append(item)
    task = tasks.get_task(_id)
    task.progress = 100
    task.success = True
    task.result = {
        'bsr_url': url,
        'asins': list(map(lambda x: x[1], result)),
        'links': list(map(lambda x: x[0], result)),
    }

