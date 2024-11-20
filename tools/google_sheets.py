import re
import typing
import urllib.parse
from time import sleep

import gspread
from gspread import Cell
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame

url = 'https://docs.google.com/spreadsheets/d/1z35ivaQvXoE3Onac4tGJ4_SbHWvk8PJbmMwLcrWS0f8/edit?usp=sharing'
gc = gspread.service_account(filename='amascraper2-e256df953833.json')
sh = gc.open_by_url(url)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('amascraper2-e256df953833.json', scope)


def get_asins():
    data = sh.worksheet('Subcategories, Brands, Top ASINs').get('A2:H')
    asins = {}
    for row in data:
        if row[0] not in asins:
            asins[row[0]] = []

        for item in row[3:]:
            if item and "can't found any" not in item.lower() and "no grocery item" not in item.lower():
                item = urllib.parse.unquote(item)
                asin = re.findall(r'/dp/(.{10})', item)
                if asin:
                    asins[row[0]].append(asin)
    return asins


def write_reviews_data(dataframe: DataFrame, chunk_size=5000, skip_chunks_count=0):
    # Add a column with brand name
    asins = get_asins()
    brands = []

    for i, row in dataframe.iterrows():
        found = False
        for brand in asins:
            if row[1] in map(lambda x: x[0], asins[brand]):
                brands.append(brand)
                found = True
                break
        if not found:
            brands.append('')
    # Appending column
    dataframe.insert(0, 'Brand', brands)
    # Проверка, является ли количество строк в DataFrame больше 1 чанка
    if len(dataframe) > chunk_size:
        chunk_count = len(dataframe) // chunk_size + 1
        # Выбор нужного листа
        sheet = sh.worksheet('output2')
        offset = get_last_row(sheet)

        i = 0
        try:
            for i in range(skip_chunks_count, chunk_count):
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
        except Exception as e:
            print(e)
            print(f'LAST INDEX: {i}')
            sleep(60)
            write_reviews_data(dataframe, chunk_size, i)

    else:
        # Выбор нужного листа
        sheet = sh.worksheet('output2')

        # Загрузка DataFrame в Google Sheets
        set_with_dataframe(sheet, dataframe)


def get_last_row(sheet) -> int:
    last_row = sheet.row_count
    first_col_range__indicator: typing.List[Cell] = sheet.range('A1:A' + str(sheet.row_count))
    for col in reversed(first_col_range__indicator):
        if col.value.strip():
            break
        last_row -= 1
    return last_row
