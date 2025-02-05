import asyncio
import os
import certifi
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import AsyncMongoClient

load_dotenv('.env') or load_dotenv('../.env')


async def get_all_asins():
    url = os.environ.get('MONGO_DB_HOST_SCHEMA', 'mongodb') + '://'
    username = None
    password = None
    if 'MONGO_DB_USER' in os.environ:
        username = os.environ['MONGO_DB_USER']
        url += username
        if 'MONGO_DB_PASS' in os.environ:
            password = os.environ['MONGO_DB_PASS']
            url += ':' + password
        url += '@'
    url += os.environ.get('MONGO_DB_HOST', 'localhost')
    db = AsyncMongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where())

    res = set(await db['amazon_reports']['catalog'].distinct('asin')).union(await db['amazon_reports_dev']['catalog'].distinct('asin'))

    await db.close()

    return res


async def main():
    asins = await get_all_asins()
    print('\n'.join(list(asins)))


asyncio.run(main())
