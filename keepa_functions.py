from seleniumbase.common.exceptions import NoSuchElementException

from functions import WebDriver


def keepa_wait(webdriver: WebDriver):
    webdriver.wait_for_element('#keepa')


def keepa_space(func):
    def wrapper(webdriver: WebDriver, *args, wrap=True, **kwargs):
        if wrap:
            webdriver.switch_to_frame('#keepa')
            res = func(*((webdriver, ) + args), **kwargs)
            webdriver.switch_to_default_content()
            return res
        return func(*args, **kwargs)
    return wrapper


@keepa_space
def keepa_login(webdriver: WebDriver, login='keepa@brandlogic.ai', password='5kJuNc6EU1itFh0Y'):
    try:
        webdriver.get_element('#keepaBoxLogin', timeout=.1).click()
    except NoSuchElementException:
        return
    webdriver.sleep(.1)
    webdriver.type('#username', login)
    webdriver.sleep(.1)
    webdriver.type('#password', password)
    webdriver.sleep(.1)
    webdriver.submit('#password')


@keepa_space
def keepa__price_history(webdriver: WebDriver):
    el = webdriver.get_element('#priceHistory', timeout=1)
    if not el or not el.get_attribute('innerHTML'):
        webdriver.click('#tabGraph')
        while not el or not el.get_attribute('innerHTML'):
            webdriver.sleep(.5)
            el = webdriver.get_element('#priceHistory')
    return el.get_attribute('innerHTML')


@keepa_space
def keepa__data(webdriver: WebDriver):
    el = webdriver.get_element('#MoreTab1', timeout=1)
    if not el or not el.get_attribute('innerHTML'):
        webdriver.click('#tabMore')
        while not el or not el.get_attribute('innerHTML'):
            webdriver.sleep(.5)
            el = webdriver.get_element('#MoreTab1')
    return el.get_attribute('innerHTML')


@keepa_space
def keepa__statistics(webdriver: WebDriver):
    el = webdriver.get_element('#statsTable', timeout=1)
    if not el or not el.get_attribute('innerHTML'):
        el = webdriver.get_element('#statistics')
        if not el or not el.is_displayed():
            el = webdriver.get_element('#priceHistory', timeout=1)
            webdriver.click('#tabGraph')
            while not el or not el.get_attribute('innerHTML'):
                webdriver.sleep(.5)
            el = webdriver.get_element('#statistics', timeout=1)
        el.hover()
        el.click()
        webdriver.sleep(.1)
    return el.get_attribute('innerHTML')


@keepa_space
def keepa__comparing(webdriver: WebDriver):
    el = webdriver.get_element('#compareChart', timeout=1)
    if not el or not el.is_displayed():
        el = webdriver.get_element('#priceHistory', timeout=1)
        webdriver.click('#tabGraph')
        while not el or not el.get_attribute('innerHTML'):
            webdriver.sleep(.5)
        el = webdriver.get_element('#compareChart', timeout=1)
    el.click()
    webdriver.sleep(1)
    container = webdriver.get_element('#comparePricesOverlay')
    return container.get_attribute('innerHTML') if container else None

