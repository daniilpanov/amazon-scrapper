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

    async getASINsLInks() {
        const pagination = document.getElementsByClassName('a-pagination');
        let links_a, old_links_a_count = 0, res = [];
        if (pagination && pagination.length) {
            pagination[0].scrollIntoView();
            await new Promise(r => setTimeout(r, 2000));
        } else {
            links_a = document.querySelectorAll('div.a-cardui[id*="asin-index"]');
            while (old_links_a_count < links_a.length) {
                links_a[links_a.length - 1].scrollIntoView();
                old_links_a_count = links_a.length;
                await new Promise(r => setTimeout(r, 1000));
                links_a = document.querySelectorAll('div.a-cardui[id*="asin-index"]');
            }
        }
        links_a = document.querySelectorAll('div.a-cardui[id*="asin-index"]');
        let i = 0, link;
        for (link of links_a) {
            if (i >= this.count) {
                break;
            }

            const reviews_info = link.querySelector('a[href*="product-reviews"]')?.innerText.replaceAll('\u2009', '\n').split('\n');
            if (!reviews_info) {
                if (this.limit) {
                    continue
                }
            } else {
                const reviews_count = reviews_info.length < 2 ? 0 : Number(reviews_info[reviews_info.length - 1].trim().replaceAll(',', '').replaceAll(' ', ''));
                if (this.limit && reviews_count < 700 || this.target && link.querySelector('a')?.href.includes(this.target)) {
                    continue;
                }
            }
            const asin = link.querySelector('a')?.href.match(/B0[0-9A-Z]{8}/g)
            if (asin && asin.length) {
                ++i;
                res.push(asin[0]);
            }
        }
        if (this.target && !(this.target in res)) {
            res.push(this.target);
        }
        /*if (i < this.count) {
            const new_page = pagination.querySelector('.a-last:not(.a-disabled) > a');
            if (new_page) {
                new_page.click();
                await new Promise(r => setTimeout(r, 2000));
                res = [...res, await this.getASINsLInks()];
            }
        }*/
        return res;
    }
}