from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from time import sleep

import settings
from database import db
from functions import base_chrome_init


def collect(wqp):
    while True:
        wd = base_chrome_init(goto='https://www.amazon.com', proxy=settings.PROXY)
        wd.change_loc()
        wqp.put(wd.driver.get_cookies())
        wd.full_close()
        sleep(1)


def write_data(wqp):
    while True:
        data = wqp.get()
        if not data:
            return
        processed = {}
        for datum in data:
            processed[datum['name']] = datum['value']
        try:
            print(processed['session-id'])
            db('amazon_data')['__cookies'].insert_one(processed)
        except Exception:
            pass


def start():
    write_cookies_q = Queue()
    write_cookies_thr = Thread(target=write_data, args=(write_cookies_q,), daemon=True)
    write_cookies_thr.start()
    with ThreadPoolExecutor(6) as pool:
        pool.map(collect, [write_cookies_q for _ in range(6)])


if __name__ == '__main__':
    start()
