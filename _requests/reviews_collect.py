import os
from bs4 import BeautifulSoup
from pandas import DataFrame
from selenium.common import WebDriverException, InvalidSessionIdException

from config import State, get_file_write_mode
from _requests.BaseRequest import BaseRequest, initialize, STATUS


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

    def processing(self, except_process=True):
        self.state['reviews_page'] = int(self.state['reviews_page'] or 1)
        req = ReviewsRequest(
            self.web_driver,
            asin=self.asin,
            filterByStar=self.stars,
            pageNumber=self.state['reviews_page']
        )
        req.send()
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
        for i in range(self.state['reviews_page'], pages + 1):
            req = ReviewsRequest(self.web_driver, asin=self.asin, filterByStar=self.stars, pageNumber=i)
            req.send(except_process)
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
        path = os.path.join(self.directory, f'reviews_list_{self.asin}.csv')
        wm = get_file_write_mode(os.path.join(self.directory, f'reviews_list_{self.asin}.csv'))
        df.to_csv(path, index=False, mode=wm, header=wm == 'w')


class ReviewsRequest(BaseRequest):
    url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt'
    params_auto_paste = True

    def __init__(self, webdriver, **kwargs):
        super().__init__(webdriver, start_url='https://www.amazon.com/s?k=computer&ref=nb_sb_noss')
        self.params = {
            'sortBy': 'helpful',
            'filterByStar': 'five_star',
            'scope': 'reviewsAjax3',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 13,
            'pageNumber': 1,
            **kwargs
        }

    def processing(self, count_reviews_only=False):
        raw_data = super().processing()
        if not raw_data:
            return False
        data_with_quantity = raw_data[1][2]
        parser = BeautifulSoup(data_with_quantity.replace('\"', '"'), features='html.parser')
        reviews_count_el = parser.find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
        if not reviews_count_el:
            return False
        reviews_count_raw = reviews_count_el.text.split('total ratings, ')
        if len(reviews_count_raw) == 1:
            reviews_count_raw = reviews_count_el.text.split('total rating, ')
        if len(reviews_count_raw) > 1:
            reviews_count = reviews_count_raw[1].replace(' with reviews', '').replace(',', '').strip()
            if 'with review' in reviews_count:
                reviews_count = reviews_count.replace(' with review', '')
            reviews_count = int(reviews_count)
        else:
            reviews_count = 0

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
                'Product Link': 'https://www.amazon.com/dp/' + self.params['asin'],
                'ASIN': self.params['asin'],
                'Review Created Date': review_date,
                'Review User Name': customer_name,
                'Review Title': review_title,
                'Review Body': review_body,
                'Review Rating': review_rating,
                'Review Helpful Votes': helpful_votes,
                'Product Options': review_options,
            })
        return reviews_count, data


selenium = None


def reviews_collect(folder, product_asin):
    global selenium
    thread = None
    stop_ev = None

    def close(status: object = 'error'):
        global selenium
        try:
            if selenium:
                selenium.close()
                selenium = None
        except InvalidSessionIdException:
            pass
        finally:
            if thread and stop_ev:
                stop_ev.set()
            if status:
                return STATUS[status]
    try:
        if not os.path.exists('./' + folder):
            os.mkdir(folder)
        # SETTINGS UP
        st = State(f'reviews_collect_{product_asin}__state.dat', directory=folder)
        start_star = int(st['current_star'] or 1)
        if start_star <= 5:
            # PREPARE
            selenium, thread, stop_ev = initialize(True)
            # sleep(5)
            thread.start()

            # processing
            for star in range(start_star, 6):
                incr = True
                try:
                    req = ReviewsPoolRequests(product_asin, star, selenium, folder, st)
                    req.processing(False)
                except KeyboardInterrupt:
                    return STATUS['closed']
                st['current_star'] = star + incr
                st['reviews_page'] = 1
                st.write()

            close(None)

        from uniqulizer import uniqulize_by_df

        if os.path.exists(os.path.join(folder, f'reviews_list_{product_asin}.csv')):
            uniqulize_by_df(
                os.path.join(folder, f'reviews_list_{product_asin}.csv'),
                os.path.join(folder, f'unique_reviews_list_{product_asin}.csv'),
                0
            )
        if os.path.exists(os.path.join(folder, f'unique_reviews_list_{product_asin}.csv')):
            os.unlink(os.path.join(folder, f'reviews_list_{product_asin}.csv'))
            os.rename(
                os.path.join(folder, f'unique_reviews_list_{product_asin}.csv'),
                os.path.join(folder, f'reviews_list_{product_asin}.csv')
            )
        return close('success')
    except KeyboardInterrupt:
        return close('closed')
    except WebDriverException:
        return close('reload')
    except Exception:
        return close('error')


if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    args_start_index = 1
    for i in sys.argv:
        if i == '--start':
            break
        args_start_index += 1
    folder = sys.argv[args_start_index]
    if len(sys.argv) > args_start_index + 1 and sys.argv[args_start_index + 1]:
        product = sys.argv[args_start_index + 1].strip()
        if len(product) != 10:
            print('error')
            sys.exit(0)
    else:
        print('error')
        sys.exit(0)

    res = reviews_collect(folder, product)
    if res == STATUS['success']:
        print('success')
    elif res == STATUS['error']:
        print('error')
    elif res == STATUS['closed']:
        print('closed')
