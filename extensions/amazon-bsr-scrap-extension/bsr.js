class CollectBSR {
    limit;
    count;
    target;
    unique_brands;
    domain;

    constructor(limit, count, target, unique_brands, domain = 'amazon.com') {
        this.limit = limit;
        this.count = count;
        this.target = target;
        this.unique_brands = unique_brands;
        this.domain = domain;
    }

    getBSRURL(asin) {
        // TODO: rewrite
        /*try:
        el = soup.select_one('[data-feature-name="detailBullets"]')
        details = el.find_all(attrs={'class': 'detail-bullet-list'})
        get_bsrs = lambda detail: detail.find_all('ul')
        except NoSuchElementException:
            el = soup.get_element('#prodDetails')
        details = el.select('[id*="productDetails_detailBullets"] tr')
        get_bsrs = lambda detail: detail.select('td > span > span')

        for det in details:
        if ev and ev.is_set():
        break
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
        return url*/
    }

    getASINsLInks() {
        const links_a = document.querySelectorAll('div.a-cardui[id*="asin-index"]'), res = [];
        let i = 0, link;
        for (link of links_a) {
            if (i >= this.count) {
                break;
            }

            const reviews_info = link.querySelector('a[href*="product-reviews"]')?.innerText.replaceAll('\u2009', '\n').split('\n');
            const reviews_count = reviews_info.length < 2 ? 0 : Number(reviews_info[1].trim().replaceAll(',', '').replaceAll(' ', ''));
            if (this.limit && reviews_count < 700 || this.target && link.querySelector('a')?.href.includes(this.target)) {
                continue;
            }
            const asin = link.querySelector('a')?.href.match(/B0[0-9A-Z]{8}/g)
            if (asin) {
                i += 1
            }
            res.push(asin);
        }
        return res;
    }
}