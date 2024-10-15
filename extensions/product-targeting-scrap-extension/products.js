class CollectProductInfo {
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

    getBreadcrumbsCurrentElement() {
        return document.getElementById('wayfinding-breadcrumbs_feature_div')
            ?.querySelector('li:last-child')?.textContent.trim() || null;
    }

    getBreadcrumbs() {
        return document.getElementById('wayfinding-breadcrumbs_feature_div')
            ?.querySelectorAll('li:not(.a-breadcrumb-divider)') || [];
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
