from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from seleniumbase.common.exceptions import NoSuchElementException

import captcha_solve
from database import write_keepa_html as write_keepa_html_to_db
from functions import WebDriver, chrome_init


def keepa_login(webdriver: WebDriver, login='keepa@brandlogic.ai', password='5kJuNc6EU1itFh0Y'):
    try:
        webdriver.get_element('#panelUserRegisterLogin', timeout=60*60).click()
    except NoSuchElementException:
        return False
    webdriver.sleep(.1)
    webdriver.type('#username', login)
    webdriver.sleep(.1)
    webdriver.type('#password', password)
    webdriver.sleep(.1)
    webdriver.submit('#password')
    return True


def keepa__price_history(webdriver: WebDriver):
    el = webdriver.get_element('#priceHistory', timeout=1)
    try:
        if not el or not el.get_attribute('innerHTML'):
            webdriver.click('#tabGraph')
            el = webdriver.get_element('#priceHistory', timeout=1)
            while not el or not el.get_attribute('innerHTML'):
                webdriver.sleep(.5)
                el = webdriver.get_element('#priceHistory')
    except StaleElementReferenceException:
        return keepa__price_history(webdriver)
    try:
        return el.get_attribute('innerHTML')
    except WebDriverException:
        el = webdriver.get_element('#priceHistory', timeout=1)
        return el.get_attribute('innerHTML')


def keepa__data(webdriver: WebDriver):
    el = webdriver.get_element('#MoreTab1', timeout=1)
    try:
        if not el or not el.get_attribute('innerHTML'):
            webdriver.click('#tabMore')
            el = webdriver.get_element('#MoreTab1', timeout=1)
            while not el or not el.get_attribute('innerHTML'):
                webdriver.sleep(.5)
                el = webdriver.get_element('#MoreTab1')
    except StaleElementReferenceException:
        return keepa__data(webdriver)
    return el.get_attribute('innerHTML')


def keepa__statistics(webdriver: WebDriver):
    el = webdriver.get_element('#statsTable', timeout=1)
    try:
        if not el or not el.get_attribute('innerHTML'):
            el = webdriver.get_element('#statistics')
            if not el or not el.is_displayed():
                webdriver.click('#tabGraph')
                el = webdriver.get_element('#priceHistory', timeout=1)
                while not el or not el.get_attribute('innerHTML'):
                    webdriver.sleep(.5)
                    el = webdriver.get_element('#priceHistory', timeout=1)
                el = webdriver.get_element('#statistics', timeout=1)
            el.hover()
            el.click()
            webdriver.sleep(.1)
            el = webdriver.get_element('#statsTable', timeout=1)
    except StaleElementReferenceException:
        return keepa__statistics(webdriver)
    return el.get_attribute('innerHTML')


def keepa__comparing(webdriver: WebDriver):
    el = webdriver.get_element('#compareChart', timeout=1)
    try:
        if not el or not el.is_displayed():
            webdriver.click('#tabGraph')
            el = webdriver.get_element('#priceHistory', timeout=1)
            while not el or not el.get_attribute('innerHTML'):
                webdriver.sleep(.5)
                el = webdriver.get_element('#priceHistory', timeout=1)
            el = webdriver.get_element('#compareChart', timeout=1)

        container = None
        while not container:
            el.click()
            webdriver.sleep(1)
            try:
                container = webdriver.get_element('#comparePricesOverlay', timeout=1)
            except NoSuchElementException:
                pass
    except StaleElementReferenceException:
        return keepa__comparing(webdriver)
    return container.get_attribute('innerHTML') if container else None


def collect_one_asin(webdriver, asin):
    webdriver.get(f'https://keepa.com/#!product/1-{asin}')
    webdriver.sleep(.5)
    write_keepa_html_to_db(
        asin,
        keepa__price_history(webdriver),
        keepa__statistics(webdriver),
        keepa__comparing(webdriver),
        keepa__data(webdriver),
    )


def keepa_start(asins=None, connection=None):
    if not asins and not connection:
        return
    if connection and connection.poll() and connection.recv() == False:
        return
    webdriver = None
    try:
        webdriver, capsolver_id = chrome_init(extension='./extension', get_ext_id='CapMonster Cloud')
        captcha_solve.init('06edbf7eec92d8e8e336fc09acc819eb', webdriver, capsolver_id)
        webdriver.sleep(1)
        if connection and connection.poll() and connection.recv() == False:
            return
        webdriver.get('https://keepa.com/')
        captcha_solve.solve(webdriver)
        if not keepa_login(webdriver):
            return

        if asins:
            for asin in asins:
                if connection and connection.poll() and connection.recv() == False:
                    return
                collect_one_asin(webdriver, asin)

        if connection:
            asin = connection.recv()
            while asin:
                collect_one_asin(webdriver, asin)
                asin = connection.recv()
    finally:
        if webdriver:
            webdriver.driver.close()


if __name__ == '__main__':
    keepa_start(['B08YKB6VMN'])
