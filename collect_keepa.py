import datetime
import os

import pytz
from pandas import DataFrame
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from seleniumbase.common.exceptions import NoSuchElementException

import captcha_solve
from database import write_keepa_html
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


def keepa_write(asin, keepa_ph, keepa_stats, keepa_comparing, keepa_data, filename='out/keepa-list.csv'):
    columns = 'asin,keepa_price_history,keepa_statistics,keepa_comparing,keepa_data,scrap_datetime'
    if not os.path.exists(filename + '--raw.csv'):
        f = open(filename + '--raw.csv', 'w', encoding='utf-8')
        f.write(columns + '\n')
        f.close()
    data = [asin, keepa_ph, keepa_stats, keepa_comparing, keepa_data]
    df = DataFrame([data + [datetime.datetime.now(pytz.UTC)]], columns=columns.split(','))
    write_keepa_html(*data)
    df.to_csv(filename + '--raw.csv', index=False, header=False, mode='a', encoding='utf-8')


def collect_one_asin(webdriver, asin, filename):
    webdriver.get(f'https://keepa.com/#!product/1-{asin}')
    webdriver.sleep(.5)
    keepa_write(
        asin,
        keepa__price_history(webdriver),
        keepa__statistics(webdriver),
        keepa__comparing(webdriver),
        keepa__data(webdriver),
        filename,
    )


def keepa_start(asins=None, connection=None, filename='out/keepa-list.csv'):
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
                collect_one_asin(webdriver, asin, filename)

        if connection:
            asin = connection.recv()
            while asin:
                collect_one_asin(webdriver, asin, filename)
                asin = connection.recv()
    finally:
        if webdriver:
            webdriver.driver.close()


if __name__ == '__main__':
    keepa_start(['B08YKB6VMN'])
