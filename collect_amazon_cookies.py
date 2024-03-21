from queue import Queue
from threading import Thread
from time import sleep

from database import db
from functions import base_chrome_init


def collect(wqp):
    for i in range(1000):
        wd = base_chrome_init(goto='https://www.amazon.com')
        wd.change_loc()
        wqp.put(wd.driver.get_cookies())
        wd.full_close()


def iteration(wqp):
    if db('amazon_data')['__cookies'].count_documents({}) < 500:
        return collect(wqp)


def write_data(wqp):
    while True:
        data = wqp.get()
        if not data:
            return
        processed = {}
        for datum in data:
            processed[datum['name']] = datum['value']
        try:
            db('amazon_data')['__cookies'].insert_one(processed)
        except Exception:
            raise
            pass


def start():
    write_cookies_q = Queue()
    write_cookies_thr = Thread(target=write_data, args=(write_cookies_q,), daemon=True)
    write_cookies_thr.start()

    while True:
        iteration(write_cookies_q)
        sleep(30)


if __name__ == '__main__':
    start()
