class SearchMultiParser extends MultiParser {
    elementsQuerySelector = 'div[data-asin]';
    waitElementQuerySelector = '.s-result-item';
    // cache
    imageElement = null;
    reviewsBlockElement = null;

    getASIN(el) {
        const asin = el.getAttribute('data-asin')?.trim();
        if (!asin) {
            return false;
        }
        return { asin };
    }

    newIteration() {
        super.newIteration();
        this.imageElement = null;
        this.reviewsBlockElement = null;
    }

    getTitle(el, index, preResult) {
        const titleEl = el.querySelector('[data-cy="title-recipe"]');
        if (!titleEl) {
            const titleLengthMap = {};
            if (preResult && preResult.asin) {
                const productLinks = el.querySelectorAll(`a[href*="${preResult.asin}"]`);
                for (const link of productLinks) {
                    const title = link.textContent?.trim();
                    if (title) {
                        titleLengthMap[title.length] = title;
                    }
                }
            }
            return titleLengthMap[Math.max(...Object.keys(titleLengthMap))] || null;
        }
        const headers = titleEl.getElementsByTagName('h2');
        if (headers && headers.length) {
            return { title: headers[0].textContent.trim() };
        }
        return { title: titleEl.textContent.trim() };
    }

    getReviewsBlockElement(el) {
        if (this.reviewsBlockElement) {
            return this.reviewsBlockElement;
        }
        return (this.reviewsBlockElement = el.querySelector('[data-cy="reviews-block"] > div'));
    }

    getReviewsCount(el) {
        const reviewsEl = this.getReviewsBlockElement(el);
        if (!reviewsEl) {
            return { reviewsCount: 0 };
        }
        const count = reviewsEl.children[1]?.textContent.trim().replaceAll(',', '');
        const intCount = Number.parseInt(count || 0);
        if (Number.isNaN(intCount)) {
            return { reviewsCount: 0 };
        }
        return { reviewsCount: intCount };
    }

    getReviewsRating(el) {
        const reviewsEl = this.getReviewsBlockElement(el);
        if (!reviewsEl) {
            return { rating: null };
        }
        const ratingEl = reviewsEl.children[0];
        const parsedRating = ratingEl.getAttribute('aria-label')?.trim()?.split(' ');
        return { rating: (parsedRating ? Number.parseFloat(parsedRating) : null) };
    }

    getPrice(el) {
        let priceEl = el.querySelector('[data-cy="price-recipe"]');
        if (!priceEl) {
            return { price: null };
        }
        const priceRow = priceEl.querySelector('div.a-row.a-size-base');
        let price = priceRow.innerText.trim();
        if (!price) {
            return { price: null };
        }
        // split by lines
        price = price.split('\n')[0];
        // delete redundant data
        price = price.split(' ')[0];
        // delete char '$'
        price = price.slice(1);
        return { price: (price ? Number.parseFloat(price) : null) };
    }

    getImageElement(el) {
        if (this.imageElement) {
            return this.imageElement;
        }
        return (this.imageElement = el.querySelector('img[srcset]'));
    }

    getImageLinks(el) {
        const imgEl = this.getImageElement(el);
        if (!imgEl) {
            return { imageSrc: null };
        }
        const srcset = imgEl.getAttribute('srcset');
        if (!srcset) {
            const imageSrc = imgEl.getAttribute('src');

            return { imageSrc: (imageSrc || null) };
        }
        try {
            const srcdata = JSON.parse(srcset);
            const sources = Object.keys(srcdata);
            return (sources && sources.length) ? { src: sources[sources.length - 1] } : null;
        } catch (e) {
            const srclinks = srcset.split(',');
            const parsedSrclinks = [];
            for (let link of srclinks) {
                link = link.trim();
                link = link.split(' ')[0].trim();
                if (link) {
                    parsedSrclinks.push(link);
                }
            }
            return { imageSrc: (parsedSrclinks.length ? parsedSrclinks[parsedSrclinks.length - 1] : null) };
        }
    }

    clickNextPage() {
        super.clickNextPage();
        const el = document.querySelector('.s-pagination-item:last-child');
        if (el.tagName === 'SPAN') {
            return false;
        }
        el.click();
        return true;
    }
}