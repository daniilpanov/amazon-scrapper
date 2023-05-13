import random
from time import sleep

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import logging


def initialize(simulate_user=False):
    from selenium import webdriver

    from random_user_agent.user_agent import UserAgent
    from random_user_agent.params import OperatingSystem, SoftwareName

    from configuration import WEBDRIVER_PATH, HEADLESS

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
    logger.setLevel(logging.CRITICAL)  # or any variant from WARNING, ERROR, CRITICAL or NOTSET

    cs = CustomSelenium(WEBDRIVER_PATH, options=options)
    if simulate_user:
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        import threading
        import time

        def input_thread():
            actions = [
                Keys.ARROW_DOWN, Keys.ARROW_UP, Keys.ARROW_LEFT, Keys.ARROW_RIGHT,
                Keys.PAGE_UP, Keys.PAGE_DOWN,
                Keys.PAGE_UP, Keys.PAGE_DOWN,
                Keys.PAGE_UP, Keys.PAGE_DOWN,
            ]
            while True:
                # create an ActionChains object
                action = ActionChains(cs)
                # perform a key-press action
                cs.execute_script("document.body.focus();")
                action.send_keys(actions[random.randint(0, len(actions) - 1)]).perform()
                # wait for some time
                time.sleep(random.randint(1, 60))

        # create a new thread for the input actions
        inputThread = threading.Thread(target=input_thread)
        return cs, inputThread

    return cs


class CustomSelenium(WebDriver):
    jquery_inserted = False

    def insert_jquery(self):
        if not self.jquery_inserted:
            self.execute_script("""
            var jq = document.createElement('script');
            jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
            document.getElementsByTagName('head')[0].appendChild(jq);
            """)
            sleep(1)
            self.jquery_inserted = True

    def insert_script(self, js_script: str):
        self.insert_jquery()
        self.execute_script("""
        $("<script>").html(" """ + js_script.replace('"', '\\"') + """ ").appendTo($("body"));
        """)

    def write_answer(self, js_code):
        self.execute_script("""
        $("#answer").text({});
        """.format(js_code))

    def get_answer(self):
        return self.get_items("answer", By.ID, single=True)

    def get_items(self, path, by=By.CSS_SELECTOR, wait=True, single=False):
        try:
            if wait:
                WebDriverWait(self, 10000).until(EC.presence_of_element_located((by, path)))
            return self.find_element(by, path) if single else self.find_elements(by, path)
        except NoSuchElementException | TimeoutException | WebDriverException:
            return None
