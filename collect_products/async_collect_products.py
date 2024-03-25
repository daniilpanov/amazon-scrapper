import asyncio

import amazon_requests
import database as db
import tasks
from helpers import parse_args, log, send_bot_msg, end_task, chunk_asins
from parser import parse_product, parse_aspects

domain = 'amazon.com'


async def collect(products_info_list, collect_aspects=True):
    if not products_info_list:
        return -1
    sess = amazon_requests.Requests(domain)
    await sess.init()
    collected = set()

    for el in products_info_list:
        html = await sess.get_html(f'dp/{el}')

        if product_info_write(el, html, collect_aspects):
            collected.add(el)

    await sess.request.close()
    return collected


def product_info_write(asin, html, write_aspects=True):
    try:
        data = parse_product(asin, html, domain=domain)
        db.write_product_parsed(*data)
        if write_aspects:
            aspects = parse_aspects(asin, html)
            db.write_aspects(asin, aspects)
        return True
    except Exception as e:
        log(f'ERROR when parsing asin: {asin} -- ', e)
        return False


async def start(_id, asins, collect_aspects=True):
    print('prods:', _id, asins, collect_aspects)
    res = False
    c = 15
    try:
        if asins:
            while not res and c > 0:
                res = await collect(asins, collect_aspects)
                c -= 1
        else:
            log('No ASINs error!')
    except:
        pass
    finally:
        task = tasks.get_task(_id)
        task.progress = 100
        task.success = bool(res)
        task.result = res
