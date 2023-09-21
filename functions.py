import os
import random
from time import sleep

import requests
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium.common import WebDriverException, NoSuchElementException, JavascriptException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import BaseCase
from seleniumbase import config as sbc
from seleniumbase.fixtures import constants
from undetected_chromedriver import Chrome, ChromeOptions

sb_config = sbc


class WebDriver (BaseCase):
    def activate_jquery(self):
        return insert_jquery(self)


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


def captcha_check_modern(webdriver, just_check=False):
    webdriver.activate_jquery()
    try:
        captcha = webdriver.get_element('div.a-box.a-alert.a-alert-info.a-spacing-base > div.a-box-inner > h4')
        if just_check:
            return captcha.text == 'Enter the characters you see below'
        if captcha and captcha.text == 'Enter the characters you see below':
            buttons = webdriver.get_elements('a[onclick="window.location.reload()"]')
            for button in buttons:
                if button.text == 'Try different image':
                    button.click()
                    sleep(1)
                    return captcha_check_modern(webdriver, True)
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


def captcha_solve_modern(webdriver, retry=10):
    if captcha_check_modern(webdriver):
        if not captchaAI:
            sleep(15)
            return captcha_check_modern(webdriver, True)
        sleep(1)
        captcha = webdriver.get_element('img[src]')
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
        webdriver.type('#captchacharacters', text)
        webdriver.submit('#captchacharacters')
        webdriver.sleep(2)
        webdriver.activate_jquery()
        if captcha_check_modern(webdriver):
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
        webdriver.execute_script('jQuery("html")')
    except JavascriptException:
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
            action = ActionChains(webdriver.driver)
            webdriver.focus('body')
            for i in range(random.randint(20, 50)):
                action.scroll_by_amount(0, random.randint(-4, 4) * 10).perform()
                sleep(0.2)
            if not random.randint(0, 5):
                action.send_keys(Keys.ARROW_LEFT).perform()
            sleep(random.randint(5, 15))
    except Exception as ex:
        print('User emulation is stopped because of this error:', ex)
        print('Reloading...')
        sleep(20)
        return user_emulate(webdriver, ev)


class RetryException(Exception):
    pass


def modern_chrome_init(headless=True, user_path=None, user_settings=None):
    global sb_config
    sb_config._do_sb_post_mortem = False
    sb_config.proxy_driver = False
    sb_config.with_testing_base = False
    sb_config.browser = 'chrome'
    sb_config.is_context_manager = True
    sb_config.headless = False
    sb_config.headless2 = headless
    sb_config.headed = False
    sb_config.xvfb = False
    sb_config.start_page = None
    sb_config.locale_code = None
    sb_config.protocol = 'http'
    sb_config.servername = 'localhost'
    sb_config.port = '4444'
    sb_config.data = None
    sb_config.var1 = None
    sb_config.var2 = None
    sb_config.var3 = None
    sb_config.variables = {}
    sb_config.account = None
    sb_config.environment = 'test'
    sb_config.env = 'test'
    sb_config.user_agent = f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
    sb_config.incognito = False
    sb_config.guest_mode = False
    sb_config.dark_mode = False
    sb_config.devtools = not headless  # ???
    sb_config.mobile_emulator = False
    sb_config.device_metrics = None
    sb_config.extension_zip = None
    sb_config.extension_dir = None
    sb_config.database_env = "test"
    sb_config.log_path = constants.Logs.LATEST
    sb_config.archive_logs = False
    sb_config.disable_csp = False
    sb_config.disable_ws = False
    sb_config.enable_ws = True
    sb_config.enable_sync = None
    sb_config.use_auto_ext = False
    sb_config.undetectable = True
    sb_config.uc_cdp_events = None
    sb_config.uc_subprocess = True
    sb_config.no_sandbox = None
    sb_config.disable_gpu = None
    sb_config.disable_js = False
    sb_config._multithreaded = False
    sb_config.reuse_session = False
    sb_config.crumbs = False
    sb_config.final_debug = False
    sb_config.visual_baseline = False
    sb_config.window_size = None
    sb_config.maximize_option = True
    sb_config._disable_beforeunload = False
    sb_config.save_screenshot = False  # ??? (maybe helpful)
    sb_config.no_screenshot = False
    sb_config.binary_location = None
    sb_config.driver_version = None
    sb_config.page_load_strategy = None
    sb_config.timeout_multiplier = False
    sb_config.pytest_html_report = None
    sb_config.with_db_reporting = False
    sb_config.with_s3_logging = False
    sb_config.js_checking_on = False
    sb_config.recorder_mode = False
    sb_config.recorder_ext = False  # maybe error
    sb_config.record_sleep = False
    sb_config.rec_behave = False
    sb_config.rec_print = False
    sb_config.report_on = False
    sb_config.slow_mode = False
    sb_config.demo_mode = False
    sb_config._time_limit = None
    sb_config.demo_sleep = None
    sb_config.dashboard = False
    sb_config._dashboard_initialized = False
    sb_config.message_duration = None
    sb_config.block_images = False
    sb_config.do_not_track = False  # ???
    sb_config.use_wire = False
    sb_config.external_pdf = False
    sb_config.remote_debug = False
    sb_config.settings_file = user_settings or None
    sb_config.user_data_dir = user_path or None
    sb_config.chromium_arg = None
    sb_config.firefox_arg = None
    sb_config.firefox_pref = None
    sb_config.proxy_string = None
    sb_config.proxy_bypass_list = None
    sb_config.proxy_pac_url = None
    sb_config.multi_proxy = False
    sb_config.enable_3d_apis = False
    sb_config.swiftshader = False
    sb_config.ad_block_on = False  # ???
    sb_config.highlights = None
    sb_config.interval = None
    sb_config.cap_file = None
    sb_config.cap_string = None

    sb = WebDriver()
    sb.with_testing_base = sb_config.with_testing_base
    sb.browser = sb_config.browser
    sb.is_behave = False
    sb.is_pytest = False
    sb.is_nosetest = False
    sb.is_context_manager = sb_config.is_context_manager
    sb.headless = sb_config.headless
    sb.headless2 = sb_config.headless2
    sb.headed = sb_config.headed
    sb.xvfb = sb_config.xvfb
    sb.start_page = sb_config.start_page
    sb.locale_code = sb_config.locale_code
    sb.protocol = sb_config.protocol
    sb.servername = sb_config.servername
    sb.port = sb_config.port
    sb.data = sb_config.data
    sb.var1 = sb_config.var1
    sb.var2 = sb_config.var2
    sb.var3 = sb_config.var3
    sb.variables = sb_config.variables
    sb.account = sb_config.account
    sb.environment = sb_config.environment
    sb.env = sb_config.env
    sb.user_agent = sb_config.user_agent
    sb.incognito = sb_config.incognito
    sb.guest_mode = sb_config.guest_mode
    sb.dark_mode = sb_config.dark_mode
    sb.devtools = sb_config.devtools
    sb.binary_location = sb_config.binary_location
    sb.driver_version = sb_config.driver_version
    sb.mobile_emulator = sb_config.mobile_emulator
    sb.device_metrics = sb_config.device_metrics
    sb.extension_zip = sb_config.extension_zip
    sb.extension_dir = sb_config.extension_dir
    sb.database_env = sb_config.database_env
    sb.log_path = sb_config.log_path
    sb.archive_logs = sb_config.archive_logs
    sb.disable_csp = sb_config.disable_csp
    sb.disable_ws = sb_config.disable_ws
    sb.enable_ws = sb_config.enable_ws
    sb.enable_sync = sb_config.enable_sync
    sb.use_auto_ext = sb_config.use_auto_ext
    sb.undetectable = sb_config.undetectable
    sb.uc_cdp_events = sb_config.uc_cdp_events
    sb.uc_subprocess = sb_config.uc_subprocess
    sb.no_sandbox = sb_config.no_sandbox
    sb.disable_gpu = sb_config.disable_gpu
    sb.disable_js = sb_config.disable_js
    sb._multithreaded = sb_config._multithreaded
    sb._reuse_session = sb_config.reuse_session
    sb._crumbs = sb_config.crumbs
    sb._final_debug = sb_config.final_debug
    sb.visual_baseline = sb_config.visual_baseline
    sb.window_size = sb_config.window_size
    sb.maximize_option = sb_config.maximize_option
    sb._disable_beforeunload = sb_config._disable_beforeunload
    sb.save_screenshot_after_test = sb_config.save_screenshot
    sb.no_screenshot_after_test = sb_config.no_screenshot
    sb.page_load_strategy = sb_config.page_load_strategy
    sb.timeout_multiplier = sb_config.timeout_multiplier
    sb.pytest_html_report = sb_config.pytest_html_report
    sb.with_db_reporting = sb_config.with_db_reporting
    sb.with_s3_logging = sb_config.with_s3_logging
    sb.js_checking_on = sb_config.js_checking_on
    sb.recorder_mode = sb_config.recorder_mode
    sb.recorder_ext = sb_config.recorder_ext
    sb.record_sleep = sb_config.record_sleep
    sb.rec_behave = sb_config.rec_behave
    sb.rec_print = sb_config.rec_print
    sb.report_on = sb_config.report_on
    sb.slow_mode = sb_config.slow_mode
    sb.demo_mode = sb_config.demo_mode
    sb.time_limit = sb_config._time_limit
    sb.demo_sleep = sb_config.demo_sleep
    sb.dashboard = sb_config.dashboard
    sb._dash_initialized = sb_config._dashboard_initialized
    sb.message_duration = sb_config.message_duration
    sb.block_images = sb_config.block_images
    sb.do_not_track = sb_config.do_not_track
    sb.use_wire = sb_config.use_wire
    sb.external_pdf = sb_config.external_pdf
    sb.remote_debug = sb_config.remote_debug
    sb.settings_file = sb_config.settings_file
    sb.user_data_dir = sb_config.user_data_dir
    sb.chromium_arg = sb_config.chromium_arg
    sb.firefox_arg = sb_config.firefox_arg
    sb.firefox_pref = sb_config.firefox_pref
    sb.proxy_string = sb_config.proxy_string
    sb.proxy_bypass_list = sb_config.proxy_bypass_list
    sb.proxy_pac_url = sb_config.proxy_pac_url
    sb.multi_proxy = sb_config.multi_proxy
    sb.enable_3d_apis = sb_config.enable_3d_apis
    sb.swiftshader = sb_config.swiftshader
    sb.ad_block_on = sb_config.ad_block_on
    sb.highlights = sb_config.highlights
    sb.interval = sb_config.interval
    sb.cap_file = sb_config.cap_file
    sb.cap_string = sb_config.cap_string
    sb._has_failure = False  # This may change
    if hasattr(sb_config, "headless_active"):
        sb.headless_active = sb_config.headless_active
    else:
        sb.headless_active = False
    sb.setUp()

    return sb


def chrome_init(modern=False, headless=True, goto='https://www.amazon.com/product-reviews/B08JPS4554'):
    if modern:
        webdriver = modern_chrome_init(headless=headless)
        if goto:
            webdriver.get(goto)
            captcha_solve_modern(webdriver)
        return webdriver
    else:
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
        if goto:
            webdriver.get(goto)
            wait_for_loading(webdriver)
            captcha_solve(webdriver)
        return webdriver
