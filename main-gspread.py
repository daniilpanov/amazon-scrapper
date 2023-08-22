import sys
import os
from time import sleep

from google_sheets import get_asins, write_reviews_data
from collect_reviews import main

# Mainloop
if __name__ == '__main__':
    print('PROGRAM STARTED')
    try:
        asins = get_asins()
        start_time, end_time = main(asins)
        delta = end_time - start_time
        print(
            'The time of the collecting:',
            delta.days, 'days,', delta.seconds // 3600, 'hours,',
            delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
            delta.microseconds, 'microseconds.'
        )
        from uniqulizer import uniqulize_by_df
        uniqulize_by_df('reviews_list.csv', 'output_reviews_list.csv', 0)
        from pandas import read_csv
        p = 'output_reviews_list.csv'
        while not os.path.exists(p):
            p = input('Default file can not be found. Please type the path of the CSV file with collected reviews: ')
        write_reviews_data(read_csv(p, encoding='utf-8'))
    except KeyboardInterrupt:
        print('Script stopped')
    except:
        print('Something went wrong... reloading all script after 20 seconds')
        sleep(20)
        os.execv(sys.executable, [sys.executable] + sys.argv)
