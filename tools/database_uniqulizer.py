import certifi
import pymongo
import pandas as pd

from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo.server_api import ServerApi

load_dotenv() or load_dotenv('.env') or load_dotenv('../.env')

from os import environ as env

if __name__ == '__main__' and input('Are you sure?').lower().strip() == 'yes':
    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
    with pymongo.MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'),
                         password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as client:
        collection = input('Enter the collection name: ')
        uniq_cols = input('Enter the unique columns, divided by ",": ').split(',')
        db_name, collection = collection.split('.')
        c = client[db_name][collection]
        data = list(c.find({}))
        df = pd.DataFrame(data)
        print('Data saved to local DataFrame')
        df = df.drop_duplicates(subset=uniq_cols)
        print('Duplicates dropped')
        if input('Continue?').lower().strip() == 'yes':
            c.delete_many({})
            print('Deleted old data')
            try:
                c.insert_many(list(df.T.to_dict().values()), ordered=False)
            except (DuplicateKeyError, BulkWriteError) as e:
                pass
            except Exception as e:
                print('An error occurred:', type(e), e)
            print('Inserted uniqulized data')
        else:
            print('Cancelled')
