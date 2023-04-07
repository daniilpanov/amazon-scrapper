# -*- coding: utf-8 -*-
from argparse import ArgumentError

from pandas import DataFrame
import logging
import os.path
import random
import re
import typing
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementNotInteractableException, \
    JavascriptException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from MustBeReloadedException import MustBeReloadedException
from config import r, HEADLESS

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import OperatingSystem, SoftwareName
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import IGNORED_CHAR


# wrapper for selenium instance
from config import WEBDRIVER_PATH, state


class AmazonRequest:
    # system data
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value,
                         OperatingSystem.LINUX.value]
    user_agents = UserAgent(software_names=software_names,
                            operating_systems=operating_systems, limit=120)
    options = webdriver.ChromeOptions()

    def __init__(self, **kwargs):
        self.browser: typing.Union[None, WebDriver] = None
        self.retries = 0
        self.driver_path = WEBDRIVER_PATH
        self.max_retries = kwargs.get('max_retries') or 5
        url = kwargs.get('url')
        self.options.add_argument(kwargs.get('window_size') or '--window-size=1920,1080')
        self.options.add_argument('--start-maximized')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        if HEADLESS:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument(f'user-agent={self.user_agents.get_random_user_agent()}')
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument('--ignore-ssl-errors')
        self.init(url)

    def init(self, url):
        self.browser = webdriver.Chrome(self.driver_path, chrome_options=self.options)
        self.browser.get(url)
        sleep(2)

    def hover(self, criteria, element):
        try:
            element_to_hover_over = self.browser.find_element(criteria, element)
            hover = ActionChains(self.browser).move_to_element(element_to_hover_over)
            hover.perform()
        except (ElementNotInteractableException, JavascriptException, NoSuchElementException):
            return
        except Exception as ex:
            print(type(ex).__name__, element)

    def wait(self, criteria, element):
        try:
            WebDriverWait(self.browser, 50) \
                .until(EC.presence_of_element_located((criteria, element)))
        except (WebDriverException, TimeoutException):
            self.retries += 1
            self.browser.quit()
            sleep(random.randint(1, 6))
            self.init(self.browser.current_url)

            if not self.retries > self.max_retries:
                self.wait(criteria, element)
            else:
                sleep(5)
                raise MustBeReloadedException

        self.browser.maximize_window()
        body = self.get_element(By.TAG_NAME, 'body', False)
        for i in range(1, 3):
            body.send_keys(Keys.PAGE_DOWN)
            sleep(1)

        body.send_keys(Keys.PAGE_UP)
        sleep(1)
        body.send_keys(Keys.PAGE_UP)
        sleep(2)

    def get_element(self, criteria, element, wait=True) -> typing.Union[WebElement, None]:
        try:
            if wait:
                self.wait(criteria, element)
            return self.browser.find_element(criteria, element)
        except NoSuchElementException:
            return None

    def get_html(self, criteria=None, element=None) -> str:
        if criteria and element:
            self.wait(criteria, element)
        page_html = self.browser.page_source
        return page_html

    def get(self, url):
        self.browser.get(url)


class ProductFull:

    reviews_count = 0

    def __init__(self, **kwargs):
        self.browser: AmazonRequest = kwargs.get('browser')
        self.category = kwargs.get('category') or None
        self.page = kwargs.get('page') or None
        self.dirname = kwargs.get('dirname') or None
        self.url = '/'.join(kwargs.get('url').split('/')[:-1])
        self.asin = self.url.split('/')[5]
        self.alias = self.url.split('/')[3]
        self.reviews: typing.Union[ReviewsFull, None] = None
        # HTML parsing
        html = self.html = BeautifulSoup(self.browser.get_html(By.ID, 'title'), features='html.parser')
        # title
        self.title = html.find('h1', id='title')
        # bullets
        self.bullet = ''
        feature_bullets = html.find('div', id='feature-bullets')
        # remove the replacement message if it exists
        replace_msg = feature_bullets.find('li', id='replacementPartsFitmentBullet')
        if not isinstance(replace_msg, type(None)):
            replace_msg.decompose()

        for item in feature_bullets.findAll('span', attrs={'class': 'a-list-item'}):
            self.bullet += ''.join((item.text.strip().replace('\n', ''), '\n'))

        # description
        self.bullet = re.sub(IGNORED_CHAR, '', self.bullet)
        self.desc = html.find('div', id='productDescription')
        # #look for product description containing images and text
        if isinstance(self.desc, type(None)):
            self.desc = html.find('div', class_='aplus-v2 desktop celwidget')

        if isinstance(self.desc, type(None)):
            self.desc = ''
        else:
            self.desc = self.desc.find('p').text.strip()
        # rating
        self.overall_rating = html.find('span', id='acrPopover').attrs['title'].split(' ')[0]
        self.ratings_count = html.find('span', id='acrCustomerReviewText').text.split(' ')[0]
        # group
        self.group = ' '.join(
            html.find('div', id='wayfinding-breadcrumbs_feature_div').text.strip().replace('\n', ' ').split()
        )
        # images
        self.image_urls = [elem.find('img').attrs['src'].replace('SX466', 'SX679') for elem in
                           html.findAll('div', attrs={'class': 'imgTagWrapper'}) if elem.find('img')]
        self.image_urls = {f'image_url_{i + 1}': e for i, e in enumerate(self.image_urls[:6])}
        # log
        logging.info('Loading product URL: {}'.format(self.url))
        self.browser.hover(By.XPATH, f'//*[@id="a-autoid-1"]')
        state(product_url=self.url)

    def reviews_collect(self):
        # goto reviews page
        button_reviews = self.browser.get_element(By.CSS_SELECTOR, '[data-hook="see-all-reviews-link-foot"]')
        self.browser.browser.execute_script('arguments[0].scrollIntoView(true);', button_reviews)
        sleep(1)
        self.browser.hover(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a')
        sleep(1)
        button_reviews.click()
        # wait for load...
        self.browser.wait(By.CSS_SELECTOR, 'h3[data-hook*="reviews-header"]')
        # reviews count
        reviews_count_raw = BeautifulSoup(self.browser.browser.page_source, features='html.parser')\
            .find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
        if reviews_count_raw:
            reviews_count_raw = reviews_count_raw.text.split('total ratings, ')
            if len(reviews_count_raw) > 1:
                self.reviews_count = int(reviews_count_raw[1].replace(' with reviews', '').replace(',', '').strip())
        # collect all
        # if more than 5k uses the filter trick
<<<<<<< Updated upstream
        if self.reviews_count > 5000:
=======
        if self.reviews_count > 5000 or bool(state()['filtered']):
            if int(state()['rating']) > 5:
                state(filtered=1, rating=5)
            else:
                state(filtered=1)
>>>>>>> Stashed changes
            self.reviews = FilteredReviews(
                product=self,
                reviews_page=state()['reviews_page'],
                state=bool(int(state()['current_state'])),
            )
        # else this trick is redundant
        else:
            self.reviews = ReviewsFull(
                product=self,
                reviews_page=state()['reviews_page'],
                state=bool(int(state()['current_state'])),
            )
        print('Reviews collected!')

    def get_data(self) -> dict:
        return {
            'url': self.url,
            'asin': self.asin,
            'name': self.title,
            'category': self.category,
            'short_description': self.bullet,
            'images': self.image_urls,
            'product_description': self.desc,
            # 'reviews': self.reviews.get_data(),
            'overall_rating': self.overall_rating,
            'ratings_count': self.ratings_count,
            'group': self.group,
        }

    def to_csv(self, direct, mode='a'):
        # f = open(os.path.join(direct, 'products.csv'), mode=mode)
        # data = self.get_data()
        # # del data['reviews']
        # csv.writer(f).writerows(data)
        # f.close()
        pass


class FilteredReviews:
    def __init__(self, **kwargs):
        # get all data
        self.product: ProductFull = kwargs.get('product')
        if not self.product:
            raise ArgumentError
        self.browser: AmazonRequest = self.product.browser
        self.page = kwargs.get('reviews_page') or None
        self.state = kwargs.get('state') or False
        self.page = self.browser.browser.current_url
        self.current_star = int(state()['rating']) or 6
        self.reviews_list: list[ReviewsFull] = []

        self.browser.wait(By.CSS_SELECTOR, 'h3[data-hook*="reviews-header"]')

        filter_params_id_pattern = 'star-count-dropdown_{}'
        filter_button = self.browser.get_element(By.ID, 'a-autoid-5-announce')
        for i in range(6 - self.current_star, 6):
            state(rating=6 - i)
            self.browser.browser.execute_script('arguments[0].scrollIntoView(true);', filter_button)
            sleep(1)
            filter_button.click()
            sleep(1)
            el = self.browser.get_element(By.ID, filter_params_id_pattern.format(i), True)
            sleep(1)
            hover = ActionChains(self.browser.browser).move_to_element(el)
            hover.perform()
            sleep(1)
            el.click()
            sleep(1)
            self.reviews_list.append(ReviewsFull(
                product=self.product,
                reviews_page=state()['reviews_page'],
                state=bool(int(state()['current_state'])),
            ))
            state(reviews_page='', current_state=0)


class ReviewsFull:
    def __init__(self, **kwargs):
        # get all data
        self.product: ProductFull = kwargs.get('product')
        if not self.product:
            raise ArgumentError
        self.browser: AmazonRequest = self.product.browser
        # link to the current page
        page = self.page = kwargs.get('reviews_page') or None
        # state: has data written or not?
        self.state = kwargs.get('state') or False

        # gets url and update it when it is not current page's url
        url = self.browser.browser.current_url
        if page and url != page:
            self.browser.get(page)
        # then wait for loading
        self.browser.wait(By.CSS_SELECTOR, 'h3[data-hook*="reviews-header"]')
        # if data is written, and we can not click next, we close the reviews collecting
        if self.state and not self.click_next():
            return

        logging.info('Loading product reviews URL: {}'.format(self.product.url))
        # HTML parsing
        while True:
            sleep(1)
            self.page = self.browser.browser.current_url
            print(self.page)
            # The data is not written now
            self.state = False
            # updates the state file
            state(reviews_page=self.page, current_state=0)
            # gets HTML code
            html = self.html = BeautifulSoup(self.browser.get_html(By.CLASS_NAME, 'view-point'), features='html.parser')
            # gets block with all reviews inside
            self.reviews_block = html.find('div', id='cm_cr-review_list')
            self.reviews = []
            # gets all reviews blocks
            reviews_blocks = self.reviews_block.find_all('div', {'data-hook': 'review'})
            for review_block in reviews_blocks:
                # adds data
                self.reviews.append(ReviewBlock(review_block, self.product.url, self.product.asin))
            # writes data
            self.to_csv(self.product.dirname or datetime.now().strftime('%Y-%m-%d'), r)
            # updates state
            state(reviews_page=self.page, current_state=1)
            self.state = True
            # if it is end, exit the loop
            if not self.click_next():
                break

    def click_next(self) -> bool:
        """
        This function uses for click next button
        :rtype: bool (able to click next)
        """
        el = self.browser.get_element(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a', False)
        if not el:
            return False

        body = self.browser.get_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.PAGE_DOWN)
        sleep(1)
        body.send_keys(Keys.PAGE_UP)
        sleep(1)
        self.browser.browser.execute_script('arguments[0].scrollIntoView(true);', el)
        sleep(1)
        self.browser.hover(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a')
        sleep(1)
        el.click()
        sleep(random.randint(2, 4))
        return True

    def get_data(self) -> DataFrame:
        return DataFrame(
            map(lambda x: x.get_data().values(), self.reviews),
            columns=list(self.reviews[0].get_data().keys()),
        )

    def to_csv(self, direct, mode):
        self.get_data().to_csv(
            os.path.join(direct, 'reviews.csv'),
            index=False,
            mode=mode(),
            header=mode() == 'w',
        )


class ReviewBlock:
    def __init__(self, html, url, asin):
        # HTML parsing
        html = str(html)
        html = re.sub(IGNORED_CHAR, '', html)
        html = BeautifulSoup(html, features='html.parser')
        self.html = html
        self.product_url = url
        self.product_asin = asin

        # 1. title
        self.title = html.find(class_="review-title").text.strip()
        # 2. name
        self.name = html.find(class_='a-profile-name').text.strip()
        # 3. rating
        review_star_rating = html.find('i', {'data-hook': 'review-star-rating'})
        if not review_star_rating:
            review_star_rating = html.find('i', {'data-hook': 'cmps-review-star-rating'})
        self.rating = review_star_rating.find('span').text.split(' ')[0].strip()
        # 4. date
        self.date = html.find('span', {'data-hook': 'review-date'}).text.strip()
        # 5. content
        review_body = html.find('span', {'data-hook': 'review-body'}).find('span')
        self.content = \
            re.sub(' +', ' ', '. '.join(review_body.get_text("\n").strip().splitlines())).strip() if review_body\
            else '<images>'
        # 6. quantity of people who find this review helpful
        self.votes = html.find('span', {'data-hook': 'helpful-votes-statement'})
        if self.votes:
            self.votes = self.votes.text.split(' ')[0]
            if self.votes == 'One':
                self.votes = 1
        else:
            self.votes = 0
        # 7. options
        self.options = html.find_all('a', {'data-hook': 'format-strip'})
        if self.options:
            self.options = '|'.join(map(lambda x: x.text, self.options))
        else:
            self.options = ''

    def get_data(self) -> dict:
        return {
            'product_url': self.product_url,
            'asin': self.product_asin,
            'date_info': self.date,
            'name': self.name,
            'title': self.title,
            'content': self.content,
            'rating': self.rating,
            'helpful': self.votes,
            'options': self.options,
        }
