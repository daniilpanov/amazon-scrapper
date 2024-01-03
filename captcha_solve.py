
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


def init(api_key: str, driver: BaseCase, _id):
    driver.driver.get('chrome-extension://{}/popup.html'.format(_id))
    driver.sleep(1)
    driver.send_keys('//*[@placeholder]', api_key, By.XPATH)
    driver.click('//*[@width="20"]', By.XPATH)
    old_element = driver.get_element('//input[@autocomplete="off"]', By.XPATH)
    for i in range(1, 11):
        old_element.send_keys(Keys.DOWN)
        driver.sleep(.2)
    old_element.send_keys(Keys.ENTER)
    driver.sleep(1)
    return driver


def solve(driver: BaseCase):
    try:
        driver.get_element('iframe[title="reCAPTCHA"]', timeout=1)
    except NoSuchElementException:
        return True
    driver.switch_to_frame('iframe[title="reCAPTCHA"]')
    res = False
    while True:
        try:
            if 'style' in driver.get_element('.recaptcha-checkbox-checkmark', timeout=1).get_attribute('outerHTML'):
                res = True
                break
            if driver.get_element('.rc-anchor-error-msg', timeout=1).text:
                break
            driver.sleep(1)
        except NoSuchElementException:
            res = True
            break
    driver.switch_to_default_content()
    return res
