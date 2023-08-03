import re
import urllib.parse

import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame

url = 'https://docs.google.com/spreadsheets/d/1z35ivaQvXoE3Onac4tGJ4_SbHWvk8PJbmMwLcrWS0f8/edit?usp=sharing'
gc = gspread.service_account(filename='amascrap-9f8d561d63a1.json')
sh = gc.open_by_url(url)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('amascrap-9f8d561d63a1.json', scope)


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


def write_reviews_data(dataframe, chunk_size=5000):
    # Проверка, является ли количество строк в DataFrame больше максимального значения
    if len(dataframe) > 5000:
        chunk_count = len(dataframe) // chunk_size + 1

        for i in range(chunk_count):
            # Выбор нужного листа с добавлением порядкового номера
            sheet = sh.worksheet('output')

            # Получение подмножества данных для текущего блока
            start_index = i * chunk_size
            end_index = (i + 1) * chunk_size
            chunk_dataframe = dataframe[start_index:end_index]

            # Загрузка DataFrame в блок Google Sheets
            set_with_dataframe(sheet, chunk_dataframe, row=start_index + 1)

    else:
        # Выбор нужного листа
        sheet = sh.worksheet('output')

        # Загрузка DataFrame в Google Sheets
        set_with_dataframe(sheet, dataframe)
