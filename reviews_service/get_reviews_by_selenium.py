from functions import WebDriver, base_chrome_init

wd: WebDriver | None = None


def update_wd():
    global wd
    wd = base_chrome_init(False, goto='https://www.amazon.com')
    wd.change_loc()
    return wd


def load_reviews(_id, asin, keywords='', domain='amazon.com', index=0, current_format=True):
    if not wd:
        update_wd()
    try:
        try:
            wd.get(full_link or 'https://www.' + domain + '/dp/' + asin)
        except WebDriverException:
            update_wd().get(full_link or 'https://www.' + domain + '/dp/' + asin)
    except WebDriverException as e:
        print(e)
        return None
    return BeautifulSoup(wd.get_page_source(), features='lxml')


def close():
    global wd
    if wd:
        wd.full_close()
        wd = None
