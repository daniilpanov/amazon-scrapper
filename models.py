# -*- coding: utf-8 -*-
from pandas import DataFrame
import logging
import os.path
import random
import re
import typing
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementNotInteractableException, \
    JavascriptException
from selenium.webdriver.common.by import By

from config import r

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import OperatingSystem, SoftwareName
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import IGNORED_CHAR


# wrapper for selenium instance
from config import WEBDRIVER_PATH, state, defaultstate


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
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument(f'user-agent={self.user_agents.get_random_user_agent()}')
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
        except ElementNotInteractableException:
            return
        except JavascriptException:
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

        self.browser.maximize_window()
        body = self.get_element(By.TAG_NAME, 'body', False)
        for i in range(1, 3):
            body.send_keys(Keys.PAGE_DOWN)
            sleep(1)

        body.send_keys(Keys.PAGE_UP)
        sleep(1)
        body.send_keys(Keys.PAGE_UP)
        sleep(2)

    def get_element(self, criteria, element, wait=True):
        if wait:
            self.wait(criteria, element)
        return self.browser.find_element(criteria, element)

    def get_html(self, criteria=None, element=None):
        if criteria and element:
            self.wait(criteria, element)
        page_html = self.browser.page_source
        return page_html

    def get(self, url):
        self.browser.get(url)


class ProductFull:
    def __init__(self, **kwargs):
        self.reviews: typing.Union[ReviewsFull, None] = None
        # HTML parsing
        self.browser: AmazonRequest = kwargs.get('browser')
        html = self.html = BeautifulSoup(self.browser.get_html(By.ID, 'title'), features='html.parser')
        self.title = html.find('h1', id='title')
        self.url = '/'.join(kwargs.get('url').split('/')[:-1])
        self.asin = self.url.split('/')[5]
        self.alias = self.url.split('/')[3]
        self.category = kwargs.get('category') or None
        self.page = kwargs.get('page') or None

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
        button_reviews = self.browser.get_element(By.CSS_SELECTOR, '[data-hook="see-all-reviews-link-foot"]')
        self.browser.browser.execute_script('arguments[0].scrollIntoView(true);', button_reviews)
        sleep(2)
        self.browser.hover(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a')
        sleep(2)
        button_reviews.click()

    def reviews_collect(self):
        self.reviews = ReviewsFull(
            url="https://www.amazon.com/"
                + self.alias + "/product-reviews/"
                + self.asin + "?pageNumber="
                + str(defaultstate['reviews_page'] if int(defaultstate['reviews_page']) > 0 else '1'),
            product_url=self.url,
            product_asin=self.asin,
            reviews_page=int(defaultstate['reviews_page']) if int(defaultstate['reviews_page']) > 0 else 1,
            browser=self.browser,
            page=self.page
        )

    def get_data(self):
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


class ReviewsFull:
    def __init__(self, **kwargs):
        self.browser: AmazonRequest = kwargs.get('browser')
        self.product_url = kwargs.get('product_url') or 'Unknown'
        self.product_asin = kwargs.get('product_asin') or 'Unknown'
        page = self.page = kwargs.get('reviews_page') or 1

        if page > 1:
            url = self.browser.browser.current_url
            if 'pageNumber=1' not in url:
                url += ('&' if '?' in url else '?') + 'pageNumber=' + str(page)
            else:
                url = url.replace('pageNumber=1', 'pageNumber=' + str(page))
            self.browser.get(url)
            self.browser.wait(By.CSS_SELECTOR, 'h3[data-hook*="local-reviews-header"]')

        logging.info('Loading product reviews URL: {}'.format(self.product_url))
        # HTML parsing
        while True:
            html = self.html = BeautifulSoup(self.browser.get_html(By.CLASS_NAME, 'view-point'), features='html.parser')
            self.reviews_block = html.find('div', id='cm_cr-review_list')
            self.reviews = []
            reviews_blocks = self.reviews_block.find_all('div', {'data-hook': 'review'})
            for review_block in reviews_blocks:
                self.reviews.append(ReviewBlock(review_block, self.product_url, self.product_asin))

            self.to_csv(kwargs.get('dirname') or datetime.now().strftime('%Y-%m-%d'), r)

            if not self.click_next():
                break

    def click_next(self):
        el = self.browser.get_element(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a')
        if not el:
            return False

        body = self.browser.get_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.PAGE_DOWN)
        sleep(1)
        body.send_keys(Keys.PAGE_UP)
        sleep(2)
        self.browser.browser.execute_script('arguments[0].scrollIntoView(true);', el)
        sleep(2)
        self.browser.hover(By.CSS_SELECTOR, '.a-last:not(.a-disabled) > a')
        sleep(2)
        # self.url = self.url.replace('pageNumber=' + str(self.page), 'pageNumber=' + str(self.page + 1))
        # self.browser.get(self.url)
        self.page += 1
        state(reviews_page=self.page)
        el.click()
        sleep(2)
        sleep(random.randint(3, 5))
        return True

    def get_data(self):
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
        html = str(html)
        html = re.sub(IGNORED_CHAR, '', html)
        html = BeautifulSoup(html, features='html.parser')
        self.html = html
        self.product_url = url
        self.product_asin = asin

        # 1. title
        self.title = html.find("a", class_="review-title").text.strip()
        # 2. name
        self.name = html.find('span', class_='a-profile-name').text.strip()
        # 3. rating
        self.rating = html.find("i", {"data-hook": "review-star-rating"}).find('span').text.split(' ')[0].strip()
        # 4. date
        self.date = html.find("span", {"data-hook": "review-date"}).text.strip()
        # 5. content
        review_body = html.find("span", {"data-hook": "review-body"}).find('span')
        self.content = \
            re.sub(' +', ' ', ". ".join(review_body.get_text("\n").strip().splitlines())).strip() if review_body\
            else "<images>"
        # 6. quantity of people who find this review helpful
        self.votes = html.find("span", {"data-hook": "helpful-votes-statement"})
        if self.votes:
            self.votes = self.votes.text.split(' ')[0]
            if self.votes == 'One':
                self.votes = 1
        else:
            self.votes = 0
        # 7. options
        self.options = html.find_all("a", {"data-hook": "format-strip"})
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
