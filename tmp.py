import random
from time import sleep

from selenium.webdriver import Keys, ActionChains

from functions import chrome_init
# TODO: check jquery
wd = chrome_init(modern=True, headless=False, goto=None)
try:
    wd.get("https://seleniumbase.io/coffee/")
    wd.assert_title("Coffee Cart")
    wd.click('div[data-sb="Cappuccino"]')
    wd.click('div[data-sb="Flat-White"]')
    wd.click('div[data-sb="Cafe-Latte"]')
    wd.click('a[aria-label="Cart page"]')
    wd.assert_exact_text("Total: $53.00", "button.pay")
    action = ActionChains(wd.driver)
    wd.click("button.pay")
    wd.type("input#name", "Selenium Coffee")
    wd.type("input#email", "test@test.test")
    wd.focus('input#email')
    if not random.randint(0, 5):
        action.send_keys(Keys.PAGE_DOWN).perform()
    wd.sleep(10)
    wd.submit("input#email")
    wd.assert_text("Thanks for your purchase.", "#app .success")
except Exception as e:
    raise e
finally:
    try:
        wd.driver.close()
    except:
        pass


