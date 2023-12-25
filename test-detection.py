import time

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from functions import WebDriver

opts = Options()
opts.add_argument('start-maximized')
opts.add_argument('disable-infobars')
opts.add_experimental_option('excludeSwitches', ['ignore-certificate-errors', 'enable-automation'])
opts.add_argument('--disable-blink-features=AutomationControlled')
opts.add_argument('--no-first-run')  # this might be specific to undetected_chromedriver.v2 only
opts.add_argument('--no-service-autorun')  # this might be specific to undetected_chromedriver.v2 only
opts.add_argument('--password-store=basic')  # this might be specific to undetected_chromedriver.v2 only
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
opts.add_argument('user-agent={}'.format(user_agent))
opts.page_load_strategy = 'normal'
driver = webdriver.Chrome(opts, Service(ChromeDriverManager.install()))

wd = WebDriver(driver)

wd.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  '''
})

wd.get('https://nowsecure.nl')
time.sleep(500)
wd.get('https://bot.sannysoft.com/')
time.sleep(500)
wd.close()
wd.quit()
