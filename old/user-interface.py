import os.path


#
from config import FOLDER_NAME


def search_url(query):
    return f"https://www.amazon.com/s?k={query.strip().replace(' ', '+')}"


max_pages_count = int(input('Please, type quantity of products\' pages: ') or 999999999999)
search = input('Please, type the search (you can divide different queries using symbol ";"): ')
SEARCH_CATEGORIES = {item: search_url(item) for item in search.split(';')}




