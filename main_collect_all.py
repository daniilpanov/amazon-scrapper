import datetime
import re
from multiprocessing import Process, Pipe
from time import sleep

import pytz
from numpy import datetime_data

from collect_keepa import keepa_start
from collect_products import collect_products_info
from collect_reviews import main


def start(asins, callback=None, callback_args=None, conf=None, conn_reader=None):
    if not conf:
        conf = {'keepa': False}
    if not callback_args:
        callback_args = []
    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        return

    # PROCESSES
    # check config, then check need
    reader = writer = products_info_thr = keepa_thr = None
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
    def close_all(cbk=None):
        if writer:
            try:
                for _ in range(conf.get('keepa', True) + conf.get('products', True) + conf.get('reviews', True)):
                    writer.send(False)
                writer.close()
                reader.close()
            except OSError:
                pass
        if products_info_thr:
            products_info_thr.join()
        if keepa_thr:
            keepa_thr.join()
        elif cbk:
            cbk(*callback_args, asins=asins)
        return None
    if conn_reader and conn_reader.poll() and conn_reader.recv() == False:
        return close_all(callback)
    # REVIEWS - in main process
    try:
        if not conf or conf.get('reviews', True):
            # process
            main(list(asins), conn_reader=reader)
        return close_all(callback)
    except KeyboardInterrupt:
        print('Script stopped')
        return close_all(callback)
    except Exception as e:
        # raise e
        print('Something went wrong... reloading all script after 10 seconds')
        print('ERROR:', e)
        close_all()
        sleep(10)
        return start(asins, callback, callback_args, conf)


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
    print('TIMEDELTA:', start(['B0BGV79FHT']))

