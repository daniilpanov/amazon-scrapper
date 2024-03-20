import asyncio
import logging

import amazon_requests
import database as db
from helpers import parse_args, log, send_bot_msg, end_task
from parser import parse_product
from state import chunk

logger = logging.getLogger('products')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f'products.log', 'a')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

domain = 'amazon.com'


async def collect(products_info_list):
    # products_info_list = list(asin for asin in products_info_list if state.get_asin(asin, 'products') != -1)
    if not products_info_list:
        return -1
    sess = amazon_requests.Requests(domain)
    await sess.init()
    collected = set()

    for el in products_info_list:
        # if state.get_asin(el, 'products') == -1:
        #     collected.add(el)
        #     continue
        html = await sess.get_html(f'dp/{el}')

        if product_info_write(el, html):
            collected.add(el)

    await sess.request.close()
    return collected


def product_info_write(asin, html):
    try:
        data = parse_product(asin, html, domain=domain)
        db.write_product_parsed(*data)
        return True
    except Exception as e:
        log(f'ERROR when parsing asin: {asin} -- ', e)
        return False


async def start(asins):
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
        if 'user' in params_dict:
            if res or c == 15:
                send_bot_msg(
                    params_dict['user'],
                    f'Product cards of "{params_dict["list_name"]}" list collected!') \
                    if 'list_name' in params_dict else f'Products {params_dict["asins"]} collected!'
            else:
                send_bot_msg(
                    params_dict['user'],
                    f'Product cards of "{params_dict["list_name"]}" list are NOT collected.' \
                        if 'list_name' in params_dict else f'Products {params_dict["asins"]} are NOT collected'
                )
    finally:
        if 'id' in params_dict:
            end_task(params_dict['_id'])


if __name__ == '__main__':
    import sys

    params_dict = parse_args(sys.argv)
    domain = params_dict.get('domain', 'amazon.com')
    asyncio.run(start(chunk(params_dict.get('asins', 'B08H4YYXYM'))))
