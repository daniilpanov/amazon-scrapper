from concurrent.futures import ThreadPoolExecutor

import peewee
from bs4 import BeautifulSoup
from selenium.common import WebDriverException

import settings
from db import Department
from functions import base_chrome_init

domain = 'amazon.com'


def start(deps=None):
    limit = 10
    while True:
        if not deps:
            deps = list(Department.select().where(Department.collected == False).limit(limit).order_by(~Department.id))
        if not deps:
            try:
                Department.get()
                print('Collected!')
                return
            except peewee.DoesNotExist:
                deps = iteration(link='bestsellers', _id=0, ret=True)
        with ThreadPoolExecutor(limit) as threader:
            for dep in deps:
                threader.submit(iteration, model=dep)


def iteration(*, link=None, _id=0, model=None, ret=False):
    if not any((model, _id + 1, link)):
        raise ValueError('One of arguments must be sent! [iteration]')
    if _id:
        model = Department.get_by_id(_id)
    if not link:
        link = model.url
        _id = model.id
    link = f'https://www.{domain}{link}'
    _id = int(_id)
    while True:
        wd = None
        try:
            wd = base_chrome_init(goto='https://www.amazon.com', proxy=settings.PROXY)
            wd.change_loc()
            wd.get(link)
            html = wd.get_page_source()
            wd.full_close()
        except WebDriverException:
            if wd:
                wd.full_close()
            continue
        soup = BeautifulSoup(html, features='lxml')
        group = soup.find('div', {'role': 'group'})
        if group:
            items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
            break
    model.collected = True
    model.save()
    models = []
    for item in items:
        a = item.find('a')
        if not a:
            print('Not found at:', link)
            return None
        title = a.text
        link = a['href']
        internal_id = link.split('/')[-2]
        models.append(Department(parent_id=_id, name=title, url=link, internal_id=internal_id))
    try:
        Department.bulk_create(models)
    except peewee.IntegrityError as e:
        print(e)
    if ret:
        return {i.internal_id: i for i in Department.select().where(Department.parent_id == _id)}


if __name__ == '__main__':
    start()
