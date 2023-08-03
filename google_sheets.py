import re
import urllib.parse

import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

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
        # Выбор нужного листа
        sheet = sh.worksheet('output')
        offset = get_last_row(sheet)

        for i in range(chunk_count):
            # Получение подмножества данных для текущего блока
            start_index = i * chunk_size
            end_index = (i + 1) * chunk_size
            chunk_dataframe = dataframe[start_index:end_index]

            # Загрузка DataFrame в блок Google Sheets
            set_with_dataframe(
                sheet, chunk_dataframe,
                row=offset + start_index + 1,
                include_column_header=i + offset == 0,
            )

    else:
        # Выбор нужного листа
        sheet = sh.worksheet('output')

        # Загрузка DataFrame в Google Sheets
        set_with_dataframe(sheet, dataframe)


def get_last_row(sheet):
    # Получаем общее количество строк на листе
    total_rows = sheet.row_count
    # Ищем последнюю заполненную строку внизу
    for i in range(total_rows, 1, -1):
        row_values = sheet.row_values(i)
        if any(row_values):
            return i
    return 0

