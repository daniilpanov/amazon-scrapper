from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pipe
from queue import Queue
from threading import Thread

import collect_reviews
import state

processes_pool = ProcessPoolExecutor(4)
reader, writer = Pipe(False)
planned_asins = set()


def init():
    q = Queue()
    thr = Thread(target=waiting, args=(q,))
    thr.start()
    return q, thr


def waiting(q):
    res = q.get()
    while res:
        extend(*res)
        res = q.get()


def extend(asins, callback, callback_args=None):
    if not callback_args:
        callback_args = []
    for asin in asins:
        append(asin, callback, callback_args)


def append(asin, callback, callback_args):
    if state.get_asin(asin) == -1:
        return callback(*callback_args, (asin,))
    feat = processes_pool.submit(collect_reviews.main, [asin], conn_reader=reader)
    def decrement(_):
        planned_asins.remove(asin)
    def cbk(_):
        callback(*callback_args, (asin,))
    feat.add_done_callback(decrement)
    feat.add_done_callback(cbk)
    print(asin, 'accepted')


def close_all():
    for _ in range(len(planned_asins)):
        writer.send(False)
    processes_pool.shutdown(True)
    writer.close()
    reader.close()
