from time import sleep

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
    wd.click("button.pay")
    wd.type("input#name", "Selenium Coffee")
    wd.type("input#email", "test@test.test")
    wd.submit("input#email")
    # wd.click("button#submit-payment")
    wd.assert_text("Thanks for your purchase.", "#app .success")
except Exception as e:
    raise e
finally:
    try:
        wd._BaseCase__close_all_drivers()
    except:
        pass

