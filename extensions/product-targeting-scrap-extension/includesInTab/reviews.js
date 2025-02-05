class ReviewsMultiParser extends MultiParser {
    elementsQuerySelector = '[data-hook=review]';
    countReviews = null;

    getReviewId(el) {
        const id = el.getAttribute('id');
        return id ? { review_id: id } : false;
    }

    getNickname(el) {
        return { name: el.querySelector('.a-profile .a-profile-content')?.textContent.trim().replace('\n', ' ') || null };
    }

    getTitle(el) {
        return { title: el.querySelector('a[data-hook=review-title] > span:not(.a-letter-space)')?.textContent.trim() || null };
    }

    getContent(el) {
        return { description: el.querySelector('span[data-hook=review-body]')?.innerText.trim().replace('\n', ' ') || null };
    }
    
    getHelpful(el) {
        // Helpful votes
        let helpful = el.querySelector('span[data-hook=helpful-vote-statement]');
        if (helpful) {
            helpful = helpful.innerText.matchAll(/\d+/g).map(el => el[0]).toArray().join('');
            if (helpful) {
                helpful = Number(helpful);
            }
            else {
                helpful = 1;
            }
        }
        else {
            helpful = 0;
        }
        
        return { helpful };
    }
    
    getOptions(el) {
        // Options
        let review_options = el.querySelector('a[data-hook=format-strip]') || el.querySelector('span[data-hook=format-strip-linkless]');
        if (review_options) {
            const divider = review_options.querySelector('i.a-icon.a-icon-text-separator')?.outerHTML;
            if (divider) {
                review_options = review_options.innerHTML.split(divider);
            }
            else {
                review_options = [review_options.textContent.trim()];
            }
        }
        else {
            review_options = [];
        }
        
        return { review_options };
    }
    
    getRating(el) {
        const review_star_rating = (el.querySelector('i[data-hook=review-star-rating]') || el.querySelector('i[data-hook=cmps-review-star-rating]') || el.querySelector('i.cr-lightbox-review-rating'));
        let rating;
        if (review_star_rating) {
            rating = Number(review_star_rating.querySelector('span').innerText.split(' ')[0].trim());
        } else {
            rating = 0;
        }
        
        return { rating };
    }
    
    getDateAndPlace(el) {
        let date_raw, date, country;
        if ((date_raw = el.querySelector('[data-hook=review-date]'))) {
            // parse words
            let date_words = date_raw.innerHTML.trim().split(' ');
            // first two are 'reviewed at'
            date_words = date_words.slice(2);
            country = '';
            let idx = 0;  // index of beginning of date in string
            for (const word of date_words) {
                ++idx;
                // if word.istitle()
                if (word[0].toUpperCase() === word[0] && word[1] && word[1].toLowerCase() === word[1]) {
                    country += word + ' ';
                }
                // if review country is set and current word is not title (end of country name)
                else if (country) {
                    country = country.trim();
                    break;
                }
            }
            // date parsing
            const year_like = [], day_like = [], month_like = [];
            for (let rword of date_words.slice(idx)) {
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
            const date_dict = {};
            if (year_like.length === 1) {
                date_dict.year = Number(year_like[0]);
            }
            else {
                date_dict.year = null;
            }
            if (day_like.length === 1){
                date_dict.day = Number(day_like[0]);
            }
            else {
                date_dict['day'] = null;
            }
            if (month_like.length === 1) {
                date_dict['month'] = monthToNum(month_like[0]);
            }
            else {
                date_dict['month'] = null;
            }
            if ((Object.values(date_dict)).every((i) => {return i > 0;})) {
                date = date_dict['year'] + '-' + date_dict['month'].toString().padStart(2, 0) + '-' + date_dict['day'].toString().padStart(2, 0);
            }
            else {
                date = null;
            }
        }
        else {
            date = null;
            country = null;
        }
        return { date, country };
    }


    // TODO: two types of switching: 1) by filters, 2) by queries, which based on a) aspects and b) counted words from all parsed reviews
    newIteration() {
        if (this.countReviews === null) {
            const reviewsCounter = this.root.querySelector('[data-hook="cr-filter-info-review-rating-count"]');
            if (!reviewsCounter) {
                return;
            }
            this.countReviews = reviewsCounter.textContent.trim().replaceAll(',', '').match(/\d+/g)?.map(Number.parseFloat) || [0, 0];
        }
    }

    clickNextPage() {
        super.clickNextPage();
        try {
            const next = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
            if (!next) {
                return false;
            }
            next.scrollIntoView();
            next.click();
            return true;
        } catch (e) {
            return false;
        }
    }
}