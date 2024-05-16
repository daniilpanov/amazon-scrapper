import os
import random
from time import sleep

import fake_useragent
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2Request

import database
import helpers


class Amazon404Exception(Exception):
    pass


class WebDriver:
    driver: webdriver.Chrome
    auto_captcha_check: bool
    auto_waiting: bool
    auto_jquery_insert: bool
    capsolver = None
    proxy_conf: dict[str, str]

    def __init__(self, driver, auto_captcha_check=True, auto_waiting=True, auto_jquery_insert=True):
        self.proxy_conf = {}
        self.driver = driver
        self.auto_captcha_check = auto_captcha_check
        self.auto_waiting = auto_waiting
        self.auto_jquery_insert = auto_jquery_insert

    def check_404(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, 'img[alt="Sorry! We couldn\'t find that page. Try searching or go to Amazon\'s home page."]')
        except NoSuchElementException:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, 'img[alt="Lo sentimos! No pudimos encontrar la página que buscabas. Trata de usar la barra de búsqueda o visita la página principal de Amazon Mexico."]')
            except NoSuchElementException:
                return False

    def get(self, url, cap_check=None, jquery=None, wait=None):
        self.driver.get(url)
        if self.check_404():
            raise Amazon404Exception
        if wait is None and self.auto_waiting or wait:
            sleep(.04)
            htmltag = self.wait_for_loading()
            if htmltag.text == 'Request was throttled. Please wait a moment and refresh the page':
                sleep(3)
                return self.get(url, cap_check, jquery, wait)
        if jquery is None:
            jquery = self.auto_jquery_insert
        if jquery:
            sleep(.06)
            self.activate_jquery()
        if cap_check is None:
            cap_check = self.auto_captcha_check
        if cap_check:
            for _ in range(3):
                if captcha_solve(self):
                    break
            if not captcha_solve(self):
                if self.auto_waiting:
                    self.wait_for_loading()
                return False
            if self.auto_waiting:
                self.wait_for_loading()
        return True

    def wait_for_loading(self, elem=None, timeout=30):
        if not elem:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "html"))
            )
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(elem if type(elem) is tuple else (By.CSS_SELECTOR, elem))
        )

    def click(self, elem, by=By.CSS_SELECTOR, timeout=None):
        if timeout:
            el = self.wait_for_loading((by, elem))
        else:
            el = self.find_element(by, elem)
        el.click()
        return el

    def focus(self, selector, by=By.CSS_SELECTOR):
        self.driver.execute_script('arguments[0].focus();', self.get_element(selector, by))

    def activate_jquery(self):
        return insert_jquery(self)

    def init_capsolver(self, api_key):
        _id = self.get_extension_id('CapMonster Cloud')
        self.driver.get('chrome-extension://{}/popup.html'.format(_id))
        self.sleep(1)
        self.type('#client-key-input', api_key)
        self.click('#client-key-save-btn')
        old_element = self.get_element('#settings-repeat-solve-attempts')
        for i in range(1, 11):
            self.sleep(0.2)
            old_element.send_keys(Keys.DOWN)
        old_element.send_keys(Keys.ENTER)
        self.sleep(1)

    def set_capsolver(self, capsolver):
        self.capsolver = capsolver

    def set_proxy_conf(self, proxy_conf):
        self.proxy_conf = proxy_conf

    async def recaptcha_solve_capsolver(self):
        try:
            iframe = self.get_element('iframe[title="reCAPTCHA"]')
            if not iframe:
                return True
            recaptcha = self.driver.find_element(By.CLASS_NAME, 'g-recaptcha')
            res = await self.capsolver.solve_captcha(RecaptchaV2Request(
                websiteUrl=self.driver.current_url,
                websiteKey=recaptcha.get_attribute('data-sitekey'),
                recaptchaDataSValue=recaptcha.get_attribute('data-s'),
                proxyType=self.proxy_conf.get('protocol', 'socks5'),
                proxyAddress=self.proxy_conf.get('addr'),
                proxyPort=self.proxy_conf.get('port', '80'),
                proxyLogin=self.proxy_conf.get('user'),
                proxyPassword=self.proxy_conf.get('pass'),
                userAgent=self.driver.execute_script("return navigator.userAgent;"),
                cookies=';'.join((el['name'] + '=' + el['value'] for el in self.get_cookies())),
            ))
            if not res or not res.get('gRecaptchaResponse'):
                return False
            res = res['gRecaptchaResponse']
            self.driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{res}';")
            return res
        except (NoSuchElementException, JavascriptException):

            return True

    def recaptcha_solve(self):
        try:
            iframe = self.get_element('iframe[title="reCAPTCHA"]')
            if not iframe:
                return True
            self.switch_to.frame(iframe)
            res = False
            while True:
                if 'style' in self.get_element('.recaptcha-checkbox-checkmark').get_attribute('outerHTML'):
                    res = True
                    break
                if self.get_element('.rc-anchor-error-msg').text:
                    break
                self.sleep(1)
            self.switch_to.default_content()
            return res
        except NoSuchElementException:
            return True

    def get_extension_id(self, name_contains):
        self.get('chrome://extensions')
        # find ID of the extension
        self.wait_for_loading()
        sleep(5)
        items = None
        try:
            # click to devmode
            root_el = self.find_element(By.TAG_NAME, 'extensions-manager').shadow_root
            items = root_el.find_element(By.CSS_SELECTOR, '#container extensions-item-list').shadow_root.find_elements(
                By.CSS_SELECTOR,
                '#container > #content-wrapper > .items-container:not(.review-panel-container) > extensions-item',
            )
        except Exception:
            pass
        _id = None
        if items:
            for item in items:
                if name_contains in item.shadow_root.find_element(
                        By.CSS_SELECTOR,
                        '#card > #main #content > div:first-child'
                ).text:
                    _id = item.get_property('id')
                    break
        return _id

    def change_loc(self, with_zip=90005, retry=True, domain='amazon.com'):
        sleep(.5)
        url = self.current_url
        self.activate_jquery()
        try:
            # переход к необходимой локации - US (UM)
            if with_zip:
                self.execute_script(
                    f'$.post("https://www.{domain}/portal-migration/hz/glow/address-change?actionSource=glow",'
                    '{actionSource: "glow",'
                    'deviceType: "web",'
                    'locationType: "LOCATION_INPUT",'
                    'pageType: "Gateway",'
                    'storeContext: "generic",'
                    f'zipCode: "{with_zip}"' + '}'
                                               ')'
                )
                self.execute_script(
                    f'$.get("https://www.{domain}/portal-migration/hz/glow/condo-refresh-html'
                    '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
                )
            else:
                self.execute_script(
                    f'$.post("https://www.{domain}/portal-migration/hz/glow/get-rendered-address-selections'
                    '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
                )
                self.execute_script(
                    f'$.post("https://www.{domain}/portal-migration/hz/glow/address-change?actionSource=glow",'
                    '{actionSource: "glow",'
                    'countryCode: "UM",'
                    'deviceType: "web",'
                    'distinct: "UM",'
                    'locationType: "COUNTRY",'
                    'pageType: "Detail",'
                    'storeContext: "hpc"}'
                    ')'
                )
                self.execute_script(
                    f'$.get("https://www.{domain}/portal-migration/hz/glow/condo-refresh-html'
                    '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
                )
            self.refresh()
            self.wait_for_loading()
            sleep(1)
            self.get(url)
            self.activate_jquery()
            cookies = self.driver.get_cookies()
            processed = {}
            for datum in cookies:
                processed[datum['name']] = datum['value']
            try:
                database.db('amazon_data')['__cookies'].insert_one(processed)
            except Exception:
                pass
            return True
        except JavascriptException as e:
            if retry and '$ is not defined' in e.msg:
                sleep(1)
                return self.change_loc(with_zip, False, domain)
            return False

    def get_page_source(self):
        return self.driver.page_source

    def add_js_link(self, js_link):
        script_to_add_js = """function injectJS(link) {
                  var body_tag=document.getElementsByTagName("body")[0];
                  var script_tag=document.createElement("script");
                  script_tag.src=link;
                  script_tag.type="text/javascript";
                  script_tag.crossorigin="anonymous";
                  script_tag.defer;
                  script_tag.onload=function() { null };
                  body_tag.appendChild(script_tag);
               }
               injectJS("%s");"""
        if js_link.count("\\'") != js_link.count("'") or (
                js_link.count('\\"') != js_link.count('"')
        ):
            if js_link.count("'") != js_link.count("\\'"):
                js_link = js_link.replace("'", "\\'")
            if js_link.count('"') != js_link.count('\\"'):
                js_link = js_link.replace('"', '\\"')
        try:
            self.execute_script(script_to_add_js % js_link)
            return True
        except JavascriptException:
            return False

    def sleep(self, sec):
        sleep(sec)

    def find_text(self, text, selector='.//*[text()[contains(.,"{}")]]', timeout=None):
        if timeout:
            return self.wait_for_loading((By.XPATH, selector.format(text)), timeout)
        return self.find_element(By.XPATH, selector.format(text))

    def click_link_text(self, text):
        el = self.find_text(text)
        if not el:
            return False
        el.click()
        return True

    def type(self, selector, text, by=By.CSS_SELECTOR, clear=False, textarea=False):
        el = self.driver.find_element(by, selector)
        if clear:
            if textarea:
                self.driver.execute_script('arguments[0].innerHTML = "";', el)
            else:
                self.driver.execute_script('arguments[0].value = "";', el)
        el.send_keys(text)

    def submit(self, selector, by=By.CSS_SELECTOR):
        self.find_element(by, selector).submit()

    def get_element(self, selector, by=By.CSS_SELECTOR):
        return self.driver.find_element(by, selector)

    def __getattr__(self, item):
        return self.driver.__getattribute__(item)

    def full_close(self):
        return chrome_close(self)


def captcha_check(wd):
    # wd.wait_for_loading()
    # url = wd.current_url
    try:
        # wd.get('https://amazon.com')
        wd.wait_for_loading()
        return wd.get_element('body > div > div[style*="width: 350px"]')
    except:
        return False
    # finally:
    # wd.sleep(3)
    # wd.get('https://amazon.com')
    # wd.get(url)
    # wd.wait_for_loading()
    # wd.activate_jquery()


def captcha_solve(wd: WebDriver):
    if not captcha_check(wd):
        return True

    wd.click('form a[onclick="window.location.reload()"]')
    wd.wait_for_loading()
    wd.sleep(.25)
    if not captcha_check(wd):
        return True

    captcha = wd.find_element(by=By.CSS_SELECTOR, value='img[src]')
    img_source = captcha.get_attribute('src')
    if not img_source:
        return False
    text = helpers.captcha_solve(img_source)
    if not text:
        return False
    wd.type('#captchacharacters', text)
    wd.submit('#captchacharacters')
    wd.sleep(1)
    wd.wait_for_loading()
    return not captcha_check(wd)


def insert_jquery(wd):
    try:
        wd.execute_script('jQuery("html")')
        return True
    except JavascriptException:
        return wd.add_js_link('https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js') and not sleep(3)


def user_emulate(wd, ev):
    try:
        while not ev.is_set():
            action = ActionChains(wd.driver)
            wd.focus('body')
            for i in range(random.randint(20, 50)):
                if ev.is_set():
                    break
                action.scroll_by_amount(0, random.randint(-4, 4) * 10).perform()
                sleep(0.2)
            if not random.randint(0, 5):
                if ev.is_set():
                    break
                action.send_keys(Keys.ARROW_LEFT).perform()
            sleep(random.randint(5, 15))
    except Exception as ex:
        print('User emulation is stopped due to an error:', ex)
        print('Reloading...')
        while not ev.is_set():
            sleep(1)
        return user_emulate(wd, ev)


class RetryException(Exception):
    pass


ua = fake_useragent.UserAgent(browsers=['chrome'], min_version=119.0, platforms=['pc'])


def base_chrome_init(
        headless=True, goto=None,
        extension=None, get_ext_id=False,
        logs=False, proxy=None, proxy_conf=None,
        user_profile=None, capsolver_api_key=None,
):
    opts = Options()
    wire_opts = {}
    if extension:
        opts.add_extension(os.path.abspath(extension))
    if not proxy:
        if proxy_conf and type(proxy_conf) is dict:
            proxy = proxy_conf.get('protocol', 'socks5') + '://'
            if 'user' in proxy_conf and 'pass' in proxy_conf:
                proxy += proxy_conf['user'] + ':' + proxy_conf['pass'] + '@'
            proxy += proxy_conf['addr'] + ':' + str(proxy_conf.get('port', 80))
    if proxy:
        # opts.add_argument(f'proxy-server_service={proxy}')
        wire_opts = {'proxy': {'http': proxy, 'https': proxy}}
    if headless:
        opts.add_argument('--headless')
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('start-maximized')
    opts.add_argument('disable-infobars')
    opts.add_argument('--log-level=3')
    switches = ['ignore-certificate-errors', 'enable-automation']
    if not logs:
        switches.append('enable-logging')
    opts.add_experimental_option('excludeSwitches', switches)
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('user-agent={}'.format(ua.random))
    wd = WebDriver(webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts, seleniumwire_options=wire_opts))
    wd.set_proxy_conf(proxy_conf or {})
    client_options = ClientOptions(api_key=capsolver_api_key)
    cap_monster_client = CapMonsterClient(options=client_options)
    wd.set_capsolver(cap_monster_client)
    ext_id = wd.get_extension_id(get_ext_id) if get_ext_id else None
    if goto:
        wd.get(goto, False)
        while not captcha_solve(wd):
            print('Result of solving captcha:', False)
        print('Result of solving captcha:', True)
    if get_ext_id:
        return wd, ext_id
    return wd


def chrome_close(wd: WebDriver):
    try:
        wd.driver.close()
    except:
        pass
