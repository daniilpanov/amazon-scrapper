class ProductsParser extends Parser {
    domparser = new DOMParser();
    currentBreadcrumbElement = null;
    breadcrumbsElements = [];
    ASIN = null;
    rootASIN = null;
    title = null;
    marketplaceId = null;
    mediaConfig = null;
    relatedVideos = null;
    aspects = null;
    requestID = null;

    constructor({ funcs, doc, asin }) {
        super({ funcs, doc });
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
        const { mediaConfig } = this.getFullMediaConfig();
        return { asin: mediaConfig.currentAsin || this.ASIN || null, rootAsin: (this.rootASIN || (this.rootASIN = mediaConfig.parentAsin || null)) };
    }

    getTitle() {
        return {
            title: this.title || (
                this.title = this.getElementByIds([
                    'productTitle',
                    'title',
                    'titleSection',
                    'title_feature_div',
                ])?.textContent.trim() || false
            ),
        };
    }

    getMarketplaceId() {
        return {
            marketplaceId: (this.marketplaceId || (
                this.marketplaceId = this.root.querySelector(
                    '[data-marketplace]',
                )?.getAttribute('data-marketplace') || null
            )),
        };
    }

    getMainImage() {
        const imageEl = this.root.querySelector('#main-image-container ul img');
        return { picture_url: (imageEl?.src || null) };
    }

    requestRelatedVideos() {
        let requestBody = {
            'pageContext': {
                'page': 'DetailPage',
                'placement': 'ImageBlock',
                'device': 'Desktop',
                'marketplaceID': this.getMarketplaceId()?.marketplaceId,
                'locale': 'en_US',
                'product': {
                    'contentID': this.getASIN()?.asin,
                    'contentIDType': 'ASIN',
                    'parentContentID': this.getASIN()?.rootAsin,
                    'parentContentIDType': 'ASIN',
                },
                'requestId': this.getRequestID()?.requestID,
                'weblabContext': [
                    {
                        'name': '',
                        'assignment': '',
                        'ignoreForG2S2Key': true,
                    },
                ],
                'metadata': {
                    'ProductTitle': this.getTitle()?.title,
                },
            },
            'configuration': {
                'id': 'div-relatedvideos',
                'type': 'relatedvideos',
                'binder': 'relatedvideos',
                'loader': 'lazyload',
                'features': {
                    'features': {
                        'verticalcarousel': 'true',
                        'hide_default_buttons': 'true',
                        'first_item_flush_left': 'true',
                        'pagestate': 'dp_vse_rvc',
                        'reftagprefix': 'dp_vse_ibvc',
                        'carouselName': 'vse-ib-rvs',
                        'count': '16',
                        'useLazyLoad': 'false',
                        'hidePlayIcon': 'true',
                        'hideCustomerReviewPrefix': 'true',
                        'cssClass': 'vse-hide-carousel-title',
                        'segmentOneHeaderId': 'vse_ib_segment_one',
                        // 'segmentTwoHeaderId': 'ive_related_videos_for_this_product',
                        // 'segmentThreeHeaderId': 'vse_ib_segment_three',
                        'segmentOneHeaderDefault': 'Videos for this product',
                        // 'segmentTwoHeaderDefault': 'Related videos for this product',
                        // 'segmentThreeHeaderDefault': 'Customer review videos',
                        // 'includeProfiles': 'true',
                        'includeProfiles': 'false',
                        // 'showCustomerReviewMetadata': 'true',
                        'showCustomerReviewMetadata': 'false',
                        //'enableCustomerReviewVideos': 'true',
                        'enableCustomerReviewVideos': 'false',
                    },
                },
                'sources': {
                    'source': 'VideoAdsDataAggregatorService',
                },
            },
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
        if (result.status > 299) {
            return { relatedVideos: null };
        }
        const parsedResHTML = this.domparser.parseFromString(await result.text(), 'text/html');
        const links = [...(parsedResHTML.querySelectorAll('[data-video-url]') || [])]
            .filter(el => el.getElementsByTagName('h4')[0]?.textContent === 'Videos for this product')
            .map(el => el.getAttribute('data-video-url'));
        return { relatedVideos: (this.relatedVideos = links) };
    }

    getRequestID() {
        if (this.requestID) {
            return { requestID: this.requestID };
        }
        const allScripts = this.root.getElementsByTagName('script');
        for (const script of allScripts) {
            const scriptContent = script.textContent.trim();
            const position = scriptContent.slice(0, 750).indexOf('RequestID\':');
            if (position + 1) {
                this.requestID = scriptContent.slice(position + 11, position + 33).trim().slice(1);
                break;
            }
        }
        return { requestID: this.requestID };
    }

    getFullMediaConfig() {
        if (this.mediaConfig) {
            return { mediaConfig: this.mediaConfig };
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
            this.mediaConfig = JSON.parse(needleContent);
            delete this.mediaConfig.updateDivLists;
            delete this.mediaConfig.unselectedDimCount;
            return { mediaConfig: this.mediaConfig };
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
        return { description: el.textContent.replaceAll(/ {2,}/gm, '\n').trim() };
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
        const ratingEl = this.root.querySelector('#averageCustomerReviews > span:first-child');
        if (!ratingEl) {
            return { rating: null };
        }
        const rating = Number.parseFloat(ratingEl.textContent.trim().split(' ')[0]);
        if (Number.isNaN(rating)) {
            return { rating: null };
        }
        return { rating };
    }

    getReviewsCount() {
        const countEl = this.root.querySelector('#averageCustomerReviews > span:last-of-type');
        if (!countEl) {
            return { reviewsCount: null };
        }
        let reviewsCount = countEl.textContent?.trim().split(' ')[0]?.replaceAll(',', '');
        if (!reviewsCount) {
            return { reviewsCount: null };
        }
        reviewsCount = Number.parseInt(reviewsCount);
        if (Number.isNaN(reviewsCount)) {
            return { reviewsCount: null };
        }
        return { reviewsCount };
    }

    getOptions() {

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
        const root_div = this.root.querySelector('[data-csa-c-slot-id="cr-product-insights-cards-popover"]');
        if (!root_div) {
            return { aspects: null };
        }
        const aspects_names_els = this.root.getElementById('aspect-button-group-0')
            ?.querySelectorAll('[id*=aspect-button]');
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
            res.push({ Aspect: aspects_names_els[i].innerText.trim(), positive: positive, negative: negative });
        }
        return { aspects: (res.length ? res : null) };
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
}
