from bs4 import BeautifulSoup
from selenium.common import WebDriverException

from functions import base_chrome_init, WebDriver

wd: WebDriver | None = None


def update_wd():
    global wd
    wd = base_chrome_init(False, goto='https://www.amazon.com')
    wd.change_loc()
    return wd


def get_html_by_selenium(asin, full_link=None, domain='amazon.com'):
    if not wd:
        update_wd()
    try:
        try:
            wd.get(full_link or 'https://www.' + domain + '/dp/' + asin)
        except WebDriverException:
            update_wd().get(full_link or 'https://www.' + domain + '/dp/' + asin)
    except WebDriverException as e:
        print(e)
        return None
    return BeautifulSoup(wd.get_page_source(), features='lxml')


def close():
    if wd:
        wd.full_close()
