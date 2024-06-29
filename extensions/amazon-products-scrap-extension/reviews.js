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
    indexes_map_prev = {};
    indexes_limits = {};
    indexes_half_period = {0: 1};
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

    async waitLoad() {
        for (let i = 0; i < 1000; ++i) {
            await new Promise(resolve => setTimeout(resolve, 100));
            if (!document.querySelector('.cr-list-loading.reviews-loading:not(.aok-hidden)') && document.querySelector('.a-pagination .a-last')) {
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
        filters[0].scrollIntoView();
        this.named_filters = {};
        this.named_options = {};
        let opts;
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
        this.named_options['star-count'].pop(7);
        this.named_options['star-count'].pop(6);
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
            this.params_count *= l || 1;
            l = this.named_options[i].length;
            this.indexes_map[i] = 0;
            this.indexes_map_prev[i] = 0;
            this.indexes_limits[i] = l - 1;
            this.indexes_half_period[i] = this.params_count;
        }
    }

    getDirectionOfIndex(idx) {
        if (this.indexes_map[idx] >= this.indexes_limits[idx]) {
            return -1;
        }
        const diff = Boolean(this.indexes_map_prev[idx] - this.indexes_map[idx] + 1);
        return diff - !diff;
    }

    // snake-like switching pattern
    async switching() {
        let mod = 1, idx;
        const keys = Object.keys(this.named_options).reverse(), add_keys = Object.keys(this.named_options).reverse();
        add_keys.push(0);
        for (idx of keys) {
            if (!this.index) {
                ++this.index;
                return;
            }
            mod = this.index % this.indexes_half_period[idx];
            if (!mod) {
                break;
            }
        }
        const dir = this.getDirectionOfIndex(idx);
        this.indexes_map_prev = {...this.indexes_map};
        this.indexes_map[idx] += dir;
        this.named_filters[idx].click();
        const opts = this.named_options[idx] = [];
        await new Promise(resolve => setTimeout(resolve, 100));
        document.querySelectorAll('.a-popover li[aria-labelledby*="' + this.named_filters[idx].id + '"] a').forEach(o => opts.push(o));
        this.named_options[idx][this.indexes_map[idx]].scrollIntoView();
        this.named_options[idx][this.indexes_map[idx]].click();
        ++this.index;
        this.page = 1;
    }

    async collect() {
        await this.updateParams();

        if (this.format_type_filter) {
            this.format_type_filter.click();
            const opts = this.format_type_options = [];
            await new Promise(resolve => setTimeout(resolve, 100));
            document.querySelectorAll('.a-popover li[aria-labelledby*="' + this.format_type_filter.id + '"] a').forEach(o => opts.push(o));
            this.format_type_options[Number(this.current_format)].click();
        }

        let result, res_arr = [];
        for (; this.index < this.params_count; ++this.index) {
            await this.waitLoad();
            await this.switching();
            for (; this.page <= 10; ++this.page) {
                await this.waitLoad();
                await new Promise(resolve => setTimeout(resolve, 100));
                try {
                    result = this.parse();
                    console.log(result);
                    if (!result || !result.length) {
                        break;
                    }
                    if (this.per_page_callback) {
                        this.per_page_callback(result);
                    }
                    if (this.per_index_callback) {
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
                    document.querySelector('.a-pagination .a-last > a').click();
                    document.querySelector('.a-pagination .a-last > a').scrollIntoView();
                } catch (e) {
                    console.log(e);
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
