import re
import sys
import os
from time import sleep

from collect_reviews import main

# Mainloop
if __name__ == '__main__':
    print('PROGRAM STARTED')
    if len(sys.argv) > 2:
        directory = sys.argv[-1]
    else:
        directory = input('Please type the directory: ') or '.'
    try:
        with open(os.path.join(directory, 'products.list')) as f:
            asins = []
            p = re.compile(r'([A-Z0-9]{10})')
            for line in f.readlines():
                res = p.findall(line)
                if res:
                    asins.append(res[0])
        start_time, end_time = main(asins, directory)
        delta = end_time - start_time
        print(
            'The time of the collecting:',
            delta.days, 'days,', delta.seconds // 3600, 'hours,',
            delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
            delta.microseconds, 'microseconds.'
        )
        from uniqulizer import uniqulize_by_df
        uniqulize_by_df(
            os.path.join(directory, 'reviews_list.csv'),
            os.path.join(directory, 'output_reviews_list.csv'),
            0
        )
    except KeyboardInterrupt:
        print('Script stopped')
    except Exception as e:
        print('Something went wrong... reloading all script after 20 seconds')
        sleep(20)
        os.execv(sys.executable, [sys.executable] + sys.argv + ([directory] if directory not in sys.argv else []))
