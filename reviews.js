
class CollectReviews {
    index = 0
    current_format
    page = 1
    keywords
    auto_send_to_AI = true
    asin
    URL
    domain
    prefix

    params = {
        'sortBy': ['', 'recent'],
        'reviewerType': ['all_reviews', 'avp_only_reviews'],
        'filterByStar': ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
        'mediaType': ['', 'media_reviews_only'],
    }

    per_page_callback = null
    per_index_callback = null
    invalidasinerror_callback = null
    serviceunavailableerror_callback = null
    finish_callback = null

    constructor(asin: string, prefix: string, current_format: boolean = true, keywords: string = '', domain = 'amazon.com') {
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
            'scope': 'reviewsAjax{}'.format((this.index + 1) * this.page),
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
            throw new Error('Service unavailable')
        }
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
                    const review_date_words = review_date_raw.innerHTML.trim().split(' ')
                    let first = true
                    review_country = ''
                    let idx = 0
                    for (const word of review_date_words) {
                        if (word.istitle()) {  // ??

                        }
                    }
                    if first:
                    first = False
                else:
                    review_country += word + ' '
                    elif review_country:
                        review_country = review_country.strip()
                    idx += 1
                    break
                    idx += 1
                    date_part = [rword.replace(',', '') for rword in review_date_words[idx:]]
                    year_like = list(filter(lambda x: x.isdigit() and len(x) == 4, date_part))
                    review_date_dict: dict[str, int | None] = {}
                    if len(year_like) == 1:
                    review_date_dict['year'] = int(year_like[0])
                else:
                    review_date_dict['year'] = None
                    day_like = list(filter(lambda x: x.isdigit() and len(x) in (1, 2), date_part))
                    if len(day_like) == 1:
                    review_date_dict['day'] = int(day_like[0])
                else:
                    review_date_dict['day'] = None
                    month_like = list(filter(lambda x: not x.isdigit() and len(x) > 2, date_part))
                    if len(month_like) == 1:
                    review_date_dict['month'] = month_to_int(month_like[0])
                else:
                    review_date_dict['month'] = None
                    if all(review_date_dict.values()):
                    review_date = datetime.datetime(
                        review_date_dict['year'],
                        review_date_dict['month'],
                        review_date_dict['day'],
                    )
                else:
                    review_date = None
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
        let params_count = 0, result
        for (const params_variants of this.params) {
            params_count += params_variants.length
        }

        for (; this.index < params_count; ++this.index) {
            for (; this.page <= 10; ++this.page) {
                try {
                    result = await this.sendRequest()
                    if (!result) {
                        break
                    }
                } catch (e) {
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
        }
    }

    reset() {
        this.page = 1
        this.index = 0
    }
}
