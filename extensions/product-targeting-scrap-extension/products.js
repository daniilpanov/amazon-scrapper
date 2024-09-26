class CollectProducts {
    asin;
    domain;

    constructor(asin, domain = 'amazon.com') {
        this.asin = asin;
        this.domain = domain;
    }

    getElementByIds(ids) {
        let r;
        for (const el_id of ids) {
            r = document.getElementById(el_id);
            if (r) {
                return r;
            }
        }
        return null;
    }

    getBreadcrumbs() {
        return document.getElementById('wayfinding-breadcrumbs_feature_div')
            ?.querySelector('li:last-child')?.textContent.trim() || null;
    }

    getProductCard() {
        let res = {
            title: null,
            description: null,
        };

        // Title & description
        res.title = this.getElementByIds(['titleSection', 'title', 'productTitle'])?.textContent.trim();
        if (!res.title) {
            throw new Error('Invalid page');
        }
        res.description = document.querySelector(['#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]'])?.textContent.trim();

        return res;
    }
}
