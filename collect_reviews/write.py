from threading import Thread
from queue import Queue
from pymongo.errors import BulkWriteError, DuplicateKeyError
from database import db

_writing_queue = Queue()
_writer_thr: Thread | None = None
reviews_collection = db('amazon_data')['customer_reviews']


def _writer(q: Queue):
    while True:
        reviews = q.get()
        if reviews is None:
            return
        revs = []
        if type(reviews) is list:
            revs = reviews
        else:
            for i, row in reviews.iterrows():
                revs.append({
                    'asin': row['asin'],
                    'product_url': row['product_url'],
                    'date': row['date'],
                    'country': row['country'],
                    'name': row['name'],
                    'title': row['title'],
                    'description': row['content'],
                    'rating': row['rating'],
                    'helpful': row['helpful'],
                    'options': row['options'],
                    'review_id': row['review_id'],
                    'scrap_datetime': row['scrap_datetime'],
                })
        if not revs:
            continue
        try:
            reviews_collection.insert_many(revs, ordered=False)
        except (BulkWriteError, DuplicateKeyError):
            continue


def start():
    global _writer_thr
    if _writer_thr:
        stop()
    _writer_thr = Thread(target=_writer, args=(_writing_queue,))
    _writer_thr.start()


def write(x):
    _writing_queue.put(x)


def stop():
    global _writer_thr
    if _writer_thr:
        _writing_queue.put(None)
        _writer_thr.join()
        _writer_thr = None
