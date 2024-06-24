class CollectReviews {
    index = 0
    page = 1
    // Collect params
    current_format
    keywords
    asin
    URL
    domain
    prefix
    // Request params
    params = {
        'sortBy': ['', 'recent'],
        'reviewerType': ['all_reviews', 'avp_only_reviews'],
        'filterByStar': ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
        'mediaType': ['', 'media_reviews_only'],
    }
    // Callbacks
    per_page_callback = null
    per_index_callback = null
    invalidasinerror_callback = null
    serviceunavailableerror_callback = null
    finish_callback = null

    constructor(asin, prefix, current_format = true, keywords = '', domain = 'amazon.com') {
        this.asin = asin
        this.current_format = current_format
        this.keywords = keywords
        this.domain = domain
        this.prefix = prefix
        this.URL = 'https://www.' + domain + '/' + (prefix ? prefix + '/' : '') + 'dp/' + asin + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
    }


    getParams() {
        let current_params = {
            'formatType': this.current_format ? 'current_format' : '',
            'filterByAge': '',
            'pageNumber': this.page,
            'filterByLanguage': '',
            'filterByKeyword': this.keywords,
            'shouldAppend': 'undefined',
            'deviceType': 'desktop',
            'canShowIntHeader': 'undefined',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 10,
            'asin': this.asin,
            'scope': `reviewsAjax${(this.index + 1) * this.page}`,
        }

        let s = this.index
        let length

        for (const i in this.params) {
            length = this.params[i].length
            current_params[i] = this.params[i][s % length]
            s = Math.floor(s / length)
        }

        return current_params
    }

    getRequestBody(data_obj) {
        const formBody = [];
        let encodedKey, encodedValue
        for (const property in data_obj) {
            encodedKey = encodeURIComponent(property);
            encodedValue = encodeURIComponent(data_obj[property]);
            formBody.push(encodedKey + '=' + encodedValue);
        }
        return formBody.join('&');
    }

    async sendRequest() {
        const params = this.getParams()

        const request_result = await fetch(
            `https://www.${this.domain}/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt`,
            {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                },
                'referrer': `https://www.${this.domain}/${this.prefix ? this.prefix + '/' : ''}product-reviews/${this.asin}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=${params.reviewerType}&filterByStar=${params.filterByStar}&sortBy=${params.sortBy}&mediaType=${params.mediaType}&pageNumber=${this.page}`,
                'body': this.getRequestBody(params),
            },
        )
        const res_text = await request_result.text()
        if (res_text.includes('BAAAAAAD ASIN!')) {
            throw new Error('Invalid ASIN')
        }
        if (request_result.status !== 200) {
            console.log('Service unavailable')
            throw new Error('Service unavailable')
        }
        console.log('Send success!')
        return this.processRequest(res_text)
    }

    processRequest(raw_data, return_count = false) {
        let res = {}
        const process_data_res = raw_data.trim().replaceAll(/\["script","if\(window\.ue\) \{[^]]+]/, '')
        let row
        const raw = []
        for (row of process_data_res.replaceAll('\r', '').split('\n')) {
            try {
                row = JSON.parse(row.trim())
                if (row.length >= 3 && row[1] !== '#cm_cr-review_list' && (row[2] = row[2].trim())) {
                    raw.push(row)
                }
            } catch (e) {
            }
        }
        const parser = new DOMParser()
        if (raw[0][1] !== 'filter-info-section') {
            return null
        }
        if (return_count) {
            const doc = parser.parseFromString(raw[0][2])
            const [total, reviews] = doc.querySelector('[data-hook=cr-filter-info-review-rating-count]')?.innerHTML?.trim()?.replaceAll(',', '')?.match(/\d+/g) || [0, 0]
            res['total_count'] = total
            res['reviews_count'] = reviews
        }

        let root_el, review_el, review_id, review_date_raw, review_country, review_date

        for (const el of raw) {
            root_el = parser.parseFromString(el[2].trim())
            if (root_el.querySelector('div.a-divider-section, h3[data-hook=dp-global-reviews-header]')) {
                continue
            }
            if ((review_el = root_el.querySelector('[data-hook=review]'))) {
                //
                review_id = review_el.getAttribute('id')
                //
                if ((review_date_raw = review_el.querySelector('[data-hook=review-date]'))) {
                    let review_date_words = review_date_raw.innerHTML.trim().split(' ')
                    review_date_words = review_date_words.slice(2)
                    review_country = ''
                    let idx = 0
                    for (const word of review_date_words) {
                        if (word[0].toUpperCase() === word[0] && word[1] && word[1].toLowerCase() === word[1]) {
                            review_country += word + ' '
                        }
                        else if (review_country) {
                            review_country = review_country.trim()
                            ++idx
                            break
                        }
                        ++idx
                    }
                    const year_like = [], day_like = [], month_like = []
                    for (let rword of review_date_words.slice(idx)) {
                        rword = rword.replaceAll(',', '').trim()
                        if (/^\d+$/.test(rword)) {
                            if (rword.length === 4) {
                                year_like.push(Number(rword))
                            } else {
                                day_like.push(rword)
                            }
                        }
                        else if (rword.length > 2) {
                            month_like.push(rword)
                        }
                    }
                    const review_date_dict = {}
                    if (year_like.length === 1) {
                        review_date_dict.year = Number(year_like[0])
                    }
                    else {
                        review_date_dict.year = null
                    }
                    if (day_like.length === 1){
                        review_date_dict.day = Number(day_like[0])
                    }
                    else {
                        review_date_dict['day'] = null
                    }
                    if (month_like.length === 1) {
                        review_date_dict['month'] = monthToNum(month_like[0])
                    }
                    else {
                        review_date_dict['month'] = null
                    }
                    if ((Object.values(review_date_dict)).every((i) => {return i > 0;})) {
                        review_date = [
                            review_date_dict['year'],
                            review_date_dict['month'],
                            review_date_dict['day'],
                        ]
                    }
                    else {
                        review_date = null
                    }
                }
                else {
                    review_date = null
                    review_country = null
                }
                // Customer name
                const customer_name = review_el.querySelector('span.a-profile-name')?.innerText.trim().replace('\n', ' ') || ''
                // Title
                let review_title = review_el.querySelector('a[data-hook=review-title] > span:not(.a-letter-space)')?.innerText.trim() || ''
                // Content
                const review_body = review_el.querySelector('span[data-hook=review-body]')?.innerText.trim().replace('\n', ' ') || ''
                // Rating
                const review_star_rating = (review_el.querySelector('i[data-hook=review-star-rating]') || review_el.querySelector('i[data-hook=cmps-review-star-rating]') || review_el.querySelector('i.cr-lightbox-review-rating'))
                let review_rating
                if (review_star_rating) {
                    review_rating = Number(review_star_rating.querySelector('span').innerText.split(' ')[0].trim())
                } else {
                    review_rating = 0
                }
                // Helpful votes
                let helpful_votes = review_el.querySelector('span[data-hook=helpful-vote-statement]')
                if (helpful_votes) {
                    helpful_votes = helpful_votes.innerText.matchAll(/\d+/g).map(el => el[0]).toArray().join('')
                    if (helpful_votes) {
                        helpful_votes = Number(helpful_votes)
                    }
                    else {
                        helpful_votes = 1
                    }
                }
                else {
                    helpful_votes = 0
                }
                // Options
                let review_options = review_el.querySelector('a[data-hook=format-strip]') || review_el.querySelector('span[data-hook=format-strip-linkless]')
                if (review_options) {
                    const divider = review_options.querySelector('i.a-icon.a-icon-text-separator').outerHTML
                    if (divider) {
                        review_options = review_options.innerHTML.split(divider)
                    }
                    else {
                        review_options = [review_options.innerText]
                    }
                }
                else {
                    review_options = []
                }
                return {
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
                }
            }
        }
    }

    async collect() {
        /*
        * что делать при ошибке?
        *  - при parseerror пропускать
        *  - при badasinerror - останавливать
        *  - при service unavailable - ??
        */
        let params_count = 1, result, res_arr = [], fin_res_arr = []
        for (const key in this.params) {
            params_count *= this.params[key].length
        }

        for (; this.index < params_count; ++this.index) {
            for (; this.page <= 10; ++this.page) {
                try {
                    result = await this.sendRequest()
                    console.log(result)
                    if (!result) {
                        break
                    }
                    if (this.per_page_callback) {
                        this.per_page_callback(result);
                    }
                    if (this.per_index_callback) {
                        res_arr.push(result)
                    }
                    if (this.finish_callback) {
                        fin_res_arr.push(result)
                    }
                } catch (e) {
                    console.log(e.message)
                    if (e.message === 'Invalid ASIN') {
                        if (this.invalidasinerror_callback) {
                            return this.invalidasinerror_callback(this)
                        }
                        return
                    } else if (e.message === 'Service unavailable') {
                        if (this.serviceunavailableerror_callback) {
                            if (!this.serviceunavailableerror_callback(this)) {
                                return
                            }
                        }
                    }
                }
            }
            this.page = 1
            if (this.per_index_callback) {
                this.per_index_callback(res_arr);
            }
        }
    }

    reset() {
        this.page = 1
        this.index = 0
    }
}

function monthToNum(month) {
    month = month.toLowerCase()
    let r
    if (month[0] === 'f') {
        r = 2
    } else if (month[0] === 'j' && month[1] === 'u') {
        r = 6 + ('l' in month)
    } else if (month[0] === 'a') {
        r = 4 + 4 * ('g' in month)
    } else if (month[0] === 'm') {
        r = 3 + 2 * (!month.includes('r'))
    } else if (month[0] === 's') {
        r = 9
    } else if (month[0] === 'o') {
        r = 10
    } else if (month[0] === 'n') {
        r = 11
    } else if (month[0] === 'd') {
        r = 12
    } else {
        r = 1
    }
    return r
}
