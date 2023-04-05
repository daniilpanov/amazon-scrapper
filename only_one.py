import logging
import sys

if len(sys.argv) > 1:
    import time

    time.sleep(10)
    current_reviews_page = int(sys.argv[1])
else:
    from config import state, FOLDER_NAME

    current_reviews_page = state()['reviews_page']
    if int(current_reviews_page) == 1:
        current_reviews_page = None


def run(page):
    from selenium.common import WebDriverException
    from selenium.common.exceptions import InvalidSessionIdException
    from urllib3.exceptions import MaxRetryError

    from models import ProductFull, AmazonRequest

    try:
        product_url = 'https://www.amazon.com/Sugarbear-Vitamin-Gummies-Chewable-Supplement/dp/B019ZZB3O2/ref=sr_1_8' \
                      '?crid=1A032JAVNFCZ4&keywords=hair+gummies&qid=1680186819&sprefix=hair+gummies%2Caps%2C146&sr=8' \
                      '-8'
        browser_inst = AmazonRequest(url=product_url)
        product = ProductFull(url=product_url, browser=browser_inst, page=page, dirname=FOLDER_NAME)
    except:
        print("Error when creating AmazonRequest")
        logging.warning("Error when creating AmazonRequest")
        sys.exit(1)

    try:
        product.reviews_collect()
        browser_inst.browser.quit()
    except WebDriverException:
        try:
            if browser_inst:
                browser_inst.browser.quit()
        finally:
            run(product.reviews.page)
    except (MaxRetryError, InvalidSessionIdException):
        import os
        os.execv(sys.executable, [sys.executable] + sys.argv)
        sys.exit(0)


if __name__ == '__main__':
    run(current_reviews_page)
