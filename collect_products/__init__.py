from helpers import get_all_asins_from_text
from .async_collect_products import *
import tasks
import amazon_requests


def get_runnable(ev, _id, asins, collect_aspects=True):
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    task = tasks.get_task(_id)
    task.all = len(set(asins))
    task.result = {'asins': []}
    if not asins:
        return []
    sess = amazon_requests.Requests(domain)
    collected = set()

    return [get_item(el, sess, task, collected, collect_aspects) for el in asins]
