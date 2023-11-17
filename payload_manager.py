from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pipe

import main_collect_all

processes_pool = ProcessPoolExecutor(4)
reader, writer = Pipe(False)
planned_asins = set()


def extend(asins, callback, callback_args=None):
    if not callback_args:
        callback_args = []
    for asin in asins:
        append(asin, callback, callback_args)


def append(asin, callback, callback_args):
    feat = processes_pool.submit(main_collect_all.start([asin], callback=callback, callback_args=callback_args, conn_reader=reader))
    def decrement():
        planned_asins.remove(asin)
    feat.add_done_callback(decrement)
    print(asin, 'accepted')


def close_all():
    for _ in range(len(planned_asins)):
        writer.send(False)
    processes_pool.shutdown(True)
    writer.close()
    reader.close()
