import seleniumbase as sel

w = sel.SB()
wd = w.__enter__()
try:
    wd.open("https://seleniumbase.io/coffee/")
    wd.assert_title("Coffee Cart")
    print('ok')
    wd.click('div[data-sb="Cappuccino"]')
    wd.click('div[data-sb="Flat-White"]')
    wd.click('div[data-sb="Cafe-Latte"]')
    wd.click('a[aria-label="Cart page"]')
    wd.assert_exact_text("Total: $53.00", "button.pay")
    wd.click("button.pay")
    wd.type("input#name", "Selenium Coffee")
    wd.type("input#email", "test@test.test")
    wd.click("button#submit-payment")
    wd.assert_text("Thanks for your purchase.", "#app .success")
except Exception as e:
    w.__exit__(type(e), e, e.__traceback__)
    raise e

