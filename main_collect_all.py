import datetime
import re
from multiprocessing import Process, Pipe
from time import sleep

import pytz

from collect_keepa import keepa_start
from collect_products import collect_products_info
from collect_reviews import main


def start(asins, start_time=None, products_info_thr=None, keepa_thr=None, reader=None, writer=None, callback=None, callback_args=None, conf=None):
    if not callback_args:
        callback_args = []
    # PROCESSES
    # check config, then check need
    if (not conf or conf['products']) and (not products_info_thr or not reader or not writer):
        reader, writer = Pipe(False)
        products_info_thr = Process(target=collect_products_info, args=(list(asins), reader))
        products_info_thr.start()
    # check config, then check need
    if (not conf or conf['keepa']) and (not keepa_thr or not reader or not writer):
        if not reader or not writer:
            reader, writer = Pipe(False)
        keepa_thr = Process(target=keepa_start, args=(list(asins), reader))
        keepa_thr.start()

    # FAST EXIT FROM FUNCTION
    def close_all(stime):
        writer.send(False)
        writer.send(False)
        products_info_thr.join()
        keepa_thr.join()
        writer.close()
        reader.close()
        if not stime:
            stime = datetime.datetime.now()
        etime = datetime.datetime.now()
        dtime = etime - stime
        timedelta_text = (f'''{dtime.days} days, {dtime.seconds // 3600} hours, {dtime.seconds % 3600 // 60} minutes, '''
                          f'''{dtime.seconds % 60} seconds, {dtime.microseconds} microseconds''')
        print('The time of the collecting all data:', timedelta_text)
        callback(*callback_args, timedelta_text)
        return dtime

    # REVIEWS - in main process
    try:
        # Keep start time
        if not start_time:
            start_time = datetime.datetime.now()
        if not conf or conf.get('reviews', True):
            # process
            main(list(asins))
            # end time
            end_time = datetime.datetime.now()
            delta = end_time - start_time
            print(
                'The time of the reviews collecting:',
                delta.days, 'days,', delta.seconds // 3600, 'hours,',
                delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
                delta.microseconds, 'microseconds.'
            )
        return close_all(start_time)
    except KeyboardInterrupt:
        print('Script stopped')
        return close_all(start_time)
    except Exception as e:
        # raise e
        print('Something went wrong... reloading all script after 10 seconds')
        print('ERROR:', e)
        sleep(10)
        return start(asins, start_time, products_info_thr, keepa_thr, reader, writer, callback, callback_args, conf)


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('[A-Z0-9]{10}')
    asins = set()
    for line in text.strip().splitlines():
        found = pattern_find.findall(line)
        for item in found:
            asins.add(item)
    return list(asins)



# Mainloop
if __name__ == '__main__':
    # FILES PATHS
    datetime_now = datetime.datetime.now(pytz.UTC).strftime('%m-%d-%Y')
    print('TIMEDELTA:', start(['kjjkjkjjk']))

