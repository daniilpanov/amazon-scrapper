import datetime

from pymongo.errors import BulkWriteError, DuplicateKeyError
from ..abstract_handler import AbstractHandler


class KeywordTrackerHandler(AbstractHandler):
    @classmethod
    def get_handlers(cls):
        return {
            'result.success.kwt': {'handler': cls.handle_success},
            'result.error.kwt': {'handler': cls.handle_error},
        }

    def handle_success(self):
        sq = self._data['searchQuery']
        organic_count = self._data.get('countOrganic', 0)
        sponsored_count = self._data.get('countSponsored', 0)
        data = self._data['chunk']
        new_data = []

        for item in data:
            if not item: continue
            item['searchQuery'] = sq
            setdefaultmany(item, ('bought_count', 'score', 'price', 'itemPrice', 'oldPrice', 'subscriptionDiscount', 'subscriptionDiscountPercents'), float)
            setdefaultmany(item, ('bestSellerIn', 'image', 'title', 'asin'), str)
            if item.get('isSponsored'):
                sponsored_count += 1
                item['organic_rank'] = None
                item['sponsored_rank'] = sponsored_count
            else:
                organic_count += 1
                item['organic_rank'] = organic_count
                item['sponsored_rank'] = None
            del item['isSponsored']
            item['date'] = datetime.datetime.fromisoformat(item['date'])
            item['date_key'] = datetime.datetime.combine(item['date'].date(), datetime.time())
            new_data.append(item)

        if new_data:
            try:
                self._db['Keywords']['keyword_tracking_new'].insert_many(new_data, ordered=False)
            except (DuplicateKeyError, BulkWriteError):
                pass

    def handle_error(self, msg):
        self._logger.error(msg)


def setdefaultmany(obj, keys, func, default = None):
    for k in keys:
        obj[k] = func(obj[k]) if obj.get(k) else default


handler = KeywordTrackerHandler
