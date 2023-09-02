import os
import random
from time import sleep

import requests
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium.common import WebDriverException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome, ChromeOptions

try:
    import tensorflow
    from captcha_solver.solve_captcha_with_model import CaptchaSolver

    captchaAI = True
except ImportError as e:
    CaptchaSolver = None
    captchaAI = False


def captcha_check(webdriver, just_check=False):
    wait_for_loading(webdriver)
    insert_jquery(webdriver)
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
                    return captcha_check(webdriver, True)
        return True
    except:
        return False


def captcha_solve(webdriver, retry=10):
    if captcha_check(webdriver):
        if not captchaAI:
            sleep(15)
            return captcha_check(webdriver, True)
        wait_for_loading(webdriver)
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
        wait_for_loading(webdriver)
        insert_jquery(webdriver)
        if captcha_check(webdriver):
            if retry:
                return captcha_solve(webdriver, retry - 1)
            return False
    return True


def wait_for_loading(webdriver, p=None, by=By.CSS_SELECTOR):
    if not p:
        p = 'html'
        by = By.TAG_NAME
    try:
        WebDriverWait(webdriver, 10000).until(EC.presence_of_element_located((by, p)))
        return True
    except WebDriverException:
        return False


def insert_jquery(webdriver):
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


def user_emulate(webdriver, ev):
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


def chrome_init():
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
    )
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--log-level=3')
    webdriver = Chrome(options=options)
    webdriver.get('https://www.amazon.com/product-reviews/B08JPS4554')
    wait_for_loading(webdriver)
    captcha_solve(webdriver)
    return webdriver
