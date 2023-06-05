import os
from io import TextIOWrapper
from json import JSONDecoder
from time import sleep

from bs4 import BeautifulSoup
from pandas import DataFrame
from selenium.common import JavascriptException

from configuration import get_file_write_mode
from initialization import CustomSelenium


class Request:
    url = None
    params_auto_paste = False
    method = 'post'
    result = None

    def __init__(self, **kwargs):
        self.params = kwargs

    def params_to_str(self):
        return '?' + '&'.join('='.join(map(str, keyval)) for keyval in self.params.items())

    def send(self, web_driver: CustomSelenium):
        if not self.url:
            raise NotImplementedError('Please type the URL')
        try:
            web_driver.insert_jquery()
            sleep(1)
            if self.params_auto_paste:
                ajax = f"$.{self.method}(\"{self.url}\", " \
                       + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in self.params.items()]) + "\"}" \
                       + ", null, 'text');"
            else:
                ajax = f"$.{self.method}(\"{self.url}\", null, null, 'text');"
            result = web_driver.execute_script("return " + ajax)
            sleep(1)
            self.result: str = result
            return True
        except JavascriptException as e:
            print(e)
            return False

    def processing(self):
        if not self.result:
            return None
        decoder = JSONDecoder()
        return list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, self.result.strip().split('&&&'))))


class ProductsRequest(Request):
    @property
    def url(self):
        return 'https://www.amazon.com/s/query' + self.params_to_str()

    def __init__(self, directory, file, **kwargs):
        self.directory = directory
        self.file: TextIOWrapper = file
        kwargs = {'pageNumber': 1, 'scope': 'reviewsAjax0', 'reftag': 'cm_cr_arp_d_viewopt_sr', **kwargs}
        super().__init__(**kwargs)
        self.web_driver = kwargs.get('web_driver')

    def send(self, web_driver=None):
        if not self.web_driver:
            self.web_driver = web_driver
        return super().send(web_driver or self.web_driver)

    def processing(self):
        raw_data = super().processing()
        count_all_products = 0
        rows = [] if self.params.get('page') > 1 else ['asin,overall_rating,rating1,rating2,rating3,rating4,rating5\n']

        for item in raw_data:
            if count_all_products > 0 and count_all_products // 48 + 1 < self.params['pageNumber']:
                return count_all_products
            if 'data-search-metadata' in item[1]:
                count_all_products = item[2]['metadata']['totalResultCount']
            elif 'data-main-slot:search-result-' in item[1]:
                soup = BeautifulSoup(item[2]['html'], features="html.parser")
                overall_rating_el = soup.select_one(
                    '.a-size-small > span > .a-declarative[data-csa-c-func-deps="aui-da-a-popover"] span.a-icon-alt')
                if not overall_rating_el:
                    overall_rating = '0,0,0,0,0,0'
                else:
                    overall_rating = overall_rating_el.text.replace(' out of 5 stars', '').strip()
                    for i in range(1, 5):
                        r_request = ReviewsRequest(asin=item[2]['asin'], filterByStar=ReviewsPoolRequests.get_star(i))
                        r_request.send(self.web_driver)
                        overall_rating += ',' + str(r_request.processing(True))
                rows.append(item[2]['asin'] + ',' + str(overall_rating) + '\n')

        self.file.writelines(rows)

        return count_all_products


class ReviewsPoolRequests:
    def __init__(self, product_asin, reviews_stars, web_driver, directory, state):
        self.asin = product_asin
        self.stars = ReviewsPoolRequests.get_star(reviews_stars)
        self.web_driver = web_driver
        self.directory = directory
        self.state = state

    @staticmethod
    def get_star(n: int):
        return {1: 'one_star', 2: 'two_star', 3: 'three_star', 4: 'four_star', 5: 'five_star'}[max(1, min(5, n))]

    def processing(self):
        self.state['reviews_page'] = int(self.state['reviews_page'] or 1)
        req = ReviewsRequest(asin=self.asin, filterByStar=self.stars, pageNumber=self.state['reviews_page'])
        req.send(self.web_driver)
        r = req.processing()

        if not r:
            return
        quantity, data = r
        if not quantity:
            return

        pages = (quantity // 13) + 1
        if self.state['reviews_page'] > pages:
            return
        self.iter(data)
        self.state['reviews_page'] += 1
        self.state.write()
        for i in range(self.state['reviews_page'], pages):
            req = ReviewsRequest(asin=self.asin, filterByStar=self.stars, pageNumber=i)
            req.send(self.web_driver)
            r = req.processing()

            if not r:
                break
            q, data = r
            if not q:
                break

            self.iter(data)
            self.state['reviews_page'] = i + 1
            self.state.write()

    def iter(self, data):
        df = DataFrame(data)
        path = os.path.join(self.directory, 'reviews_list.csv')
        wm = get_file_write_mode('reviews_list.csv')
        df.to_csv(path, index=False, mode=wm, header=wm == 'w')


class ReviewsRequest(Request):
    url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt'
    params_auto_paste = True

    def __init__(self, **kwargs):
        kwargs = {
            'sortBy': 'helpful',
            'filterByStar': 'five_star',
            'scope': 'reviewsAjax3',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 13,
            'pageNumber': 1,
            **kwargs
        }
        super().__init__(**kwargs)

    def processing(self, count_reviews_only=False):
        raw_data = super().processing()
        data_with_quantity = raw_data[1][2]
        parser = BeautifulSoup(data_with_quantity.replace('\"', '"'), features='html.parser')
        reviews_count_el = parser.find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
        if not reviews_count_el:
            return False
        reviews_count_raw = reviews_count_el.text.split('total ratings, ')
        if len(reviews_count_raw) > 1:
            reviews_count = reviews_count_raw[1].replace(' with reviews', '').replace(',', '').strip()
            if 'with review' in reviews_count:
                reviews_count = reviews_count.replace(' with review', '')
            reviews_count = int(reviews_count)
        else:
            reviews_count = None

        if count_reviews_only:
            return reviews_count

        data = []

        for item in raw_data[6:]:
            if item[1] != "#cm_cr-review_list" or not item[2].strip():
                break
            item_parser = BeautifulSoup(item[2].strip(), features='html.parser')
            if item_parser.find('div', class_='a-divider-section') \
                    or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                continue
            # Date
            review_date = item_parser.find('span', attrs={'data-hook': 'review-date'})
            review_date = review_date.text.strip().replace("\n", " ") if review_date else ''
            # Customer name
            customer_name = item_parser.find('span', attrs={'class': 'a-profile-name'})
            customer_name = customer_name.text.strip().replace("\n", " ") if customer_name else ''
            # Title
            review_title = item_parser.find('a', attrs={'data-hook': 'review-title'})
            review_title = review_title.text.strip().replace("\n", " ") if review_title else ''
            # Content
            review_body = item_parser.find('span', attrs={'data-hook': 'review-body'})
            review_body = review_body.text.strip().replace("\n", " ") if review_body else ''
            # Rating
            review_star_rating = item_parser.find('i', {'data-hook': 'review-star-rating'})
            if not review_star_rating:
                review_star_rating = item_parser.find('i', {'data-hook': 'cmps-review-star-rating'})
            if not review_star_rating:
                review_star_rating = item_parser.find('i', class_='cr-lightbox-review-rating')
            if not review_star_rating:
                print(item_parser)
            review_rating = review_star_rating.find('span').text.split(' ')[0].strip()
            # Helpful votes
            helpful_votes = item_parser.find('span', {'data-hook': 'helpful-vote-statement'})
            if helpful_votes:
                helpful_votes = helpful_votes.text.split(' ')[0]
                if helpful_votes == 'One':
                    helpful_votes = 1
                else:
                    helpful_votes = int(helpful_votes.replace(',', ''))
            else:
                helpful_votes = 0
            # Options
            review_options = item_parser.find_all('a', {'data-hook': 'format-strip'})
            if review_options:
                review_options = '|'.join(map(lambda x: x.text, review_options)).replace("\n", " ")
            else:
                review_options = ''

            data.append({
                'product_url': 'https://www.amazon.com/dp/' + self.params['asin'],
                'asin': self.params['asin'],
                'date_info': review_date,
                'name': customer_name,
                'title': review_title,
                'content': review_body,
                'rating': review_rating,
                'helpful': helpful_votes,
                'options': review_options,
            })
        return reviews_count, data


class FeedbackRequest(Request):
    url = ''
    method = 'get'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
