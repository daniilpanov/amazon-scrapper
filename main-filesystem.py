import re
import sys
import os
from time import sleep

from collect_reviews import main

# Mainloop
if __name__ == '__main__':
    print('PROGRAM STARTED')
    if len(sys.argv) > 1 and (os.path.exists(sys.argv[-2]) or os.path.exists(os.path.abspath(sys.argv[-2]))):
        filename = sys.argv[-2]
    else:
        filename = input('Please enter the filename[products-list.txt]: ') or 'products-list.txt'
    if len(sys.argv) > 2 and (os.path.exists(sys.argv[-1]) or os.path.exists(os.path.abspath(sys.argv[-1]))):
        new_filename = sys.argv[-1]
    else:
        new_filename = input('Please enter the result filename[reviews-list.csv]: ') or 'reviews-list.csv'
    try:
        with open(filename) as f:
            asins = []
            p = re.compile(r'([A-Z0-9]{10})')
            for line in f.readlines():
                res = p.findall(line)
                if res:
                    asins.append(res[0])
        start_time, end_time = main(asins, filename, new_filename)
        delta = end_time - start_time
        print(
            'The time of the collecting:',
            delta.days, 'days,', delta.seconds // 3600, 'hours,',
            delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
            delta.microseconds, 'microseconds.'
        )
        from uniqulizer import uniqulize_by_df
        uniqulize_by_df(new_filename, new_filename, 0)
    except KeyboardInterrupt:
        print('Script stopped')
    except Exception as e:
        print(e)
        print('Something went wrong... reloading all script after 30 seconds')
        sleep(10)
        os.execv(sys.executable, [sys.executable] + sys.argv + ([filename] if filename not in sys.argv else []) + ([new_filename] if new_filename not in sys.argv else []))
