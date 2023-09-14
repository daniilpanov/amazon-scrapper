import datetime
import os.path
import re
from builtins import Exception
from json import JSONDecoder, JSONEncoder, JSONDecodeError
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Union

from alive_progress import alive_bar

from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium.common import JavascriptException, InvalidSessionIdException, TimeoutException
from seleniumbase import BaseCase

from functions import RetryException, user_emulate, chrome_init, captcha_solve_modern

params = {
    'sortBy': ['helpful', 'recent'],
    'reviewerType': ['all_reviews', 'avp_only_reviews'],
    'filterByStar': ['all_stars', 'five_star', 'four_star', 'three_star', 'two_star', 'one_star'],
    'formatType': ['all_formats', 'current_format'],
    'mediaType': ['all_contents', 'media_reviews_only'],
    'pageNumber': list(range(1, 11)),
}
params_len = 1
for key in params:
    params_len *= len(params[key])
data_queue = Queue()
write_queue = Queue()
state_queue = Queue()
ev = Event()

webdriver: Union[None, BaseCase] = None
url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_srt'

jsd = JSONDecoder()
jse = JSONEncoder()

file_exists = os.path.exists('reviews_list.csv')
if file_exists:
    try:
        data = jsd.decode('\n'.join(list(open('state.json')))) if os.path.exists('state.json') else {}
    except JSONDecodeError:
        data = {}
else:
    data = {}


def state(asin, seed):
    global data
    data[asin] = seed
    return jse.encode(data)


def write_state(folder='.'):
    if not file_exists:
        f = open(os.path.join(folder, 'state.json'), 'w', encoding='utf-8')
        f.write('{}')
        f.close()
    while True:
        # Wait for a data from the queue
        state_data = state_queue.get()

        # Stop flag!
        if state_data is None:
            return

        asin, seed = state_data
        try:
            f = open(os.path.join(folder, 'state.json'), 'w', encoding='utf-8')
            f.write(state(asin, seed))
            f.close()
        except IOError:
            sleep(10)
            f = open(os.path.join(folder, 'state.json'), 'w', encoding='utf-8')
            f.write(state(asin, seed))
            f.close()


def write_data(folder='.'):
    if not file_exists:
        f = open(os.path.join(folder, 'reviews_list.csv'), 'w', encoding='utf-8')
        f.write('product_url,asin,date,country,name,title,content,rating,helpful,options\n')
        f.close()
    while True:
        # Wait for a data from the queue
        write_data_res = write_queue.get()

        # Stop flag!
        if write_data_res is None:
            state_queue.put(None)
            return

        asin, seed, write_data_res = write_data_res
        df = DataFrame(write_data_res, columns=[
            'product_url',
            'asin',
            'date',
            'country',
            'name',
            'title',
            'content',
            'rating',
            'helpful',
            'options',
        ])
        df.to_csv(os.path.join(folder, 'reviews_list.csv'), index=False, header=False, mode='a', encoding='utf-8')
        state_queue.put([asin, seed])


def process_data():
    months = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October', 'November', 'December']

    while True:
        # Wait for a data from the queue
        process_data_res = data_queue.get()

        # Stop flag!
        if process_data_res is None:
            write_queue.put(None)
            return

        asin, seed, process_data_res = process_data_res
        try:
            process_data_res = re.sub(r'\["script","if\(window\.ue\) \{[^]]+]', '', process_data_res.strip())
            try:
                raw = list(map(
                    lambda s: jsd.decode(s.strip()),
                    [i for i in process_data_res.splitlines() if i.strip() and '&&&' != i.strip()],
                ))
            except Exception as e:
                print(e)
                continue
            data_with_quantity = None
            for item in raw:
                if len(item) >= 3 and item[1] == '#filter-info-section':
                    data_with_quantity = item[2]
                    break
            if not data_with_quantity:
                continue
            parser = BeautifulSoup(data_with_quantity.replace('\"', '"'), features='html.parser')
            reviews_count_el = parser.find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
            if not reviews_count_el:
                continue
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

            res = []

            for item in raw:
                if len(item) < 3 or item[1] != "#cm_cr-review_list" or not item[2].strip():
                    continue
                item_parser = BeautifulSoup(item[2].strip(), features='html.parser')
                if not item_parser or not item_parser.find(attrs={'data-hook': 'review'}) \
                        or item_parser.find('div', class_='a-divider-section') \
                        or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                    continue
                # Country & Date
                review_date_raw = item_parser.find('span', attrs={'data-hook': 'review-date'})
                if review_date_raw:
                    review_date_raw = review_date_raw.text.replace("\n", " ").strip()
                    review_date_data, year = \
                        (review_date_raw[16:] if review_date_raw[12] == 't' else review_date_raw[12:]).split(', ')
                    year = int(year)
                    review_country, review_date = review_date_data.split(' on ')
                    month, day = review_date.split(' ')
                    month = months.index(month) + 1
                    day = int(day)
                    review_date = f'{year}-{month:02}-{day:02}'
                else:
                    review_date = ''
                    review_country = ''
                # Customer name
                customer_name = item_parser.find('span', attrs={'class': 'a-profile-name'})
                customer_name = customer_name.text.strip().replace("\n", " ") if customer_name else ''
                # Title
                review_title = item_parser.find('a', attrs={'data-hook': 'review-title'})
                if review_title:
                    review_title = review_title.text.strip().replace("\n", " ").split('.0 out of 5 stars ')
                    review_title = review_title[1] if len(review_title) > 1 else ''
                else:
                    review_title = ''
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

                # data.append({
                #     'Product Link': 'https://www.amazon.com/dp/' + self.params['asin'],
                #     'ASIN': self.params['asin'],
                #     'Review Created Date': review_date,
                #     'Country': review_country,
                #     'Review User Name': customer_name,
                #     'Review Title': review_title,
                #     'Review Body': review_body,
                #     'Review Rating': review_rating,
                #     'Review Helpful Votes': helpful_votes,
                #     'Product Options': review_options,
                # })
                # product_url,asin,date_info,name,title,content,rating,helpful,options
                res.append({
                    'product_url': 'https://www.amazon.com/dp/' + asin,
                    'asin': asin,
                    'date': review_date,
                    'country': review_country,
                    'name': customer_name,
                    'title': review_title,
                    'content': review_body,
                    'rating': review_rating,
                    'helpful': helpful_votes,
                    'options': review_options,
                })
            write_queue.put([asin, seed, res])
        except Exception as ex:
            print(ex)


def send_request(asin, seed):
    if seed < params_len:
        current_params = {
            'scope': 'reviewsAjax3',
            'reftag': 'cm_cr_arp_d_viewopt_srt',
            'pageSize': 13,
            'asin': asin,
        }
        s = seed
        for i in params:
            length = len(params[i])
            current_params[i] = params[i][s % length]
            s //= length

        ajax = f"$.post(\"{url}\", " \
               + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in current_params.items()]) + "\"}" \
               + ", null, 'text');"

        try:
            res = webdriver.execute_script("return " + ajax)
            if not res or 'BAAAAAAD ASIN!' in res:
                raise RetryException()
        except (JavascriptException, RetryException, TimeoutException):
            print('something went wrong. retry... ')
            sleep(1)
            try:
                webdriver.reload()
                if not captcha_solve_modern(webdriver):
                    raise Exception()
                webdriver.reload()
                webdriver.activate_jquery()
                res = webdriver.execute_script("return " + ajax)
                if not res or 'BAAAAAAD ASIN!' in res:
                    raise Exception()
                print('success. continue')
            except Exception as e:
                print('error')
                print(e)
                try:
                    webdriver.driver.close()
                finally:
                    data_queue.put(None)
                    return False

        data_queue.put([asin, seed, res])
    else:
        data_queue.put(None)
    return True


def main(ASINs, folder='.'):
    # timestamp
    start_time = datetime.datetime.now()
    print('loading webdriver')
    global webdriver, ev, file_exists

    file_exists = os.path.exists(os.path.join(folder, 'reviews_list.csv'))

    ev = Event()
    webdriver = chrome_init(modern=True)

    user_emulate_thread = Thread(target=user_emulate, args=(webdriver, ev), daemon=True)
    process_thread = Thread(target=process_data)
    writer_thread = Thread(target=write_data, args=(folder,))
    state_writer_thread = Thread(target=write_state, args=(folder,))
    user_emulate_thread.start()
    process_thread.start()
    writer_thread.start()
    state_writer_thread.start()

    index = 0
    try:
        if type(ASINs) is dict:
            for brand in ASINs:
                for asin in ASINs[brand]:
                    asin = asin[0]
                    if asin in data:
                        if data[asin] >= params_len - 1:
                            continue
                        index = data[asin]
                    print('COLLECTING REVIEWS FOR ASIN', asin + ':')
                    with alive_bar(params_len, bar='classic') as bar:
                        bar(index, skipped=True)
                        for params_seed in range(index, params_len):
                            send_request(asin, params_seed)
                            bar()
                    index = 0
        elif type(ASINs) is list:
            for asin in ASINs:
                if asin in data:
                    if data[asin] >= params_len - 1:
                        continue
                    index = data[asin]
                print('COLLECTING REVIEWS FOR ASIN', asin + ':')
                with alive_bar(params_len, bar='classic') as bar:
                    bar(index, skipped=True)
                    for params_seed in range(index, params_len):
                        send_request(asin, params_seed)
                        bar()
                index = 0
        print('wait for writing the data...')
        data_queue.put(None)
        process_thread.join()
        writer_thread.join()
        state_writer_thread.join()
        print('DONE.')
        return start_time, datetime.datetime.now()
    except (InvalidSessionIdException, RetryException) as e:
        print('ERROR: invalid session. Program will be restarted')
        print('wait for writing the data...')
        data_queue.put(None)
        ev.set()
        user_emulate_thread.join()
        process_thread.join()
        writer_thread.join()
        state_writer_thread.join()
        print('done. reloading...')
        sleep(10)
        return main(ASINs, folder)
    except KeyboardInterrupt:
        print('Script stopped')
        data_queue.put(None)
        return start_time, datetime.datetime.now()
    finally:
        try:
            webdriver.driver.close()
        except:
            pass

