import os.path
import random
from builtins import Exception
from json import JSONDecoder, JSONEncoder, JSONDecodeError
from queue import Queue
from threading import Thread, Event
from time import sleep
from alive_progress import alive_bar

import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import OperatingSystem, SoftwareName
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException, WebDriverException, JavascriptException, InvalidSessionIdException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import ChromeOptions, Chrome
from selenium.webdriver.support import expected_conditions as EC

from google_sheets import get_asins, write_reviews_data

try:
    import tensorflow
    from captcha_solver.solve_captcha_with_model import CaptchaSolver
    captchaAI = True
except ImportError as e:
    CaptchaSolver = None
    captchaAI = False


def captcha_check(just_check=False):
    wait_for_loading()
    insert_jquery()
    try:
        captcha = webdriver.find_element(
            By.CSS_SELECTOR,
            'div.a-box.a-alert.a-alert-info.a-spacing-base > div.a-box-inner > h4',
        )
        if just_check:
            return captcha.text == 'Enter the characters you see below'
        if captcha and captcha.text == 'Enter the characters you see below':
            buttons = webdriver.find_elements(By.CSS_SELECTOR, 'a[onclick="window.location.reload()"]')
            for button in buttons:
                if button.text == 'Try different image':
                    button.click()
                    sleep(1)
                    return captcha_check(True)
        return True
    except:
        return False


def captcha_solve(retry=10):
    if captcha_check():
        if not captchaAI:
            sleep(15)
            return captcha_check(True)
        wait_for_loading()
        sleep(1)
        captcha = webdriver.find_element(By.CSS_SELECTOR, 'img[src]')
        img_source = requests.get(captcha.get_attribute('src'))
        if not img_source:
            return False
        if not os.path.exists(os.path.join('.', 'tmp')):
            os.makedirs('tmp')
        filepath = os.path.join('tmp', 'captcha.jpg')
        counter = 0
        while os.path.exists(filepath):
            filepath = os.path.join('tmp', f'captcha{counter}.jpg')
            counter += 1
        file = open(filepath, 'wb')
        file.write(img_source.content)
        file.close()
        solver = CaptchaSolver('captcha_solver')
        text = solver.solve(filepath)
        os.remove(filepath)
        if not text:
            return False
        input_element = webdriver.find_element(value='captchacharacters')
        for symbol in text:
            input_element.send_keys(symbol)
            sleep(random.randint(0, 2))
        input_element.send_keys(Keys.ENTER)
        sleep(1)
        wait_for_loading()
        insert_jquery()
        if captcha_check():
            if retry:
                return captcha_solve(retry - 1)
            return False
    return True


def wait_for_loading(p=None, by=By.CSS_SELECTOR):
    if not p:
        p = 'html'
        by = By.TAG_NAME
    try:
        WebDriverWait(webdriver, 10000).until(EC.presence_of_element_located((by, p)))
        return True
    except WebDriverException:
        return False


def insert_jquery():
    try:
        webdriver.find_element(value='JQUERY_ELEMENT_SCRIPT')
    except NoSuchElementException:
        webdriver.execute_script("""
        var jq = document.createElement('script');
        jq.id = 'JQUERY_ELEMENT_SCRIPT';
        jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
        document.getElementsByTagName('head')[0].appendChild(jq);
        """)
        sleep(3)


def user_emulate():
    try:
        while not ev.is_set():
            action = ActionChains(webdriver)
            webdriver.execute_script("document.body.focus();")
            for i in range(random.randint(20, 50)):
                action.scroll_by_amount(0, random.randint(-4, 4) * 10).perform()
                sleep(0.2)
            if not random.randint(0, 5):
                action.send_keys(Keys.PAGE_DOWN).perform()
            sleep(random.randint(5, 15))
    except Exception as ex:
        print('User emulation is stopped because of this error:', ex)
        return


class RetryException(Exception):
    pass


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

webdriver = None
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


def write_state():
    with open('state.json', 'w+', encoding='utf-8') as f:
        f.write(jse.encode(data))
        while True:
            # Wait for a data from the queue
            state_data = state_queue.get()

            # Stop flag!
            if state_data is None:
                return

            asin, seed = state_data

            f.seek(0)
            f.write(state(asin, seed))


def write_data():
    with open('reviews_list.csv', 'a' if file_exists else 'w', encoding='utf-8') as f:
        if not file_exists:
            f.write('product_url,asin,date_info,name,title,content,rating,helpful,options\n')
        while True:
            # Wait for a data from the queue
            write_data_res = write_queue.get()

            # Stop flag!
            if write_data_res is None:
                state_queue.put(None)
                return

            asin, seed, write_data_res = write_data_res

            for item in write_data_res:
                f.write(','.join(map(str, item.values())) + '\n')

            state_queue.put([asin, seed])


def process_data():
    while True:
        # Wait for a data from the queue
        process_data_res = data_queue.get()

        # Stop flag!
        if process_data_res is None:
            write_queue.put(None)
            return

        asin, seed, process_data_res = process_data_res

        raw = list(map(lambda s: jsd.decode(s.strip()), filter(lambda x: x, process_data_res.strip().split('&&&'))))
        data_with_quantity = raw[1][2]
        parser = BeautifulSoup(data_with_quantity.replace('\"', '"'), features='html.parser')
        reviews_count_el = parser.find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
        if not reviews_count_el:
            return None
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

        for item in raw[6:]:
            if item[1] != "#cm_cr-review_list" or not item[2].strip():
                break
            item_parser = BeautifulSoup(item[2].strip(), features='html.parser')
            if item_parser.find('div', class_='a-divider-section') \
                    or item_parser.find('h3', attrs={'data-hook': 'dp-global-reviews-header'}):
                continue
            # Country & Date
            review_date_raw = item_parser.find('span', attrs={'data-hook': 'review-date'})
            if review_date_raw:
                review_date_raw = review_date_raw.text.strip()
                review_date = review_date_raw.replace("\n", " ") \
                    .replace('Reviewed in the ', '').replace(',', '').replace('"', '')
                rdc = review_date.split(' on ')
                review_date = rdc[-1]
                review_country = ' on '.join(rdc[:-1])
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
                'date_info': review_date_raw,
                'name': customer_name,
                'title': review_title,
                'content': review_body,
                'rating': review_rating,
                'helpful': helpful_votes,
                'options': review_options,
            })

        write_queue.put([asin, seed, res])


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
        print(ajax)

        try:
            res = webdriver.execute_script("return " + ajax)
            if not res or 'BAAAAAAD ASIN!' in res:
                print('something went wrong')
                raise RetryException()
        except (JavascriptException, RetryException):
            try:
                wait_for_loading()
                insert_jquery()
                res = webdriver.execute_script("return " + ajax)
                if not res or 'BAAAAAAD ASIN!' in res:
                    print('error')
                    raise Exception()
            except Exception as e:
                print(e)
                try:
                    webdriver.close()
                except:
                    pass
                return False

        data_queue.put([asin, seed, res])
    else:
        data_queue.put(None)
    return True


def main():
    print('loading webdriver')
    global webdriver, ev, file_exists

    file_exists = os.path.exists('reviews_list.csv')

    ev = Event()
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
    )
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--log-level=3')
    webdriver = Chrome(options=options)
    webdriver.get('https://www.amazon.com/product-reviews/B08JPS4554')
    wait_for_loading()
    captcha_solve()

    user_emulate_thread = Thread(target=user_emulate, daemon=True)
    process_thread = Thread(target=process_data)
    writer_thread = Thread(target=write_data)
    state_writer_thread = Thread(target=write_state)
    user_emulate_thread.start()
    process_thread.start()
    writer_thread.start()
    state_writer_thread.start()

    ASINs = get_asins()
    index = 0
    try:
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
    except (InvalidSessionIdException, RetryException):
        print('ERROR: invalid session. Program will be restarted')
        sleep(1000)
        print('wait for writing the data...')
        data_queue.put(None)
        ev.set()
        user_emulate_thread.join()
        process_thread.join()
        writer_thread.join()
        state_writer_thread.join()
        print('done. reloading...')
        sleep(10)
        main()


# Mainloop
if __name__ == '__main__':
    print('PROGRAM STARTED')
    try:
        main()
        from uniqulizer import uniqulize_by_df
        uniqulize_by_df('reviews_list.csv', 'output_reviews_list.csv', 0)
        write_reviews_data()
    except KeyboardInterrupt:
        print('STOP')
        data_queue.put(None)
