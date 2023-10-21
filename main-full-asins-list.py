import os.path
from queue import Queue
from threading import Thread

from collect_products import writer, collect_products_info, collect_reviews

if __name__ == '__main__':
    # Queues init
    wq = Queue()
    piq = Queue()
    rq = Queue()
    # Threads init
    writer_thr = Thread(target=writer, args=(wq,))
    products_info_thr = Thread(target=collect_products_info, args=(piq, wq))
    reviews_thr = Thread(target=collect_reviews, args=(rq,))
    # Threads start
    writer_thr.start()
    products_info_thr.start()
    reviews_thr.start()
    # Getting ASINs
    p = input('Please enter the filepath of products-list.txt [./products-list.txt]: ') or 'products-list.txt'
    while p.endswith('products-list.txt') and not os.path.exists(p) or not p.endswith('products-list.txt') and not os.path.exists(os.path.join(p)):
        p = input('Please enter the filepath of products-list.txt [./products-list.txt]: ') or 'products-list.txt'
    if not p.endswith('products-list.txt'):
        p = os.path.join(p, 'products-list.txt')
    with open(p) as f:
        asins = list(i.strip() for i in f)
    # Collecting
    rq.put(asins)
    for asin in asins:
        piq.put(asin)
    # Waiting
    piq.join()
    rq.join()
    # Finishing
    wq.put((-1, None))
    piq.put(None)
    rq.put(None)
