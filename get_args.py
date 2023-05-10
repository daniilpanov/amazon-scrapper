import urllib
from time import sleep

from configuration import State


def get_args(selenium, write=True, use_cached=False):
    if use_cached:
        st = State('reviews-scrapper-args.dat')
        if st.data:
            return st.data
    # GET DATA
    # get `qid` param: click to any pagination link
    pagination_button = selenium.get_items('a.s-pagination-item.s-pagination-button', wait=False, single=True)
    if pagination_button:
        selenium.execute_script('arguments[0].scrollIntoView();', pagination_button)
        sleep(2)
        pagination_button.click()
        sleep(5)
    base_url = selenium.current_url
    params_str = base_url.split('?')[1]
    args = dict(list(tuple(map(lambda x: urllib.parse.quote(urllib.parse.unquote(x)),
                               map(lambda x: x.replace('+', ' '), item.split('='))))
                     for item in params_str.split('&')))

    if write:
        st = State('reviews-scrapper-args.dat')
        st.set_data(args)
        st.write()
    return args
