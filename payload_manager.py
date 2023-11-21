from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pipe
from queue import Queue
from threading import Thread

import collect_products
import collect_reviews
import state

reviews_processes_pool = ProcessPoolExecutor(4)
products_processes_pool = ProcessPoolExecutor(1)
reader, writer = Pipe(False)
reviews_planned_asins = set()
products_planned_asins = set()


def init(prods_conn=None):
    q = Queue()
    thr = Thread(target=waiting, args=(q, prods_conn))
    thr.start()
    return q, thr


def waiting(q, prods_conn=None):
    res = q.get()
    while res:
        res = res
        extend(*res, prods_conn=prods_conn)
        res = q.get()


def extend(asins, callback, chat_id=None, callback_args=None, prods_conn=None):
    if not callback_args:
        callback_args = []
    for asin in asins:
        append(asin, callback, callback_args + [chat_id])
    add_products_info_collect(asins, prods_conn, chat_id)


def add_products_info_collect(asins, conn=None, chat_id=None):
    if not asins:
        return
    for_collecting = set({asin for asin in asins if state.get_asin(asin, 'products') != -1})
    asins = for_collecting

    feat = products_processes_pool.submit(collect_products.collect_products_info, asins, reader)

    def decrement(res):
        global products_planned_asins
        collected_asins = res.result()
        if not collected_asins:
            if conn:
                conn.send((chat_id, asins))
            return add_products_info_collect(asins, conn, chat_id)
        if collected_asins == -1:
            products_planned_asins -= asins
            if conn:
                conn.send((chat_id, asins))
            return
        not_collected_asins = asins - collected_asins
        products_planned_asins -= collected_asins
        if conn:
            conn.send((chat_id, collected_asins))
        if len(not_collected_asins) > 0:
            add_products_info_collect(not_collected_asins, conn, chat_id)

    feat.add_done_callback(decrement)

def append(asin, callback, callback_args):
    if state.get_asin(asin) == -1:
        return callback(*callback_args, asin)
    reviews_planned_asins.add(asin)
    feat = reviews_processes_pool.submit(collect_reviews.main, asin, reader)
    def decrement(_):
        reviews_planned_asins.remove(asin)
    def cbk(res):
        if res.result():
            callback(*callback_args, asin)
        else:
            append(asin, callback, callback_args)
    feat.add_done_callback(decrement)
    feat.add_done_callback(cbk)
    print(asin, 'accepted for reviews collecting')


def close_all():
    for _ in range(len(reviews_planned_asins)):
        writer.send(False)
    reviews_processes_pool.shutdown(True)
    products_processes_pool.shutdown(True)
    writer.close()
    reader.close()
