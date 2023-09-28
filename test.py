import os

from functions import chrome_init

wd = chrome_init(modern=True, goto='chrome://extensions', headless=False,
                 extension=os.path.abspath('./keepa-extension'))

