import logging
import sys

from MustBeReloadedException import MustBeReloadedException

if len(sys.argv) > 1:
    import time

    time.sleep(10)
    current_reviews_page = int(sys.argv[1])
    print("Done")
    logging.warning("Done")
else:
    from config import state, FOLDER_NAME

    current_reviews_page = state()['reviews_page']


def run(product_url, page):
    from selenium.common import WebDriverException
    from selenium.common.exceptions import InvalidSessionIdException
    from urllib3.exceptions import MaxRetryError

    from models import ProductFull, AmazonRequest

    browser_inst = product = None
    try:
        browser_inst = AmazonRequest(url=product_url)
        product = ProductFull(
            url=product_url,
            browser=browser_inst,
            page=page,
            dirname=FOLDER_NAME,
        )
    except MustBeReloadedException:
        import os
        print("Critical error. Reloading script...")
        logging.warning("Critical error. Reloading script...")
        if browser_inst and browser_inst.browser:
            browser_inst.browser.quit()
        if product and product.reviews:
            if len(sys.argv) > 1:
                sys.argv[1] = product.reviews.page
            else:
                sys.argv.append(product.reviews.page)
        os.execv(sys.executable, [sys.executable] + sys.argv)
        sys.exit(0)
    except Exception:
        print("Error when creating AmazonRequest")
        logging.warning("Error when creating AmazonRequest")
        if browser_inst and browser_inst.browser:
            browser_inst.browser.quit()
        sys.exit(1)

    try:
        product.reviews_collect()
        browser_inst.browser.quit()
    except (WebDriverException, MaxRetryError, InvalidSessionIdException, MustBeReloadedException):
        import os
        print("Critical error. Reloading script...")
        logging.warning("Critical error. Reloading script...")
        if browser_inst and browser_inst.browser:
            browser_inst.browser.quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)
        sys.exit(0)


if __name__ == '__main__':
    run(input("Please, input product's url: "), current_reviews_page)
