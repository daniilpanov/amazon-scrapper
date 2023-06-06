import os
import sys
from time import sleep

from pandas import read_csv
from selenium.common import WebDriverException

from Requests import ReviewsPoolRequests
from initialization import initialize
from configuration import State, FOLDER_NAME, MAX_RETRIES

selenium = None

try:
    if '-f' in sys.argv:
        for i in range(len(sys.argv) - 1):
            if '-f' == sys.argv[i]:
                FOLDER_NAME = sys.argv[i + 1]
    else:
        FOLDER_NAME = input(f'Please, type the data directory [{FOLDER_NAME}]: ') or FOLDER_NAME

    if not os.path.exists('./' + FOLDER_NAME):
        os.makedirs(FOLDER_NAME)

    if '-f' in sys.argv:
        file = 'products_list.csv'
    else:
        file = input('Please, type the source filename [products_list.csv]: ') or 'products_list.csv'
    # SETTINGS UP
    st = State('reviews_collect__state.dat', directory=FOLDER_NAME)

    # PREPARE
    selenium, thread = initialize(True, '-p' in sys.argv)
    selenium.get('https://www.amazon.com/')
    sleep(10)
    if '-C' in sys.argv:
        # if not selenium.captcha_solve():
        #     print('CAPTCHA can't be solved!')
        #     selenium.close()
        #     sys.exit(0)
        pass
    else:
        if not selenium.captcha_check(not ('-c' in sys.argv)):
            print('CAPTCHA!')
            selenium.close()
            sys.exit(0)
    # GET DATA
    if not os.path.exists(os.path.join(FOLDER_NAME, file)):
        products = input('Please, type the ASINs of products dividing by column: ').replace(' ', '').replace(',', '')
        if len(products) < 10:
            print('Error! There is no asins! This program will be closed')
            sys.exit(0)


        def grouper(iterable, n):
            string_part = [iter(iterable)] * n
            return zip(*string_part)


        products = [''.join(i) for i in grouper(products, 10)]
    else:
        # Loading dump
        products_df = read_csv(os.path.join(FOLDER_NAME, file))
        products = list(map(lambda x: x[1], products_df['asin'].items()))

    if '-v' in sys.argv:
        print(' ***** PRODUCTS ASINS LIST: ***** ')
        print('\n'.join(products))
        print(' ******************************** ')

    current_asin = st['current_asin']
    ready = not current_asin
    sleep(10)
    thread.start()

    # processing
    for product in products:
        if not ready:
            if current_asin != product:
                continue
            else:
                ready = True
                if int(st['asin_ready'] or 0) == 1:
                    st['asin_ready'] = 0
                    continue
        st['current_asin'] = product
        st['asin_ready'] = 0
        st.write()

        start_star = int(st['current_star'] or 1)
        if start_star > 5:
            start_star = 1
        for star in range(start_star, 6):
            if '-v' in sys.argv:
                print('Product:', product + '; stars:', star)
            incr = True
            try:
                req = ReviewsPoolRequests(product, star, selenium, FOLDER_NAME, st)
                req.processing(False)
            except KeyboardInterrupt:
                incr = False
                sys.exit(0)
            st['current_star'] = star + incr
            st['reviews_page'] = 1
            st.write()

        st['current_star'] = 1
        st['asin_ready'] = 1
        st.write()

    selenium.close()
    print('Reviews collecting done! Running uniqulizer and closing script...')
    from uniqulizer import uniqulize_by_df

    uniqulize_by_df(
        os.path.join(FOLDER_NAME, 'reviews_list.csv'),
        os.path.join(FOLDER_NAME, 'unique_reviews_list.csv'),
    )
except WebDriverException as e:
    if selenium:
        selenium.close()
    if '-S' in sys.argv:
        raise e
    elif '-s' in sys.argv:
        print('An error was occurred when collecting.')
        if '-v' in sys.argv:
            print(e)
    else:
        print('An error was occurred when collecting. Will try to reload script')

        args = [sys.executable, sys.argv[0]]
        if '-v' in sys.argv:
            print(e)
            args.append('-v')

        trying = 0
        for i in range(len(sys.argv) - 1):
            if sys.argv[i] == '--trying':
                trying = (int(sys.argv[i + 1]) + 1) if sys.argv[i + 1].isdigit() else 0
                break

        if trying <= int(MAX_RETRIES):
            sleep(10)
            args.append('--trying')
            args.append(str(trying))
            args.append('-f')
            args.append(FOLDER_NAME)
            os.execv(sys.executable, args)

    sys.exit(0)
except Exception as e:
    if selenium:
        selenium.close()

    raise e
