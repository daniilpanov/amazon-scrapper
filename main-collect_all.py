import datetime
import re
from multiprocessing import Process, Pipe
from time import sleep

import pytz

from collect_keepa import keepa_start
from collect_products import collect_products_info
from collect_reviews import main


def start(
        asins_list_file, products_info_file, reviews_file, keepa_file, start_time=None,
        products_info_thr=None, keepa_thr=None, reader=None, writer=None,
):
    with open(asins_list_file) as f:
        asins = []
        p = re.compile(r'([A-Z0-9]{10})')
        for line in f.readlines():
            res = p.findall(line)
            if res:
                asins.append(res[0])
    # PROCESSES
    if not products_info_thr or not keepa_thr or not reader or not writer:
        reader, writer = Pipe(False)
        products_info_thr = Process(target=collect_products_info, args=(asins, products_info_file, reader))
        keepa_thr = Process(target=keepa_start, args=(asins, reader, keepa_file))
        products_info_thr.start()
        keepa_thr.start()

    try:
        # Keep start time
        if not start_time:
            start_time = datetime.datetime.now()
        main(asins, asins_list_file, reviews_file)
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        print(
            'The time of the collecting:',
            delta.days, 'days,', delta.seconds // 3600, 'hours,',
            delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
            delta.microseconds, 'microseconds.'
        )
        from uniqulizer import uniqulize_by_df
        uniqulize_by_df(reviews_file, reviews_file, 0)
        writer.send(False)
        writer.send(False)
        products_info_thr.join()
        keepa_thr.join()
        writer.close()
        reader.close()
        return delta
    except KeyboardInterrupt:
        print('Script stopped')
        writer.send(False)
        writer.send(False)
        products_info_thr.join()
        keepa_thr.join()
        writer.close()
        reader.close()
        return None
    except Exception as e:
        # raise e
        print('Something went wrong... reloading all script after 10 seconds')
        print('ERROR:', e)
        sleep(10)
        return start(
            asins_list_file, products_info_file, reviews_file, keepa_file, start_time,
            products_info_thr, keepa_thr, reader, writer,
        )


# Mainloop
if __name__ == '__main__':
    print('PROGRAM STARTED')
    # FILES PATHS
    datetime_now = datetime.datetime.now(pytz.UTC).strftime('%m-%d-%Y')
    print('TIMEDELTA:', start(
        f'p{datetime_now}.txt',
        f'out/pr{datetime_now}.csv',
        f'out/r{datetime_now}.csv',
        f'out/k{datetime_now}.csv',
    ))

