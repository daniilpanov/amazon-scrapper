import asyncio
import os
from bs4 import BeautifulSoup
from peewee import MySQLDatabase, Model, AutoField, ForeignKeyField, CharField

from amazon_requests import Requests
from helpers import log

import dotenv

dotenv.load_dotenv('.env')


domain = 'amazon.com'

conn = MySQLDatabase(
    os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT'),
)


def NotIncrementingAutoField():
    field = AutoField()
    field.auto_increment = False
    return field


class BaseModel(Model):
    class Meta:
        database = conn


class Department(BaseModel):
    class Meta:
        table_name = 'departments'

    id = AutoField()
    parent_id = ForeignKeyField('self', backref='departments', null=True)
    name = CharField(255)
    url = CharField(1000, unique=True)


class Product(BaseModel):
    class Meta:
        table_name = 'products'

    id = AutoField()
    department_id = ForeignKeyField('self', backref='products', null=True)
    name = CharField(255)
    url = CharField(1000, unique=True)


async def _test():
    r = Requests()
    await r.init()
    html = await r.get_html('https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_amazon-devices_0_1289283011_4')
    soup = BeautifulSoup(html, features='lxml')
    group = soup.find('div', {'role': 'group'})
    items = group.find_all('div', {'role': 'treeitem'}, recursive=False)
    data = []
    for item in items:
        a = item.find('a')
        data.append((a.text, a['href']))
    print(data)



if __name__ == '__main__':
    print(asyncio.run(_test()))
