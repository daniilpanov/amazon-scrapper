import asyncio

import amazon_requests
import database as db
from helpers import parse_args, log, send_bot_msg, end_task, chunk_asins
from parser import parse_product, parse_aspects

domain = 'amazon.com'


async def collect(products_info_list):
    if not products_info_list:
        return -1
    sess = amazon_requests.Requests(domain)
    await sess.init()
    collected = set()

    for el in products_info_list:
        html = await sess.get_html(f'dp/{el}')

        if product_info_write(el, html):
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


async def start(asins, user, list_name, _id):
    res = False
    c = 15
    try:
        if asins:
            while not res and c > 0:
                res = await collect(asins)
                c -= 1
        else:
            log('No ASINs error!')
    except:
        pass
    else:
        if user:
            if res or c == 15:
                send_bot_msg(
                    user,
                    f'Product cards of "{list_name}" list collected!') \
                    if list_name else f'Products {asins} collected!'
            else:
                send_bot_msg(
                    user,
                    f'Product cards of "{list_name}" list are NOT collected.' \
                        if list_name else f'Products {asins} are NOT collected'
                )
    finally:
        if _id:
            end_task(_id)


if __name__ == '__main__':
    import sys

    params = parse_args(sys.argv)
    domain = params.get('domain', 'amazon.com')
    asyncio.run(start(chunk_asins(params.get('asins', 'B08H4YYXYM')), **params))
