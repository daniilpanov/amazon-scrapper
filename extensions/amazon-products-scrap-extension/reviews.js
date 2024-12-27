class CollectReviews {
    index = 0;
    page = 1;
    // Collect params
    current_format;
    keywords;
    asin;
    URL;
    domain;
    prefix;
    // Callbacks
    per_page_callback = null;
    per_index_callback = null;
    invalidasinerror_callback = null;
    serviceunavailableerror_callback = null;
    finish_callback = null;
    // Current params
    named_filters = {};
    named_options = {};
    indexes_map = {};
    directions = {}
    indexes_limits = {};
    indexes_half_period = {};
    format_type_filter = null;
    format_type_options = null;
    params_count = 1;
    // Count
    total_count = 0;
    reviews_count = 0;

    constructor(asin, prefix, current_format = true, keywords = '', domain = 'amazon.com') {
        this.asin = asin;
        this.current_format = current_format;
        this.keywords = keywords;
        this.domain = domain;
        this.prefix = prefix;
        this.URL = 'https://www.' + domain + '/' + (prefix ? prefix + '/' : '') + 'dp/' + asin + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews';
    }

    // TODO: replace with observer
    async waitLoad() {
        for (let i = 0; i < 100; ++i) {
            await new Promise(resolve => setTimeout(resolve, 100));
            if (!document.querySelector('.cr-list-loading.reviews-loading:not(.aok-hidden)')) {
                return;
            }
        }
    }

    parse(return_count = false) {
        if (return_count) {
            const [total, reviews] = document.querySelector('[data-hook=cr-filter-info-review-rating-count]')?.innerHTML.trim().replaceAll(',', '').match(/\d+/g) || [0, 0];
            this.total_count = total;
            this.reviews_count = reviews;
        }
        let review_id, review_date_raw, review_country, review_date, reviews = [];

        for (const review_el of document.querySelectorAll('[data-hook=review]')) {
            // review ID
            review_id = review_el.getAttribute('id');
            // review date
            if ((review_date_raw = review_el.querySelector('[data-hook=review-date]'))) {
                // parse words
                let review_date_words = review_date_raw.innerHTML.trim().split(' ');
                // first two are 'reviewed at'
                review_date_words = review_date_words.slice(2);
                review_country = '';
                let idx = 0;  // index of beginning of date in string
                for (const word of review_date_words) {
                    ++idx;
                    // if word.istitle()
                    if (word[0].toUpperCase() === word[0] && word[1] && word[1].toLowerCase() === word[1]) {
                        review_country += word + ' ';
                    }
                    // if review country is set and current word is not title (end of country name)
                    else if (review_country) {
                        review_country = review_country.trim();
                        break;
                    }
                }
                // date parsing
                const year_like = [], day_like = [], month_like = [];
                for (let rword of review_date_words.slice(idx)) {
                    rword = rword.replaceAll(',', '').trim();  // simplify
                    // numbers may be days or years
                    if (/^\d+$/.test(rword)) {
                        if (rword.length === 4) {
                            year_like.push(Number(rword));
                        } else {
                            day_like.push(rword);
                        }
                    }
                    // string is month if len > 2
                    else if (rword.length > 2) {
                        month_like.push(rword);
                    }
                }
                // convert to preferred format
                const review_date_dict = {};
                if (year_like.length === 1) {
                    review_date_dict.year = Number(year_like[0]);
                }
                else {
                    review_date_dict.year = null;
                }
                if (day_like.length === 1){
                    review_date_dict.day = Number(day_like[0]);
                }
                else {
                    review_date_dict['day'] = null;
                }
                if (month_like.length === 1) {
                    review_date_dict['month'] = monthToNum(month_like[0]);
                }
                else {
                    review_date_dict['month'] = null;
                }
                if ((Object.values(review_date_dict)).every((i) => {return i > 0;})) {
                    review_date = review_date_dict['year'] + '-' + review_date_dict['month'].toString().padStart(2, 0) + '-' + review_date_dict['day'].toString().padStart(2, 0);
                }
                else {
                    review_date = null;
                }
            }
            else {
                review_date = null;
                review_country = null;
            }
            // Customer name
            const customer_name = review_el.querySelector('span.a-profile-name')?.innerText.trim().replace('\n', ' ') || '';
            // Title
            let review_title = review_el.querySelector('a[data-hook=review-title] > span:not(.a-letter-space)')?.innerText.trim() || '';
            // Content
            const review_body = review_el.querySelector('span[data-hook=review-body]')?.innerText.trim().replace('\n', ' ') || '';
            // Rating
            const review_star_rating = (review_el.querySelector('i[data-hook=review-star-rating]') || review_el.querySelector('i[data-hook=cmps-review-star-rating]') || review_el.querySelector('i.cr-lightbox-review-rating'));
            let review_rating;
            if (review_star_rating) {
                review_rating = Number(review_star_rating.querySelector('span').innerText.split(' ')[0].trim());
            } else {
                review_rating = 0;
            }
            // Helpful votes
            let helpful_votes = review_el.querySelector('span[data-hook=helpful-vote-statement]');
            if (helpful_votes) {
                helpful_votes = helpful_votes.innerText.matchAll(/\d+/g).map(el => el[0]).toArray().join('');
                if (helpful_votes) {
                    helpful_votes = Number(helpful_votes);
                }
                else {
                    helpful_votes = 1;
                }
            }
            else {
                helpful_votes = 0;
            }
            // Options
            let review_options = review_el.querySelector('a[data-hook=format-strip]') || review_el.querySelector('span[data-hook=format-strip-linkless]');
            if (review_options) {
                const divider = review_options.querySelector('i.a-icon.a-icon-text-separator')?.outerHTML;
                if (divider) {
                    review_options = review_options.innerHTML.split(divider);
                }
                else {
                    review_options = [review_options.innerText];
                }
            }
            else {
                review_options = [];
            }
            reviews.push({
                'review_id': review_id,
                'product_url': `https://www.${this.domain}/dp/${this.asin}`,
                'asin': this.asin,
                'date': review_date,
                'country': review_country,
                'name': customer_name,
                'title': review_title,
                'description': review_body,
                'rating': review_rating,
                'helpful': helpful_votes,
                'options': review_options,
            });
        }
        return reviews;
    }

    async updateParams() {
        const filters = document.querySelectorAll('[id*="cm_cr-view_opt_"] select');
        this.named_filters = {};
        this.named_options = {};
        let opts;
        if (filters && filters.length) {
            filters[0].scrollIntoView();
            for (let filter of filters) {
                filter.click();
                const key = filter.id.replace('-dropdown', '');
                this.named_filters[key] = filter;
                await new Promise(resolve => setTimeout(resolve, 500));
                opts = [];
                document.querySelectorAll('.a-popover li[aria-labelledby*="' + filter.id + '"] a').forEach(o => opts.push(o));
                this.named_options[key] = opts;
            }
            // Remove redundant params
            this.named_options['star-count'].pop();
            this.named_options['star-count'].pop();
            // Move special filters
            if ('format-type' in this.named_filters) {
                this.format_type_filter = this.named_filters['format-type'];
                this.format_type_options = this.named_options['format-type'];
                delete this.named_filters['format-type'];
                delete this.named_options['format-type'];
            }
            // Count filters params variants
            let l;
            for (const i in this.named_options) {
                if (i !== 'star-count') continue;
                l = this.named_options[i].length;
                this.indexes_map[i] = 0;
                this.indexes_limits[i] = l;
                this.indexes_half_period[i] = this.params_count;
                this.directions[i] = 1;
                this.params_count *= l || 1;
            }
        }
    }

    // snake-like switching pattern
    async switching() {
        if (this.index >= this.params_count) {
            console.log(...Object.values(this.indexes_map), 'END');
            chrome.runtime.sendMessage({log: [...Object.values(this.indexes_map), 'END']}, () => {});
            return false;
        }
        let curr = this.index++;
        if (curr === 0) {
            console.log(...Object.values(this.indexes_map));
            chrome.runtime.sendMessage({log: [...Object.values(this.indexes_map)]}, () => {});
            return true;
        } else if (this.reviews_count <= 125) {
            return false;
        }
        let key;
        const reversed_keys = Object.keys(this.indexes_map).reverse();
        for (key of reversed_keys) {
            if (!(curr % this.indexes_half_period[key])) {
                break;
            }
        }
        if (this.indexes_map[key] >= this.indexes_limits[key] - 1) {
            this.directions[key] = -1;
        } else if (this.indexes_map[key] <= 0) {
            this.directions[key] = 1;
        }
        this.indexes_map[key] += this.directions[key];

        console.log(...Object.values(this.indexes_map));
        chrome.runtime.sendMessage({log: [...Object.values(this.indexes_map)]}, () => {});

        try {
            this.named_filters[key].click();
        } catch (e) {
            console.error('Error when trying to click to filter:', e);
            chrome.runtime.sendMessage({log: ['Error when trying to click to filter:', e]}, () => {});
            return false;
        }
        const opts = this.named_options[key] = [];
        await new Promise(resolve => setTimeout(resolve, 100));
        try {
            document.querySelectorAll('.a-popover li[aria-labelledby*="' + this.named_filters[key].id + '"] a').forEach(o => opts.push(o));
        } catch (e) {
            console.error('Error when looking for options:', e);
            chrome.runtime.sendMessage({log: ['Error when looking for options:', e]}, () => {});
            return false;
        }
        try {
            this.named_options[key][this.indexes_map[key]].scrollIntoView();
            this.named_options[key][this.indexes_map[key]].click();
        } catch (e) {
            console.error('Error when clicking option:', e);
            chrome.runtime.sendMessage({log: ['Error when clicking option:', e]}, () => {});
            return false;
        }
        this.page = 1;

        return true;
    }

    async collect() {
        await this.updateParams();
        this.parse(true);

        if (this.format_type_filter) {
            this.format_type_filter.click();
            const opts = this.format_type_options = [];
            await new Promise(resolve => setTimeout(resolve, 100));
            document.querySelectorAll('.a-popover li[aria-labelledby*="' + this.format_type_filter.id + '"] a').forEach(o => opts.push(o));
            this.format_type_options[Number(this.current_format)].click();
        }

        let result, res_arr = [];
        while (this.index < this.params_count) {
            await this.waitLoad();
            if (!await this.switching()) {
                break;
            }
            for (; this.page <= 10; ++this.page) {
                await this.waitLoad();
                await new Promise(resolve => setTimeout(resolve, 100));
                try {
                    result = this.parse();
                    if (!result || !result.length) {
                        break;
                    }
                    if (this.per_page_callback) {
                        this.per_page_callback(result);
                        for (const item of result){
                            res_arr.push(item);
                        }
                    }
                } catch (e) {
                    console.log(e.message);
                    if (e.message === 'Invalid ASIN') {
                        if (this.invalidasinerror_callback) {
                            return this.invalidasinerror_callback(this);
                        }
                        return;
                    } else if (e.message === 'Service unavailable') {
                        if (this.serviceunavailableerror_callback) {
                            if (!this.serviceunavailableerror_callback(this)) {
                                return;
                            }
                        }
                    }
                }
                try {
                    const next = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
                    if (!next) {
                        break;
                    }
                    next.scrollIntoView();
                    next.click();
                } catch (e) {
                    console.log('No pagination found:', e);
                    chrome.runtime.sendMessage({log: ['No pagination found:', e]}, () => {});
                    break;
                }
            }
            if (this.per_index_callback) {
                this.per_index_callback(res_arr);
            }
            res_arr = [];
        }
        if (this.finish_callback) {
            this.finish_callback();
        }
    }

    reset() {
        this.page = 1;
        this.index = 0;
    }
}

// Universal and fast method FOR DIFFERENT LANGUAGES (tested on Spanish and English)
function monthToNum(month) {
    month = month.toLowerCase();
    let r;
    if (month[0] === 'f') {
        r = 2;
    } else if (month[0] === 'j' && month[1] === 'u') {
        r = 6 + (month.includes('l'));
    } else if (month[0] === 'a') {
        r = 4 + 4 * (month.includes('g'));
    } else if (month[0] === 'm') {
        r = 3 + 2 * (!month.includes('r'));
    } else if (month[0] === 's') {
        r = 9;
    } else if (month[0] === 'o') {
        r = 10;
    } else if (month[0] === 'n') {
        r = 11;
    } else if (month[0] === 'd') {
        r = 12;
    } else {
        r = 1;
    }
    return r;
}
