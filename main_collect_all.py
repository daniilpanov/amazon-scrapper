import datetime
import re
from multiprocessing import Process, Pipe
from time import sleep

import pytz

from collect_keepa import keepa_start
from collect_products import collect_products_info
from collect_reviews import main


def start(asins, start_time=None, callback=None, callback_args=None, conf=None, conn_reader=None):
    if not conf:
        conf = {'keepa': False}
    if not callback_args:
        callback_args = []
    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        return
    # Keep start time
    if not start_time:
        start_time = datetime.datetime.now()
    # PROCESSES
    # check config, then check need
    reader = writer = None
    if not conf or conf.get('products', True):
        reader, writer = Pipe(False)
        products_info_thr = Process(target=collect_products_info, args=(list(asins), reader))
        products_info_thr.start()
    # check config, then check need
    if not conf or conf.get('keepa', True):
        if not reader or not writer:
            reader, writer = Pipe(False)
        keepa_thr = Process(target=keepa_start, args=(list(asins), reader))
        keepa_thr.start()

    # FAST EXIT FROM FUNCTION
    def close_all(stime=None, cbk=None):
        if writer:
            for _ in range(conf.get('keepa', True) + conf.get('products', True) + conf.get('reviews', True)):
                writer.send(False)
            writer.close()
            reader.close()
        if products_info_thr:
            products_info_thr.join()
        if keepa_thr:
            keepa_thr.join()
        if stime:
            etime = datetime.datetime.now()
            dtime = etime - stime
            timedelta_text = (f'''{dtime.days} days, {dtime.seconds // 3600} hours, {dtime.seconds % 3600 // 60} minutes, '''
                              f'''{dtime.seconds % 60} seconds, {dtime.microseconds} microseconds''')
            print('The time of the collecting all data:', timedelta_text)
            if cbk:
                cbk(*callback_args, timedelta_text)
            return dtime
        elif cbk:
            cbk(*callback_args)
        return None
    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        return close_all(start_time, callback)
    # REVIEWS - in main process
    try:
        if not conf or conf.get('reviews', True):
            # process
            main(list(asins), conn_reader=reader)
            # end time
            end_time = datetime.datetime.now()
            delta = end_time - start_time
            print(
                'The time of the reviews collecting:',
                delta.days, 'days,', delta.seconds // 3600, 'hours,',
                delta.seconds % 3600 // 60, 'minutes,', delta.seconds % 60, 'seconds,',
                delta.microseconds, 'microseconds.'
            )
        return close_all(start_time, callback)
    except KeyboardInterrupt:
        print('Script stopped')
        return close_all(start_time, callback)
    except Exception as e:
        # raise e
        print('Something went wrong... reloading all script after 10 seconds')
        print('ERROR:', e)
        sleep(10)
        close_all()
        return start(asins, start_time, callback, callback_args, conf)


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('B0[A-Z0-9]{8}')
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
    print('TIMEDELTA:', start(['B0BGV79FHT']))

