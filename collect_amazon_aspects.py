from time import sleep

import requests

import database
from functions import base_chrome_init
from helpers import send_bot_msg, log, parse_args, end_task
from parser import parse_aspects
from state import chunk


def collect(products_aspects_list):
    wd = base_chrome_init(goto=f'https://www.{domain}')
    wd.change_loc()
    collected = set()

    for el in products_aspects_list:
        html = database.db('amazon_data')['raw_product_card_htmls'].find_one({'asin': el})
        if html:
            html = html['HTML_text']
            if products_aspects_write(el, html):
                collected.add(el)
                continue

        wd.get(f'https://{domain}/dp/{el}')
        html = wd.get_page_source()
        if html and products_aspects_write(el, html):
            collected.add(el)

    return set(products_aspects_list) == collected

def products_aspects_write(asin, html):
    aspects = parse_aspects(asin, html)
    return aspects and database.write_aspects(asin, aspects)


if __name__ == '__main__':
    import sys
    params_dict = parse_args(sys.argv)
    domain = params_dict.get('domain', 'amazon.com')
    asins = chunk(params_dict.get('asins', ''))
    try:
        res = True
        if asins:
            res = collect(asins)
        else:
            log('No ASINs error!')
        if 'user' in params_dict:
            if res:
                send_bot_msg(
                    params_dict['user'],
                    f'Aspects of list "{params_dict.get("list_name", params_dict["asins"])}" collected!')
            else:
                send_bot_msg(
                    params_dict['user'],
                    f'Aspects of list "{params_dict.get("list_name", params_dict["asins"])}"'
                    ' did NOT collected.'
                )
    finally:
        if 'id' in params_dict:
            end_task(params_dict['_id'])

