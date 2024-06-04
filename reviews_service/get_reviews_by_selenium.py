from functions import WebDriver

wd: WebDriver | None = None


def load_reviews(_id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    pass


def close():
    global wd
    if wd:
        wd.full_close()
        wd = None
