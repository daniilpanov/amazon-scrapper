import os

from functions import chrome_init

wd = chrome_init(modern=True, goto='chrome://extensions', headless=False,
                 extension=f'{os.path.abspath("JSextension")},{os.path.abspath("./keepa-extension")}')
wd.sleep(100)
wd.driver.quit()
