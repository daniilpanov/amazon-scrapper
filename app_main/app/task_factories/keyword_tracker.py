import math
from itertools import chain

from pymongo.synchronous.collection import Collection

from ..models.keyword_tracker import KeywordTrackerTask
from ..task_factories.abstract_factory import AbstractFactory


def get_data_iterator(col: Collection):
    return col.aggregate([
        {
            "$match": {
                "$expr": {
                    "$gte": [{ "$strLenCP": "$search_query" }, 3],
                },
            },
        },
        { "$sort": { "search_query": 1, "date": -1 } },
        {
            "$group": {
                "_id": "$search_query",
                "search_query_volume": { "$first": "$search_query_volume" },
                "asins": { "$addToSet": "$asin" },
            },
        },
        {
            "$project": {
                "_id": 0,
                "search_query": "$_id",
                "search_query_volume": 1,
                "asins": 1,
            },
        },
    ])


def priority_function(search_volume):
    if search_volume == 0:
        return 0

    log_vol = math.log10(search_volume)

    if log_vol >= 6:  # 1_000_000+
        return 15
    elif log_vol >= 5:  # 100_000 - 999_999
        return 11 + min(3, int((log_vol - 5) * 3))
    elif log_vol >= 4:  # 10_000 - 99_999
        return 8 + min(3, int((log_vol - 4) * 3))
    elif log_vol >= 3:  # 1_000 - 9_999
        return 5 + min(3, int((log_vol - 3) * 3))
    elif log_vol >= 2:  # 100 - 999
        return 2 + min(3, int((log_vol - 2) * 2))
    elif log_vol >= 1:  # 10 - 99
        return 1
    else:  # 1 - 9
        return 0


class KeywordTrackerFactory(AbstractFactory):
    def _post_init(self):
        self._primary_collections = (
            self._db["amazon_reports"]["search_query_brand"],
            self._db["amazon_reports_dev"]["search_query_brand"],
        )
        self._secondary_collections = (
            self._db["amazon_reports"]["search_query_asin"],
            self._db["amazon_reports_dev"]["search_query_asin"],
        )

    def publish_keyword_tracker(self):
        primary_items_set = {
            (query["search_query"], query["search_query_volume"], ())
            for query in chain(*(get_data_iterator(collection) for collection in self._primary_collections))
        }

        found_search_queries = {item[0] for item in primary_items_set}

        remaining_secondary_items_set = {
            (query["search_query"], query["search_query_volume"], tuple(query.get("asins")))
            for query in chain(*(get_data_iterator(collection) for collection in self._secondary_collections))
            if query["search_query"] not in found_search_queries
        }

        items_set = primary_items_set.union(remaining_secondary_items_set)

        for item in items_set:
            self._basic_publish("tasks", "kwt", KeywordTrackerTask(
                asins=list(item[2]),
                searchQuery=item[0],
                timeLimit=120000,
                pagesLimit=10,
            ), priority_function(item[1]))
