import os
import sys
import urllib.parse
from time import sleep

from selenium.webdriver import Keys

from Requests import ProductsRequest
from initialization import initialize
from configuration import State, FOLDER_NAME


try:
    st = State('products_reviews_collect__state.dat')
    if not st['request']:
        category = input('Please, type the name of the products category to collect or exit to stop: ')
        while not category:
            category = input('Please, type the name of the products category to collect or exit to stop: ')
        if category.strip().lower() == 'exit':
            sys.exit(0)
        st['request'] = category
        st.write()
    elif '-y' not in sys.argv:
        answer = input('Do you want to continue collecting reviews? [Yes, No]: ')
        while answer.strip().lower() not in ('yes', 'y', 'n', 'no', 'exit'):
            answer = input('Do you want to continue collecting reviews? [Yes, No]: ')
        if answer in ('n', 'no'):
            category = input('Please, type the name of the products category to collect or exit to stop: ')
            while not category.strip():
                category = input('Please, type the name of the products category to collect or exit to stop: ')
            if category.strip().lower() == 'exit':
                sys.exit(0)
            st['request'] = category
            st.write()
        elif answer.strip().lower() == 'exit':
            sys.exit(0)

    selenium = initialize()
    selenium.get('https://www.amazon.com/')
    # type the request
    search_input = selenium.get_items('#twotabsearchtextbox,#nav-bb-search', single=True)
    search_input.send_keys(st['request'])
    sleep(5)
    search_input.send_keys(Keys.ENTER)
    sleep(5)
    max_page = 7
    # get data
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

    start_page = int(st['page'] or 1)
    start_page += int(st['page_ready'] or 0)

    page = start_page

    while page <= max_page:
        st['page'] = page
        st['page_ready'] = 0
        st['error_on_page'] = 0
        st.write()

        args.update(page=page)
        req = ProductsRequest(FOLDER_NAME, st, **args)
        if not req.send(selenium):
            print('ERROR!')
            st['error_on_page'] = 1
            st.write()
            break

        count_all_results = req.processing()
        if count_all_results > 0:
            max_page = count_all_results // 48 + 1 if count_all_results // 48 + 1 <= 7 else 7

        st['page_ready'] = 1
        st['last_asin'] = ''
        st.write()
        page += 1

    selenium.close()
except Exception as e:
    if '-S' in sys.argv:
        raise e
    elif '-s' in sys.argv:
        print('An error was occurred when collecting.')
        if '-l' in sys.argv:
            print(e)
    else:
        print('An error was occurred when collecting. Will try to reload script')
        if '-l' in sys.argv:
            print(e)

        os.execv(sys.executable, [sys.executable, sys.argv[0], '-y'])
    sys.exit(0)

print("Reviews collecting done! Closing script...")
