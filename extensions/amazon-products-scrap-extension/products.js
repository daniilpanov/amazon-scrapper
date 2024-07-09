class CollectProducts {
    asin;
    domain;

    constructor(asin, domain='amazon.com') {
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

    getProductCard(collect_media_config) {
        let res = {
            asin: this.asin,
            product_url: `https://${this.domain}/dp/${this.asin}`,
            canonical_prefix: null,
            product_title: null,
            product_descr: null,
            picture_url: null,
            features: {},
            top_5_phrases: [],
            product_price: null,
        };

        // Canonical prefix
        res.canonical_prefix = document.querySelector('link[rel="canonical"]')?.href.split('amazon.com')[1]?.split('/')[1];

        // Title & description
        res.product_title = this.getElementByIds(['titleSection', 'title', 'productTitle'])?.innerText;
        if (!res.product_title) {
            throw new Error('Invalid page');
        }
        res.product_descr = document.querySelector(['#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]'])?.innerText;

        res.picture_url = document.getElementById('landingImage')?.src;

        // features
        const features_els = document.querySelectorAll(
            '[data-hook="cr-widget-SummaryAttribute"] #cr-summarization-attributes-list > div',
        );
        let key, val;
        for (const feat of features_els) {
            key = feat.querySelector('div > div > div:first-child span')?.innerText.trim();
            val = feat.querySelector('div > div > div:last-child > span:last-child')?.innerText.trim();
            if (key && val) {
                res.features[key] = val;
            }
        }
        // top 5 phrases
        const top5_els = document.querySelectorAll('[data-hook="lighthut-terms-list"] > div').values().toArray();
        let counter = 0;
        for (const lighthum of top5_els) {
            val = lighthum.querySelector('span')?.innerText.trim();
            if (val) {
                res.top_5_phrases.push(val);
                ++counter;
                if (counter >= 5) {
                    break;
                }
            }
        }

        // Product price
        res.product_price = document.querySelector('.a-price')?.innerText.split('$')[1]?.trim().replaceAll(',', '');
        if (res.product_price) {
            res.product_price = Number(res.product_price);
        }

        // Media config
        if (collect_media_config) {
            res['media_data'] = this.getMediaConfig();
        }

        return res;
    }

    getAspects() {
        const root_div = document.querySelector('[data-csa-c-slot-id="cr-product-insights-cards-popover"]');
        if (!root_div) {
            return null;
        }
        const aspects_names_els = document.getElementById('aspect-button-group-0')?.querySelectorAll('[id*=aspect-button]');
        const res = [];
        let positive, negative, raw_stat;
        for (let i = 0; i < Math.min(root_div.children.length, aspects_names_els.length); ++i) {
            raw_stat = root_div.children[i].querySelectorAll('div span');
            positive = raw_stat[1].innerText.replaceAll(',', '').split(' ');
            for (const item of positive) {
                if (Number.isNaN(Number(item))) {
                    continue;
                }
                positive = Number(item);
            }
            if (Number.isNaN(Number(positive))) {
                continue;
            }
            negative = raw_stat[2].innerText.replaceAll(',', '').split(' ');
            for (const item of negative) {
                if (Number.isNaN(Number(item))) {
                    continue;
                }
                negative = Number(item);
            }
            if (Number.isNaN(Number(negative))) {
                continue;
            }
            res.push({Aspect: aspects_names_els[i].innerText.trim(), positive: positive, negative: negative});
        }
        return res;
    }

    getMediaConfig() {
        const root_js = document.querySelector('div#imageBlockVariations_feature_div script')?.innerText;
        if (!root_js) {
            return null;
        }

        let data_json = root_js.match(/var obj = jQuery.parseJSON\('(.+)'\)/);
        if (!data_json || !data_json.length) {
            return null;
        }
        data_json = data_json[1].replaceAll('\n', '').replaceAll('\\', '');
        try {
            return JSON.parse(data_json);
        } catch (e) {
            return null;
        }
    }
}
