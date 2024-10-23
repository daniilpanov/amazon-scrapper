class ProductsParser extends Parser {
    domparser = new DOMParser();
    currentBreadcrumbElement = null;
    breadcrumbsElements = [];
    ASIN = null;
    title = null;
    marketplaceId = null;
    mediaConfig = null;
    relatedVideos = null;

    constructor(funcs, doc, asin) {
        super(funcs, doc);
        this.ASIN = asin;
    }


    getBreadcrumbsCurrentElement() {
        return this.currentBreadcrumbElement || (
            this.currentBreadcrumbElement = this.root.getElementById('wayfinding-breadcrumbs_feature_div')
                ?.querySelector('li:last-child') || null
        );
    }

    getBreadcrumbsElements() {
        return (this.breadcrumbsElements && this.breadcrumbsElements.length) ? this.breadcrumbsElements : (
            this.breadcrumbsElements = this.root.getElementById('wayfinding-breadcrumbs_feature_div')
                ?.querySelectorAll('li:not(.a-breadcrumb-divider)') || []
        );
    }

    getBreadcrumbs() {
        return { breadcrumbs: [...this.getBreadcrumbsElements()].map(el => el.textContent.trim()) };
    }

    getCurrentBreadcrumb() {
        return { currentBreadcrumb: this.getBreadcrumbsCurrentElement()?.textContent.trim() || null };
    }

    getASIN() {
        return { asin: this.ASIN };
    }

    getTitle() {
        return { title: this.title || (
            this.title = this.getElementByIds([
                'productTitle',
                'title',
                'titleSection',
                'title_feature_div'
            ])?.textContent || false
        )};
    }

    getMarketplaceId() {
        return { marketplaceId: (this.marketplaceId || (
            this.marketplaceId = this.root.querySelector(
                '[data-marketplace]'
            )?.getAttribute('data-marketplace') || null
        )) };
    }

    requestRelatedVideos() {
        let requestBody = {
            "pageContext": {
                "page": "DetailPage",
                "placement": "ImageBlock",
                "device": "Desktop",
                "marketplaceID": this.getMarketplaceId(),
                "locale": "en_US",
                "product": {
                    "contentID": this.getASIN(),
                    "contentIDType": "ASIN",
                    "parentContentID": this.getFullMediaConfig()?.parentAsin,
                    "parentContentIDType": "ASIN",
                },
                "weblabContext": [
                    {
                        "name": "",
                        "assignment": "",
                        "ignoreForG2S2Key": true
                    }
                ],
                "metadata": {
                    "ProductTitle": this.getTitle(),
                }
            },
            "configuration": {
                "id": "div-relatedvideos",
                "type": "relatedvideos",
                "binder": "relatedvideos",
                "loader": "lazyload",
                "features": {
                    "features": {
                        "verticalcarousel": "true",
                        "hide_default_buttons": "true",
                        "first_item_flush_left": "true",
                        "pagestate": "dp_vse_rvc",
                        "reftagprefix": "dp_vse_ibvc",
                        "carouselName": "vse-ib-rvs",
                        "count": "16",
                        "useLazyLoad": "false",
                        "hidePlayIcon": "true",
                        "hideCustomerReviewPrefix": "true",
                        "cssClass": "vse-hide-carousel-title",
                        "segmentOneHeaderId": "vse_ib_segment_one",
                        "segmentTwoHeaderId": "ive_related_videos_for_this_product",
                        "segmentThreeHeaderId": "vse_ib_segment_three",
                        "segmentOneHeaderDefault": "Videos for this product",
                        "segmentTwoHeaderDefault": "Related videos for this product",
                        "segmentThreeHeaderDefault": "Customer review videos",
                        "includeProfiles": "true",
                        "showCustomerReviewMetadata": "true",
                        "enableCustomerReviewVideos": "true"
                    }
                },
                "sources": {
                    "source": "VideoAdsDataAggregatorService"
                }
            }
        };

        return fetch('https://www.amazon.com/vap/ew/subcomponent/relatedvideos', {
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
            method: 'POST',
        });
    }

    async getRelatedVideos() {
        if (this.relatedVideos) {
            return { relatedVideos: this.relatedVideos };
        }
        const result = await this.requestRelatedVideos();
        const parsedResHTML = this.domparser.parseFromString(result, 'text/html');
        const links = [...(parsedResHTML.querySelectorAll('[data-video-url]') || [])]
            .map(el => el.getAttribute('data-video-url'));
        return { relatedVideos: (this.relatedVideos = links) };
    }

    getFullMediaConfig() {
        if (this.mediaConfig) {
            return this.mediaConfig;
        }
        const allScripts = this.root.getElementsByTagName('script');
        let needleScript = null;
        for (const script of allScripts) {
            const scriptContent = script.textContent.trim();
            if (scriptContent.slice(0, 200).includes('twister-js-init-dpx-data')) {
                needleScript = scriptContent;
                break;
            }
        }
        if (!needleScript) {
            return { mediaConfig: null };
        }
        const lines = needleScript.split('\n');
        let start = false, needleContent = '';
        for (let item of lines) {
            item = item.trim();
            if (!start && item === 'var dataToReturn = {') {
                start = true;
                needleContent += '{';
            } else if (start && item) {
                if (item === 'return dataToReturn;') {
                    break;
                }
                needleContent += item;
            }
        }
        needleContent = needleContent.slice(0, needleContent.length - 1)
            .replaceAll(',}', '}')
            .replaceAll(',]', ']');
        try {
            return { mediaConfig: (this.mediaConfig = JSON.parse(needleContent)) };
        } catch (e) {
            return { mediaConfig: null };
        }
    }

    getDescription() {
        const el = this.getElementByIds([
            'feature-bullets',
            'featurebullets_feature_div',
            'productFactsDesktop_feature_div',
        ]) || this.root.querySelector('div[aria-expanded]');
        if (!el) {
            return { description: null };
        }
        const items = el.querySelectorAll('ul > li');
        if (items && items.length) {
            let res = '';
            for (const item of items) {
                res += '\n' + item.textContent.trim();
            }
            return { description: res.trim() };
        }
        return { description: el.textContent.replaceAll(/ {2,}/gm, ' ').trim() }
    }

    getPrice() {
        const priceEl = this.root.querySelector('#corePriceDisplay_desktop_feature_div > div');
        if (!priceEl) {
            return { price: null };
        }
        const wholeEl = priceEl.querySelector('.a-price .a-price-whole');
        const fractionEl = priceEl.querySelector('.a-price .a-price-fraction');
        if (!wholeEl) {
            return { price: null };
        }
        const whole = Number.parseFloat(wholeEl.textContent.trim());
        if (Number.isNaN(whole)) {
            return { price: null };
        } else if (!fractionEl) {
            return { price: whole };
        }
        const fraction = Number.parseInt(fractionEl.textContent.trim());
        if (Number.isNaN(fraction)) {
            return { price: null };
        }
        const price = whole + (fraction / 100);
        return { price };
    }

    getReviewsRating() {

    }

    getReviewsCount() {

    }

    getOptions() {
        // TODO
    }

    getDetails() {
        // TODO
    }

    getTechnicalDetails() {
        // TODO
    }

    getAdditionalInfo() {
        // TODO
    }

    getAspects() {
        // TODO
    }

    getReviewsImages() {
        // TODO
    }

    getTopReviews() {
        // TODO
    }

    clickAllReviews() {
        // TODO
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
        res.description = this.root.querySelector(['#feature-bullets, #productFactsDesktop_feature_div div[aria-expanded]'])?.textContent.trim();

        return res;
    }
}
