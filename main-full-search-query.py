from queue import Queue
from threading import Thread

from collect_products import collect_asins, writer, collect_products_info, collect_reviews

if __name__ == '__main__':
    wq = Queue()
    piq = Queue()
    rq = Queue()
    # Threads
    writer_thr = Thread(target=writer, args=(wq,))
    products_info_thr = Thread(target=collect_products_info, args=(piq, wq))
    reviews_thr = Thread(target=collect_reviews, args=(rq,))
    # Start
    writer_thr.start()
    products_info_thr.start()
    reviews_thr.start()
    # Collect
    print(collect_asins(input('Enter the search request: '), wq, piq, rq, input('Enter the category: ')))
