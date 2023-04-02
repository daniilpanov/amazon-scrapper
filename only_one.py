from selenium.common import WebDriverException
from urllib3.exceptions import MaxRetryError

from models import ProductFull, AmazonRequest
import schedule
import time

browser_inst = None


def run():
    global browser_inst
    try:
        product = 'https://www.amazon.com/Sugarbear-Vitamin-Gummies-Chewable-Supplement/dp/B019ZZB3O2/ref=sr_1_8?crid=1A032JAVNFCZ4&keywords=hair+gummies&qid=1680186819&sprefix=hair+gummies%2Caps%2C146&sr=8-8'
        browser_inst = AmazonRequest(url=product)
        ProductFull(url=product, browser=browser_inst)
        browser_inst.browser.quit()
    except WebDriverException:
        try:
            if browser_inst:
                browser_inst.browser.quit()
        finally:
            run()
    except MaxRetryError:
        try:
            if browser_inst:
                browser_inst.browser.quit()
        finally:
            pass


if __name__ == '__main__':
    run()
    schedule.every().hour.do(run)
    while True:
        schedule.run_pending()
        time.sleep(5)
