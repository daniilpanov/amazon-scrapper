import re
import urllib.parse

import gspread

gc = gspread.service_account(filename='amascrap-9f8d561d63a1.json')
sh = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1z35ivaQvXoE3Onac4tGJ4_SbHWvk8PJbmMwLcrWS0f8/edit?usp=sharing'
)


def get_asins():
    data = sh.worksheet('Subcategories, Brands, Top ASINs').get('D2:H')

    count = 0
    asins = []
    for row in data:
        for item in row:
            if item.strip() and "can't found any" not in item.lower() and "no grocery item" not in item.lower():
                item = urllib.parse.unquote(item)
                count += 1
                asin = re.findall(r'/dp/(.{10})', item)
                if asin:
                    asins.append(asin[0])

    return asins


def write_reviews_data():
    # TODO: write data to Google Sheets from reviews_list.csv
    pass
