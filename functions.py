import os
import random
import time
from time import sleep

import colorama
import requests
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium import webdriver
from selenium.common import JavascriptException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import config as sbc, BaseCase
from seleniumbase.fixtures import constants
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sb_config = sbc

try:
    import tensorflow
    from captcha_solver.solve_captcha_with_model import CaptchaSolver

    captchaAI = True
except ImportError as e:
    print(colorama.Fore.RED, e, colorama.Fore.RESET)
    CaptchaSolver = None
    captchaAI = False


class WebDriver:
    driver: webdriver.Chrome

    def __init__(self, driver):
        self.driver = driver

    def wait_for_loading(self, elem=None):
        if not elem:
            return WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "html"))
            )
        return WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(elem if type(elem) is tuple else (By.CSS_SELECTOR, elem))
        )

    def click(self, elem, by=By.CSS_SELECTOR, timeout=None):
        if timeout:
            el = self.wait_for_loading((by, elem))
        else:
            el = self.find_element(by, elem)
        el.click()
        return el

    def activate_jquery(self):
        return insert_jquery(self)

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
        except Exception as e:
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

    def change_loc(self, retry=True):
        sleep(.5)
        url = self.current_url
        self.activate_jquery()
        try:
            # переход к необходимой локации - US (UM)
            self.execute_script(
                '$.post("https://www.amazon.com/portal-migration/hz/glow/get-rendered-address-selections'
                '?deviceType=desktop&pageType=Detail&storeContext=hpc&actionSource=desktop-modal")'
            )
            self.execute_script(
                '$.post("https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow",'
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
                '$.get("https://www.amazon.com/portal-migration/hz/glow/condo-refresh-html'
                '?triggerFeature=AddressList&deviceType=desktop&pageType=Detail&storeContext=hpc&locker=%7B%7D")'
            )
            self.refresh()
            self.wait_for_loading()
            sleep(1)
            self.get(url)
            self.activate_jquery()
            self.wait_for_loading()
        except JavascriptException as e:
            if retry and '$ is not defined' in e.msg:
                sleep(1)
                self.change_loc(False)
                self.wait_for_loading()

    def get_page_source(self):
        return self.driver.page_source

    def change_loc_like_user(self):
        # nav-global-location-popover-link
        # GLUXCountryValue
        # li[aria-labelledby^="GLUXCountryList"] -> only with data-value='{\"stringVal\":\"UM\"}'
        # GLUXConfirmClose
        self.click('a#nav-global-location-popover-link', timeout=5)
        self.click('#GLUXCountryValue', timeout=5)
        try:
            self.click("li[aria-labelledby^='GLUXCountryList'][data-value='{\"stringVal\":\"UM\"}']", timeout=2)
        except:
            self.click('#GLUXCountryValue', timeout=1)
            self.execute_script("document.querySelector(\"li[aria-labelledby^='GLUXCountryList'] a[data-value='{"
                                "\\\"stringVal\\\":\\\"UM\\\"}']\").click();")
        self.click('#GLUXConfirmClose', timeout=4)
        self.refresh()
        self.wait_for_loading()

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
        self.execute_script(script_to_add_js % js_link)

    def sleep(self, sec):
        sleep(sec)

    def find_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        element = None
        is_present = False
        full_text = None
        text = str(text)
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        for x in range(int(timeout * 10)):
            full_text = None
            try:
                element = self.find_element(by, selector)
                is_present = True
                if element.tag_name.lower() in ["input", "textarea"]:
                    if element.is_displayed() and text in element.get_property("value"):
                        return element
                    else:
                        if element.is_displayed():
                            full_text = element.get_property("value").strip()
                        element = None
                        raise Exception
                else:
                    if element.is_displayed() and text in element.text:
                        return element
                    else:
                        if element.is_displayed():
                            full_text = element.text.strip()
                        element = None
                        raise Exception
            except Exception:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        plural = "s"
        if timeout == 1:
            plural = ""
        if not element:
            if not is_present:
                # The element does not exist in the HTML
                message = "Element {%s} was not present after %s second%s!" % (
                    selector,
                    timeout,
                    plural,
                )
            # The element exists in the HTML, but the text is not visible
            elif not full_text or len(str(full_text.replace("\n", ""))) > 320:
                message = (
                        "Expected text substring {%s} for {%s} was not visible "
                        "after %s second%s!" % (text, selector, timeout, plural)
                )
            else:
                full_text = full_text.replace("\n", "\\n ")
                message = (
                        "Expected text substring {%s} for {%s} was not visible "
                        "after %s second%s!\n (Actual string found was {%s})"
                        % (text, selector, timeout, plural, full_text)
                )
            print(message)
            return None
        else:
            return element

    def click_link_text(self, text):
        el = self.find_text(text)
        if not el:
            return False
        el.click()
        return True

    def type(self, selector, text, by=By.CSS_SELECTOR):
        self.find_element(by, selector).send_keys(text)

    def submit(self, selector, by=By.CSS_SELECTOR):
        self.find_element(by, selector).submit()

    def get_element(self, selector, by=By.CSS_SELECTOR):
        return self.driver.find_element(by, selector)

    def __getattr__(self, item):
        print(item)
        return self.driver.__getattribute__(item)


def captcha_check(wd):
    wd.wait_for_loading()
    url = wd.current_url
    try:
        wd.get('https://amazon.com')
        wd.wait_for_loading()
        return (wd.find_text('Enter the characters you see below', timeout=.5)
                and wd.find_text('Type the characters you see in this image:', timeout=.5))
    except:
        return False
    finally:
        wd.sleep(3)
        wd.get('https://amazon.com')
        wd.get(url)
        wd.wait_for_loading()
        wd.activate_jquery()


def captcha_solve(wd: WebDriver):
    if not captcha_check(wd):
        return True

    wd.click_link_text('Try different image')
    wd.sleep(.25)
    if not captcha_check(wd):
        return True

    captcha = wd.find_element('img[src]')
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
    wd.type('#captchacharacters', text)
    wd.submit('#captchacharacters')
    wd.sleep(1)
    wd.wait_for_loading()
    return not captcha_check(wd)


def insert_jquery(wd):
    try:
        wd.execute_script('jQuery("html")')
    except JavascriptException:
        wd.add_js_link('https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js')
        wd.sleep(3)


def user_emulate(wd, ev):
    try:
        while not ev.is_set():
            action = ActionChains(wd.driver)
            wd.focus('body')
            for i in range(random.randint(20, 50)):
                action.scroll_by_amount(0, random.randint(-4, 4) * 10).perform()
                sleep(0.2)
            if not random.randint(0, 5):
                action.send_keys(Keys.ARROW_LEFT).perform()
            sleep(random.randint(5, 15))
    except Exception as ex:
        print('User emulation is stopped due to an error:', ex)
        print('Reloading...')
        sleep(20)
        return user_emulate(wd, ev)


class RetryException(Exception):
    pass


def modern_chrome_init(headless=True, user_path=None, user_settings=None, extension=None, tor=True):
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
    sb_config.extension_dir = extension
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
    sb_config.proxy_string = 'socks5://104.154.150.173:9050' if tor else None
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

    sb = WebDriver(BaseCase())
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

    sb.get('https://amazon.com')

    return sb


def chrome_init(headless=True, goto=None, extension=None, get_ext_id=False, tor=False):
    wd = modern_chrome_init(headless=headless, extension=extension, tor=tor)
    ext_id = wd.get_extension_id(get_ext_id) if get_ext_id else None
    if goto:
        wd.get(goto)
        print('Result of solving captcha:', captcha_solve(wd))
    if get_ext_id:
        return wd, ext_id
    return wd


def base_chrome_init(headless=True, goto=None, extension=None, get_ext_id=False, tor=False):
    opts = Options()
    if extension:
        opts.add_extension(os.path.abspath(extension))
    if tor:
        opts.add_argument('proxy-server=socks5://104.154.150.173:9050')
    if headless:
        opts.add_argument('--headless')
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
    opts.add_argument('start-maximized')
    opts.add_argument('disable-infobars')
    opts.add_experimental_option('excludeSwitches', ['ignore-certificate-errors'])
    opts.add_argument('user-agent={}'.format(
        UserAgent(software_names=(SoftwareName.CHROME.value,),
                  operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value),
                  limit=120).get_random_user_agent(),
    ))
    wd = WebDriver(webdriver.Chrome(opts, ChromeService(ChromeDriverManager().install())))
    ext_id = wd.get_extension_id(get_ext_id) if get_ext_id else None
    if goto:
        wd.get(goto)
        print('Result of solving captcha:', captcha_solve(wd))
    if get_ext_id:
        return wd, ext_id
    return wd


def chrome_close(wd: WebDriver):
    try:
        wd.driver.close()
        return True
    except:
        return False
