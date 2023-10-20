import os

from selenium.webdriver.common.by import By

from functions import chrome_init

webdriver = chrome_init(True, headless=False, extension=os.path.abspath('JSextension'), goto='chrome://extensions')
webdriver.sleep(3)
items = None
for i in range(2):
    try:
        webdriver.switch_to_tab(i)
        # click to devmode
        webdriver.sleep(1)
        root_el = webdriver.get_element('extensions-manager', timeout=1).shadow_root
        items = root_el.find_element(By.CSS_SELECTOR, '#container extensions-item-list').shadow_root.find_elements(
            By.CSS_SELECTOR,
            '#container > #content-wrapper > .items-container:not(.review-panel-container) > extensions-item',
        )
        break
    except:
        pass
if items:
    for item in items:
        _id = item.get_property('id')
        if 'Jungle Scout' in item.shadow_root.find_element(By.CSS_SELECTOR, '#card > #main #content > div:first-child')\
                .text:
            print(_id)
            break
webdriver.driver.quit()
