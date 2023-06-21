import logging
import os
import random
from json import JSONDecoder
from threading import Event
from time import sleep

import requests
from selenium import webdriver
from selenium.common import WebDriverException, JavascriptException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

captchaAI = True
try:
    import tensorflow
    from captcha_solver.solve_captcha_with_model import CaptchaSolver
except ImportError:
    captchaAI = False


def initialize(simulate_user=False):
    try:
        from random_user_agent.user_agent import UserAgent
        from random_user_agent.params import OperatingSystem, SoftwareName

        from config import WEBDRIVER_PATH, HEADLESS

        options = webdriver.ChromeOptions()
        # options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        if HEADLESS:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
        )
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--log-level=3')
        logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        logger.setLevel(logging.NOTSET)  # or any variant from WARNING, ERROR, CRITICAL or NOTSET

        wd = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)
        wd.delete_all_cookies()
        if simulate_user:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            import threading
            import time

            ev = Event()

            def input_thread():
                actions = [
                    Keys.ARROW_DOWN, Keys.ARROW_UP, Keys.ARROW_LEFT, Keys.ARROW_RIGHT,
                    Keys.PAGE_UP, Keys.PAGE_DOWN,
                    Keys.PAGE_UP, Keys.PAGE_DOWN,
                    Keys.PAGE_UP, Keys.PAGE_DOWN,
                ]
                while not ev.is_set():
                    # create an ActionChains object
                    action = ActionChains(wd)
                    # perform a key-press action
                    wd.execute_script("document.body.focus();")
                    action.send_keys(actions[random.randint(0, len(actions) - 1)]).perform()
                    # wait for some time
                    time.sleep(random.randint(1, 60))

            # create a new thread for the input actions
            inputThread = threading.Thread(target=input_thread, daemon=True)
            return wd, inputThread, ev

        return wd
    except:
        return False


class BaseRequest:
    url = 'https://www.amazon.com/'
    method = 'get'
    jquery_inserted = False
    loc = None
    params_auto_paste = False
    result = None
    webdriver: WebDriver = None
    params: dict = None
    success = True

    @staticmethod
    def get_locations():
        return 'UM,NZ,AU,JP,IT,FI,SE,FR,CA,DE,ES,AT,KZ,MX,SG,GB,BE,BO,BR,EG,GR,IE,IL,PT,TR,KR,CN'.split(',')

    def __init__(self, webdriver: WebDriver, url=None, start_url=None):
        self.webdriver = webdriver
        if url:
            self.url = url
        self.webdriver.get(start_url or self.url)
        self.wait_for_loading()
        self.insert_jquery()
        if not self.captcha_solve():
            self.success = False
        else:
            self.wait_for_loading()
            self.change_country('UM')

    def wait(self, path, by=By.CSS_SELECTOR):
        try:
            WebDriverWait(self.webdriver, 10000).until(EC.presence_of_element_located((by, path)))
            return True
        except WebDriverException:
            return False

    def get_items(self, path, by=By.CSS_SELECTOR, wait=True, single=False):
        try:
            if wait:
                self.wait(path, by)
            return self.webdriver.find_element(by, path) if single else self.webdriver.find_elements(by, path)
        except WebDriverException:
            return None

    def captcha_check(self, just_check=False):
        self.wait_for_loading()
        self.insert_jquery()
        captcha = self.get_items(
            'div.a-box.a-alert.a-alert-info.a-spacing-base > div.a-box-inner > h4',
            wait=False,
            single=True,
        )
        if just_check:
            return captcha is None or captcha.text != 'Enter the characters you see below'

        if captcha and captcha.text == 'Enter the characters you see below':
            buttons = self.get_items('a[onclick="window.location.reload()"]', wait=False)
            for button in buttons:
                if button.text == 'Try different image':
                    button.click()
                    self.jquery_inserted = False
                    return self.captcha_check(True)
        return True

    def captcha_solve(self, retry=10):
        if not self.captcha_check():
            if not captchaAI:
                return False
            captcha = self.get_items('img[src]', wait=False, single=True)
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
            os.unlink(filepath)
            if not text:
                return False
            input_element = self.get_items('input[type="text"]', wait=False, single=True)
            for symbol in text:
                input_element.send_keys(symbol)
                sleep(random.randint(0, 2))
            input_element.send_keys(Keys.ENTER)
            sleep(1)
            self.wait_for_loading()
            self.insert_jquery(True)
            if not self.captcha_check():
                if retry:
                    return self.captcha_solve(retry - 1)
                return False
        return True

    def wait_for_loading(self):
        self.wait('html', By.TAG_NAME)

    def execute_script(self, script, jquery=True):
        if jquery:
            self.insert_jquery()
        self.webdriver.execute_script(script)

    def insert_jquery(self, anyway=False):
        if not self.jquery_inserted or anyway:
            self.execute_script("""
            var jq = document.createElement('script');
            jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
            document.getElementsByTagName('head')[0].appendChild(jq);
            """, False)
            sleep(2)
            self.jquery_inserted = True

    def change_country(self, loc):
        if self.loc == loc:
            return

        self.loc = loc
        self.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
            '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
        )
        self.execute_script(
            '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
            '{actionSource: "glow",'
            f'countryCode: "{loc}",'
            'deviceType: "web",'
            f'distinct: "{loc}",'
            'locationType: "COUNTRY",'
            'pageType: "Detail",'
            'storeContext: "hpc"}'
            ')'
        )
        self.execute_script(
            '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
            '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
        )
        sleep(1)
        self.webdriver.refresh()
        self.wait_for_loading()
        self.insert_jquery(True)

    def set_params(self, **kwargs):
        self.params = kwargs

    def params_to_str(self):
        return '?' + '&'.join('='.join(map(str, keyval)) for keyval in self.params.items())

    def send(self, except_processing=True):
        if not self.url:
            if except_processing:
                return False
            raise NotImplementedError('Please type the URL')
        try:
            self.insert_jquery()
            sleep(1)
            if self.params_auto_paste:
                ajax = f"$.{self.method}(\"{self.url}\", " \
                       + "{" + '",'.join([':"'.join(map(str, keyval)) for keyval in self.params.items()]) + "\"}" \
                       + ", null, 'text');"
            else:
                ajax = f"$.{self.method}(\"{self.url}\", null, null, 'text');"
            result = self.webdriver.execute_script("return " + ajax)
            sleep(1)
            self.result: str = result
            return True
        except JavascriptException as e:
            if except_processing:
                return False
            else:
                raise e

    def processing(self, json=True):
        if not self.result:
            return None
        if json:
            decoder = JSONDecoder()
            return list(map(lambda s: decoder.decode(s.strip()), filter(lambda x: x, self.result.strip().split('&&&'))))
        return self.result

