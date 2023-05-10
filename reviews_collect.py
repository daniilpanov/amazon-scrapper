import os
import sys

import pandas as pd

from Requests import ReviewsPoolRequests
from initialization import initialize
from configuration import State, FOLDER_NAME

try:
    # SETTINGS UP
    st = State('reviews_collect__state.dat')

    # PREPARE
    selenium = initialize()
    selenium.get('https://www.amazon.com/')
    # GET DATA
    # Loading dump
    with open(os.path.join(FOLDER_NAME, 'products_list.csv')) as datafile:
        products = [line.strip() for line in datafile]
    if '-v' in sys.argv:
        print(' ***** PRODUCTS ASINS LIST: ***** ')
        print('\n'.join(products))
        print(' ******************************** ')
    current_asin = st['current_asin']
    ready = not current_asin

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
                req.processing()
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
    from uniqulizer import uniqulize
    uniqulize(
        os.path.join(FOLDER_NAME, 'reviews_list.csv'),
        os.path.join(FOLDER_NAME, 'unique_reviews_list.csv'),
    )
except Exception as e:
    if '-S' in sys.argv:
        raise e
    elif '-s' in sys.argv:
        print('An error was occurred when collecting.')
        if '-v' in sys.argv:
            print(e)
    else:
        print('An error was occurred when collecting. Will try to reload script')
        if '-v' in sys.argv:
            print(e)

        os.execv(sys.executable, [sys.executable, sys.argv[0]])
    sys.exit(0)

